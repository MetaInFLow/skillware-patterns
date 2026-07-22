from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


SAMPLE = Path(__file__).resolve().parents[1]
DEMO_PATH = SAMPLE / "scripts/run_demo.py"
FILTER_IDS = ("normalize", "redact", "classify", "prioritize", "draft")


class PipesAndFiltersDemoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not DEMO_PATH.is_file():
            return
        spec = importlib.util.spec_from_file_location("pipes_filters_demo", DEMO_PATH)
        cls.demo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.demo)

    def require_demo(self):
        self.assertTrue(DEMO_PATH.is_file(), "Pipes and Filters demo is not implemented")
        return self.demo

    def load_json(self, relative_path):
        return json.loads((SAMPLE / relative_path).read_text(encoding="utf-8"))

    def test_ticket_passes_through_declared_filters(self):
        demo = self.require_demo()

        result = demo.run_pipeline(
            {"text": "URGENT email a@example.com: cannot login"}
        )

        self.assertEqual(result, self.load_json("expected/urgent-access-result.json"))
        self.assertEqual(result["trace"], list(FILTER_IDS))
        self.assertNotIn("a@example.com", result["record"]["text"])
        self.assertEqual(result["record"]["priority"], "high")

    def test_pipeline_is_deterministic_and_does_not_mutate_source(self):
        demo = self.require_demo()
        request = {"text": "  URGENT\taccount   locked for me@example.com  "}
        original = deepcopy(request)

        first = demo.run_pipeline(request)
        second = demo.run_pipeline(request)

        self.assertEqual(request, original)
        self.assertEqual(first, second)
        self.assertIsNot(first["record"], second["record"])

    def test_injected_filters_are_addressed_exactly_once_in_runner_order(self):
        demo = self.require_demo()
        calls = []

        def replacement(filter_id):
            def transform(record):
                calls.append(filter_id)
                if filter_id == "classify":
                    record["category"] = "general"
                if filter_id == "draft":
                    record["draft"] = "Replacement draft."
                return record

            return demo.Filter(filter_id, f"injected:{filter_id}", transform)

        filters = [replacement(filter_id) for filter_id in reversed(FILTER_IDS)]
        result = demo.run_pipeline({"text": "hello"}, filters=filters)

        self.assertEqual(calls, list(FILTER_IDS))
        self.assertEqual(result["trace"], list(FILTER_IDS))
        self.assertEqual(result["record"]["draft"], "Replacement draft.")

    def test_one_filter_is_replaceable_without_changing_pipeline_topology(self):
        demo = self.require_demo()
        calls = []

        def classify_replacement(record):
            calls.append(record["text"])
            record["category"] = "billing"
            return record

        filters = [
            demo.Filter(
                item.filter_id,
                item.skill_path,
                classify_replacement if item.filter_id == "classify" else item.transform,
            )
            for item in demo.DEFAULT_FILTERS
        ]

        result = demo.run_pipeline({"text": "cannot login"}, filters=filters)

        self.assertEqual(calls, ["cannot login"])
        self.assertEqual(result["record"]["category"], "billing")
        self.assertEqual(result["trace"], list(FILTER_IDS))

    def test_pipe_passes_fresh_copies_and_detaches_the_sink_result(self):
        demo = self.require_demo()
        received = []

        def transform(filter_id):
            def run(record):
                received.append(record)
                if filter_id == "classify":
                    record["category"] = "general"
                if filter_id == "draft":
                    record["draft"] = "Done."
                return record

            return run

        filters = [
            demo.Filter(filter_id, f"injected:{filter_id}", transform(filter_id))
            for filter_id in FILTER_IDS
        ]
        result = demo.run_pipeline({"text": "hello"}, filters=filters)

        self.assertEqual(len({id(record) for record in received}), len(FILTER_IDS))
        received[-1]["text"] = "mutated after return"
        self.assertEqual(result["record"]["text"], "hello")

    def test_filter_exception_stops_pipeline_with_stage_attribution(self):
        demo = self.require_demo()
        calls = []

        def transform(filter_id):
            def run(record):
                calls.append(filter_id)
                if filter_id == "classify":
                    raise RuntimeError("classifier unavailable")
                return record

            return run

        filters = [
            demo.Filter(filter_id, f"injected:{filter_id}", transform(filter_id))
            for filter_id in FILTER_IDS
        ]

        with self.assertRaisesRegex(
            demo.PipelineStageError,
            "^stage 'classify' failed: RuntimeError: classifier unavailable$",
        ) as caught:
            demo.run_pipeline({"text": "hello"}, filters=filters)

        self.assertEqual(caught.exception.stage, "classify")
        self.assertEqual(calls, ["normalize", "redact", "classify"])

    def test_invalid_filter_output_stops_before_the_next_filter(self):
        demo = self.require_demo()
        calls = []

        def transform(filter_id):
            def run(record):
                calls.append(filter_id)
                if filter_id == "redact":
                    return {**record, "priority": 7}
                return record

            return run

        filters = [
            demo.Filter(filter_id, f"injected:{filter_id}", transform(filter_id))
            for filter_id in FILTER_IDS
        ]

        with self.assertRaisesRegex(
            demo.PipelineStageError,
            "^stage 'redact' output rejected: record.priority must be a string$",
        ):
            demo.run_pipeline({"text": "hello"}, filters=filters)

        self.assertEqual(calls, ["normalize", "redact"])

    def test_duplicate_missing_unknown_and_invalid_filters_are_rejected_preflight(self):
        demo = self.require_demo()

        def make(filter_id):
            return demo.Filter(filter_id, f"injected:{filter_id}", lambda record: record)

        cases = (
            (
                [make("normalize"), make("normalize"), make("classify"), make("prioritize"), make("draft")],
                "duplicate filter: normalize",
            ),
            (
                [make(filter_id) for filter_id in FILTER_IDS[:-1]],
                "filters must be exactly: normalize, redact, classify, prioritize, draft; missing: draft",
            ),
            (
                [make(filter_id) for filter_id in FILTER_IDS] + [make("translate")],
                "filters must be exactly: normalize, redact, classify, prioritize, draft; unexpected: translate",
            ),
            (
                [make("normalize"), make("redact"), object(), make("prioritize"), make("draft")],
                "filters must contain only Filter instances",
            ),
        )

        for filters, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(demo.PipelineConfigurationError, f"^{re.escape(message)}$"):
                    demo.run_pipeline({"text": "hello"}, filters=filters)

    def test_request_schema_types_keys_and_unicode_are_rejected(self):
        demo = self.require_demo()
        cases = (
            (None, "request must be a mapping"),
            ({}, "request fields must be exactly: text; missing: text"),
            ({"text": "hello", "priority": "high"}, "request fields must be exactly: text; unexpected: priority"),
            ({"text": 7}, "request.text must be a string"),
            ({"text": "  \t "}, "request.text must not be blank"),
            ({"text": "bad\ud800text"}, "request.text must contain valid Unicode"),
            ({7: "hello"}, "request field names must be non-empty strings"),
            ({"": "hello"}, "request field names must be non-empty strings"),
        )

        for request, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(demo.PipelineInputError, f"^{re.escape(message)}$"):
                    demo.run_pipeline(request)

    def test_record_schema_types_and_keys_are_rejected_with_stage_attribution(self):
        demo = self.require_demo()

        cases = (
            (None, "record must be a mapping"),
            ({"schema": "support-ticket.v2"}, "record fields must be exactly: schema, text, category, priority, draft; missing: text, category, priority, draft"),
            ({"schema": "support-ticket.v1", "text": "hello", "category": "general", "priority": "normal", "draft": "ok", 7: "bad"}, "record field names must be non-empty strings"),
            ({"schema": "support-ticket.v1", "text": "hello", "category": "general", "priority": "normal", "draft": "ok", "extra": True}, "record fields must be exactly: schema, text, category, priority, draft; unexpected: extra"),
            ({"schema": "support-ticket.v1", "text": "hello", "category": "general", "priority": "normal", "draft": 7}, "record.draft must be a string"),
            ({"schema": "support-ticket.v1", "text": "bad\ud800text", "category": "general", "priority": "normal", "draft": "ok"}, "record.text must contain valid Unicode"),
        )

        for invalid_result, detail in cases:
            with self.subTest(detail=detail):
                calls = []

                def bad_normalize(record, value=invalid_result):
                    calls.append("normalize")
                    return value

                filters = [
                    demo.Filter(
                        item.filter_id,
                        item.skill_path,
                        bad_normalize if item.filter_id == "normalize" else item.transform,
                    )
                    for item in demo.DEFAULT_FILTERS
                ]
                message = f"stage 'normalize' output rejected: {detail}"
                with self.assertRaisesRegex(demo.PipelineStageError, f"^{re.escape(message)}$"):
                    demo.run_pipeline({"text": "hello"}, filters=filters)
                self.assertEqual(calls, ["normalize"])

    def test_result_schema_types_and_keys_are_rejected(self):
        demo = self.require_demo()
        valid_record = demo.run_pipeline({"text": "hello"})["record"]
        cases = (
            (None, "result must be a mapping"),
            ({7: valid_record, "trace": list(FILTER_IDS)}, "result field names must be non-empty strings"),
            ({"record": valid_record}, "result fields must be exactly: record, trace; missing: trace"),
            ({"record": valid_record, "trace": "normalize"}, "result.trace must be a list"),
            ({"record": valid_record, "trace": ["normalize", 7]}, "result.trace entries must be strings"),
            ({"record": valid_record, "trace": list(reversed(FILTER_IDS))}, "result.trace must equal the canonical filter order"),
        )

        for result, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(demo.PipelineResultError, f"^{re.escape(message)}$"):
                    demo.validate_result(result)

    def test_excessive_direct_input_depth_is_rejected(self):
        demo = self.require_demo()
        value = "leaf"
        for _ in range(demo.MAX_JSON_DEPTH + 1):
            value = [value]

        with self.assertRaisesRegex(
            demo.PipelineInputError,
            "^request exceeds maximum nesting depth of 32$",
        ):
            demo.run_pipeline({"text": "hello", "nested": value})

    def test_child_filter_skills_share_one_record_contract(self):
        self.require_demo()
        for filter_id in FILTER_IDS:
            text = (SAMPLE / f"child-skills/{filter_id}/SKILL.md").read_text(encoding="utf-8")
            with self.subTest(filter=filter_id):
                self.assertIn("support-ticket.v1", text)
                self.assertIn("accept and return", text)
                self.assertNotIn("hidden conversation", text.lower())

    def test_invalid_fixtures_match_exact_cli_errors(self):
        self.require_demo()
        cases = (
            ("missing-text.json", "missing-text-error.txt"),
            ("extra-field.json", "extra-field-error.txt"),
            ("wrong-text-type.json", "wrong-text-type-error.txt"),
            ("blank-text.json", "blank-text-error.txt"),
            ("duplicate-root-member.json", "duplicate-root-member-error.txt"),
            ("duplicate-nested-member.json", "duplicate-nested-member-error.txt"),
            ("lone-surrogate.json", "lone-surrogate-error.txt"),
            ("excessive-depth.json", "excessive-depth-error.txt"),
            ("invalid-json.json", "invalid-json-error.txt"),
        )

        for fixture, expected in cases:
            with self.subTest(fixture=fixture):
                completed = subprocess.run(
                    [sys.executable, str(DEMO_PATH), str(SAMPLE / "fixtures/invalid" / fixture)],
                    cwd=SAMPLE,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(completed.returncode, 2)
                self.assertEqual(completed.stdout, "")
                self.assertEqual(
                    completed.stderr,
                    (SAMPLE / "expected" / expected).read_text(encoding="utf-8"),
                )

    def test_non_utf8_cli_error_is_stable(self):
        self.require_demo()
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "ticket.json"
            path.write_bytes(b"\xff")

            completed = subprocess.run(
                [sys.executable, str(DEMO_PATH), str(path)],
                cwd=SAMPLE,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(
            completed.stderr,
            (SAMPLE / "expected/non-utf8-ticket-error.txt").read_text(encoding="utf-8"),
        )

    def test_default_cli_matches_expected_output(self):
        self.require_demo()

        completed = subprocess.run(
            [sys.executable, str(DEMO_PATH)],
            cwd=SAMPLE,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stderr, "")
        self.assertEqual(
            completed.stdout,
            (SAMPLE / "expected/urgent-access-result.json").read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
