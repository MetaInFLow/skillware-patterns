from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


SAMPLE = Path(__file__).resolve().parents[1]
RECORD = SAMPLE.parent
DEMO_PATH = SAMPLE / "scripts/run_demo.py"


class StrategyDemoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not DEMO_PATH.is_file():
            return
        spec = importlib.util.spec_from_file_location("strategy_demo", DEMO_PATH)
        cls.demo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.demo)

    def require_demo(self):
        self.assertTrue(DEMO_PATH.is_file(), "Strategy demo is not implemented")
        return self.demo

    def load_json(self, relative_path):
        return json.loads((SAMPLE / relative_path).read_text(encoding="utf-8"))

    def test_risk_selector_is_explicit_and_deterministic(self):
        demo = self.require_demo()
        low_risk = self.load_json("fixtures/valid/low-risk-review.json")
        security_sensitive = deepcopy(low_risk)
        security_sensitive["security_sensitive"] = True
        threshold = deepcopy(low_risk)
        threshold["files"] = [
            {"path": f"src/file-{index}.py", "additions": []}
            for index in range(demo.DEEP_REVIEW_FILE_THRESHOLD)
        ]

        self.assertEqual(demo.select_strategy(low_risk), "fast-scan")
        self.assertEqual(demo.select_strategy(security_sensitive), "deep-review")
        self.assertEqual(demo.select_strategy(threshold), "deep-review")
        self.assertEqual(demo.DEEP_REVIEW_FILE_THRESHOLD, 4)

    def test_selection_and_delegation_are_independently_injectable(self):
        demo = self.require_demo()
        request = self.load_json("fixtures/valid/low-risk-review.json")
        calls = []

        class StubStrategy:
            def __init__(self, strategy_id):
                self.strategy_id = strategy_id

            def review(self, candidate):
                calls.append((self.strategy_id, deepcopy(candidate)))
                return {
                    "schema": demo.RESULT_SCHEMA,
                    "review_id": candidate["review_id"],
                    "strategy": self.strategy_id,
                    "reviewed_files": [item["path"] for item in candidate["files"]],
                    "findings": [],
                    "summary": {
                        "files_reviewed": len(candidate["files"]),
                        "findings": 0,
                        "high": 0,
                        "medium": 0,
                        "low": 0,
                    },
                }

        context = demo.RiskAwareCodeReview(
            {
                "fast-scan": StubStrategy("fast-scan"),
                "deep-review": StubStrategy("deep-review"),
            }
        )

        result = context.review(request)

        self.assertEqual(result["strategy"], "fast-scan")
        self.assertEqual(calls, [("fast-scan", request)])

    def test_explicit_addressing_can_swap_strategies_without_changing_context(self):
        demo = self.require_demo()
        request = self.load_json("fixtures/valid/low-risk-review.json")
        context = demo.RiskAwareCodeReview()

        fast = context.review(request, strategy_id="fast-scan")
        deep = context.review(request, strategy_id="deep-review")

        self.assertEqual(fast["strategy"], "fast-scan")
        self.assertEqual(deep["strategy"], "deep-review")
        self.assertEqual(tuple(fast), demo.RESULT_FIELDS)
        self.assertEqual(tuple(deep), demo.RESULT_FIELDS)
        self.assertEqual(fast["reviewed_files"], deep["reviewed_files"])
        self.assertEqual(fast["review_id"], deep["review_id"])

    def test_fast_and_deep_review_are_distinct_procedures_with_one_contract(self):
        demo = self.require_demo()
        request = {
            "schema": demo.REQUEST_SCHEMA,
            "review_id": "CR-SWAP-001",
            "security_sensitive": False,
            "files": [
                {
                    "path": "src/report.py",
                    "additions": [
                        'query = "SELECT * FROM users WHERE id = " + user_id'
                    ],
                }
            ],
        }

        fast = demo.FastScanStrategy().review(request)
        deep = demo.DeepReviewStrategy().review(request)

        self.assertEqual(tuple(fast), demo.RESULT_FIELDS)
        self.assertEqual(tuple(deep), demo.RESULT_FIELDS)
        self.assertEqual(fast["findings"], [])
        self.assertEqual(
            [finding["rule_id"] for finding in deep["findings"]],
            ["sql-concatenation"],
        )
        self.assertEqual(demo.validate_review_result(fast, request), fast)
        self.assertEqual(demo.validate_review_result(deep, request), deep)

    def test_invalid_injected_result_is_rejected_at_the_strategy_boundary(self):
        demo = self.require_demo()
        request = self.load_json("fixtures/valid/low-risk-review.json")

        class IncompatibleStrategy:
            strategy_id = "fast-scan"

            def review(self, candidate):
                return {"links": ["https://example.invalid"]}

        context = demo.RiskAwareCodeReview(
            {
                "fast-scan": IncompatibleStrategy(),
                "deep-review": demo.DeepReviewStrategy(),
            }
        )

        with self.assertRaisesRegex(
            demo.StrategyContractError,
            r"^strategy result fields must be exactly: schema, review_id, strategy, reviewed_files, findings, summary; missing: schema, review_id, strategy, reviewed_files, findings, summary; unexpected: links$",
        ):
            context.review(request)

    def test_strategy_registry_rejects_mismatched_or_non_callable_entries(self):
        demo = self.require_demo()

        class WrongId:
            strategy_id = "other"

            def review(self, request):
                return {}

        with self.assertRaisesRegex(
            demo.StrategyContractError,
            r"^strategy registry key 'fast-scan' does not match strategy_id 'other'$",
        ):
            demo.RiskAwareCodeReview(
                {"fast-scan": WrongId(), "deep-review": demo.DeepReviewStrategy()}
            )
        with self.assertRaisesRegex(
            demo.StrategyContractError,
            r"^strategy 'fast-scan' review must be callable$",
        ):
            demo.RiskAwareCodeReview(
                {"fast-scan": object(), "deep-review": demo.DeepReviewStrategy()}
            )

    def test_review_does_not_mutate_the_request(self):
        demo = self.require_demo()
        request = self.load_json("fixtures/valid/security-sensitive-review.json")
        original = deepcopy(request)

        first = demo.RiskAwareCodeReview().review(request)
        second = demo.RiskAwareCodeReview().review(request)

        self.assertEqual(request, original)
        self.assertEqual(first, second)

    def test_valid_fixtures_match_exact_expected_outputs(self):
        demo = self.require_demo()
        cases = (
            ("low-risk-review", "fast-scan"),
            ("security-sensitive-review", "deep-review"),
            ("file-threshold-review", "deep-review"),
        )

        for stem, expected_strategy in cases:
            with self.subTest(fixture=stem):
                request = self.load_json(f"fixtures/valid/{stem}.json")
                result = demo.RiskAwareCodeReview().review(request)
                self.assertEqual(result["strategy"], expected_strategy)
                self.assertEqual(result, self.load_json(f"expected/{stem}-result.json"))

    def test_request_schema_types_and_bounds_are_validated(self):
        demo = self.require_demo()
        valid = self.load_json("fixtures/valid/low-risk-review.json")
        cases = []

        too_long_id = deepcopy(valid)
        too_long_id["review_id"] = "x" * 65
        cases.append((too_long_id, "request.review_id must contain at most 64 characters"))

        too_many_files = deepcopy(valid)
        too_many_files["files"] = [
            {"path": f"src/file-{index}.py", "additions": []}
            for index in range(51)
        ]
        cases.append((too_many_files, "request files must contain between 1 and 50 items"))

        too_many_lines = deepcopy(valid)
        too_many_lines["files"][0]["additions"] = ["pass"] * 201
        cases.append((too_many_lines, "file.additions must contain at most 200 lines"))

        too_long_line = deepcopy(valid)
        too_long_line["files"][0]["additions"] = ["x" * 501]
        cases.append((too_long_line, "file.additions line 1 must contain at most 500 characters"))

        duplicate_path = deepcopy(valid)
        duplicate_path["files"].append(deepcopy(duplicate_path["files"][0]))
        cases.append((duplicate_path, "request file paths must be unique: src/formatter.py"))

        normalized_path = deepcopy(valid)
        normalized_path["files"][0]["path"] = "src/./formatter.py"
        cases.append((normalized_path, "file.path must be a safe relative POSIX path"))

        for request, error in cases:
            with self.subTest(error=error):
                with self.assertRaisesRegex(demo.ValidationError, f"^{error}$"):
                    demo.validate_request(request)

    def test_invalid_fixtures_match_exact_cli_errors(self):
        self.require_demo()
        cases = (
            ("malformed-request", "malformed-request-error"),
            ("unsupported-schema", "unsupported-schema-error"),
            ("invalid-security-sensitive", "invalid-security-sensitive-error"),
            ("empty-files", "empty-files-error"),
            ("unsafe-path", "unsafe-path-error"),
            ("invalid-line", "invalid-line-error"),
            ("invalid-json", "invalid-json-error"),
        )

        for fixture_stem, error_stem in cases:
            with self.subTest(fixture=fixture_stem):
                completed = subprocess.run(
                    [sys.executable, str(DEMO_PATH), f"fixtures/invalid/{fixture_stem}.json"],
                    cwd=SAMPLE,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(completed.returncode, 2)
                self.assertEqual(completed.stdout, "")
                self.assertEqual(
                    completed.stderr,
                    (SAMPLE / f"expected/{error_stem}.txt").read_text(encoding="utf-8"),
                )

    def test_unknown_explicit_strategy_matches_stable_cli_error(self):
        self.require_demo()
        completed = subprocess.run(
            [
                sys.executable,
                str(DEMO_PATH),
                "fixtures/valid/low-risk-review.json",
                "--strategy",
                "unsupported",
            ],
            cwd=SAMPLE,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(
            completed.stderr,
            (SAMPLE / "expected/unknown-strategy-error.txt").read_text(
                encoding="utf-8"
            ),
        )

    def test_non_utf8_request_matches_stable_cli_error(self):
        self.require_demo()
        with TemporaryDirectory() as temp_dir:
            fixture = Path(temp_dir) / "non-utf8-request.json"
            fixture.write_bytes(b"\xff\xfe")
            completed = subprocess.run(
                [sys.executable, str(DEMO_PATH), str(fixture)],
                cwd=SAMPLE,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(
            completed.stderr,
            (SAMPLE / "expected/non-utf8-request-error.txt").read_text(
                encoding="utf-8"
            ),
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
            (SAMPLE / "expected/low-risk-review-result.json").read_text(
                encoding="utf-8"
            ),
        )

    def test_participant_and_evidence_paths_resolve_locally(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML is only required for record verification")

        participant_map = yaml.safe_load(
            (RECORD / "participant-map.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(
            set(participant_map["participants"]),
            {"Context", "Strategy", "ConcreteStrategy"},
        )
        concrete_ids = {
            item["id"]
            for item in participant_map["participants"]["ConcreteStrategy"][
                "implementations"
            ]
        }
        self.assertEqual(concrete_ids, {"fast-scan", "deep-review"})
        self.assertEqual(
            set(participant_map["execution_context"]),
            {"Agent Host", "Agent Runtime"},
        )
        self.assertTrue((RECORD / participant_map["evidence_path"]).is_file())

    def test_demo_uses_only_the_standard_library_and_no_network(self):
        self.require_demo()
        source = DEMO_PATH.read_text(encoding="utf-8")
        for forbidden in (
            "requests",
            "urllib",
            "http.client",
            "socket",
            "openai",
            "anthropic",
        ):
            with self.subTest(module=forbidden):
                self.assertNotIn(f"import {forbidden}", source)
                self.assertNotIn(f"from {forbidden}", source)


if __name__ == "__main__":
    unittest.main()
