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

    def test_plan_compatibility_review_api_is_verbatim_and_exact(self):
        demo = self.require_demo()

        self.assertEqual(
            demo.review({"files": 5, "security_sensitive": False}),
            {"strategy": "fast-scan", "findings": [], "confidence": "medium"},
        )
        self.assertEqual(
            demo.review({"files": 6, "security_sensitive": False}),
            {"strategy": "deep-review", "findings": [], "confidence": "high"},
        )
        self.assertEqual(
            demo.review({"files": 1, "security_sensitive": True}),
            {"strategy": "deep-review", "findings": [], "confidence": "high"},
        )
        self.assertEqual(
            tuple(demo.review({"security_sensitive": False, "files": 0})),
            ("strategy", "findings", "confidence"),
        )

    def test_plan_compatibility_review_validates_exact_types(self):
        demo = self.require_demo()
        cases = (
            ({"files": True, "security_sensitive": False}, "files must be a non-negative integer"),
            ({"files": -1, "security_sensitive": False}, "files must be a non-negative integer"),
            ({"files": 1, "security_sensitive": 0}, "security_sensitive must be a boolean"),
            ({"files": 1}, "compatibility request fields must be exactly: files, security_sensitive; missing: security_sensitive"),
        )
        for request, error in cases:
            with self.subTest(error=error):
                with self.assertRaisesRegex(demo.ValidationError, f"^{error}$"):
                    demo.review(request)

    def test_plan_compatibility_review_delegates_to_exactly_one_callable(self):
        demo = self.require_demo()
        cases = (
            ({"files": 5, "security_sensitive": False}, "fast-scan"),
            ({"files": 6, "security_sensitive": False}, "deep-review"),
            ({"files": 1, "security_sensitive": True}, "deep-review"),
        )

        for change, expected_strategy in cases:
            calls = []

            def fast_spy(candidate):
                calls.append(("fast-scan", deepcopy(candidate)))
                return {
                    "strategy": "fast-scan",
                    "findings": [],
                    "confidence": "medium",
                }

            def deep_spy(candidate):
                calls.append(("deep-review", deepcopy(candidate)))
                return {
                    "strategy": "deep-review",
                    "findings": [],
                    "confidence": "high",
                }

            with self.subTest(change=change):
                result = demo.review(
                    change,
                    fast_strategy=fast_spy,
                    deep_strategy=deep_spy,
                )

                self.assertEqual(result["strategy"], expected_strategy)
                self.assertEqual(calls, [(expected_strategy, change)])

    def test_compact_concrete_strategies_share_the_exact_contract(self):
        demo = self.require_demo()
        change = {"files": 2, "security_sensitive": False}

        fast = demo.fast_scan(change)
        deep = demo.deep_review(change)

        self.assertEqual(tuple(fast), demo.COMPATIBILITY_RESULT_FIELDS)
        self.assertEqual(tuple(deep), demo.COMPATIBILITY_RESULT_FIELDS)
        self.assertEqual(fast["strategy"], "fast-scan")
        self.assertEqual(deep["strategy"], "deep-review")

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

    def test_builtin_strategies_own_their_declared_rule_sets(self):
        demo = self.require_demo()
        request = {
            "schema": demo.REQUEST_SCHEMA,
            "review_id": "CR-RULES-001",
            "security_sensitive": False,
            "files": [
                {
                    "path": "src/security.py",
                    "additions": [
                        "value = eval(text)",
                        "password = 'secret-value'",
                        "client.get(url, verify=False)",
                        'query = "SELECT * FROM users WHERE id = " + user_id',
                        "skip_auth = True",
                        "policy = {'Action': '*'}",
                    ],
                }
            ],
        }

        fast = demo.FastScanStrategy().review(request)
        deep = demo.DeepReviewStrategy().review(request)

        self.assertEqual(
            [item["rule_id"] for item in fast["findings"]],
            ["dynamic-execution", "hardcoded-secret", "insecure-tls"],
        )
        self.assertEqual(
            [item["rule_id"] for item in deep["findings"]],
            [
                "dynamic-execution",
                "hardcoded-secret",
                "insecure-tls",
                "sql-concatenation",
                "authorization-bypass",
                "wildcard-permission",
            ],
        )

    def test_mapping_key_order_is_semantically_irrelevant(self):
        demo = self.require_demo()
        original = self.load_json("fixtures/valid/low-risk-review.json")
        reordered = {
            "files": [
                {"additions": item["additions"], "path": item["path"]}
                for item in original["files"]
            ],
            "security_sensitive": original["security_sensitive"],
            "review_id": original["review_id"],
            "schema": original["schema"],
        }

        result = demo.RiskAwareCodeReview().review(reordered)

        self.assertEqual(
            result, self.load_json("expected/low-risk-review-result.json")
        )
        self.assertEqual(tuple(result), demo.RESULT_FIELDS)

    def test_shared_boundary_canonicalizes_custom_result_and_finding_order(self):
        demo = self.require_demo()
        request = self.load_json("fixtures/valid/low-risk-review.json")

        class CustomStrategy:
            strategy_id = "fast-scan"

            def review(self, candidate):
                return {
                    "summary": {
                        "low": 0,
                        "medium": 1,
                        "high": 1,
                        "findings": 2,
                        "files_reviewed": 2,
                    },
                    "findings": [
                        {
                            "message": "Custom test risk.",
                            "line": 1,
                            "path": "tests/test_formatter.py",
                            "severity": "medium",
                            "rule_id": "custom-test-risk",
                        },
                        {
                            "message": "Custom source risk.",
                            "line": 2,
                            "path": "src/formatter.py",
                            "severity": "high",
                            "rule_id": "custom-source-risk",
                        },
                    ],
                    "reviewed_files": [
                        "src/formatter.py",
                        "tests/test_formatter.py",
                    ],
                    "strategy": "fast-scan",
                    "review_id": "CR-LOW-001",
                    "schema": demo.RESULT_SCHEMA,
                }

        result = demo.RiskAwareCodeReview(
            {
                "fast-scan": CustomStrategy(),
                "deep-review": demo.DeepReviewStrategy(),
            }
        ).review(request)

        self.assertEqual(tuple(result), demo.RESULT_FIELDS)
        self.assertEqual(
            [tuple(item) for item in result["findings"]],
            [demo.FINDING_FIELDS, demo.FINDING_FIELDS],
        )
        self.assertEqual(
            [item["rule_id"] for item in result["findings"]],
            ["custom-source-risk", "custom-test-risk"],
        )
        self.assertEqual(tuple(result["summary"]), demo.SUMMARY_FIELDS)

    def test_shared_boundary_rejects_duplicate_finding_identity(self):
        demo = self.require_demo()
        request = self.load_json("fixtures/valid/low-risk-review.json")
        result = demo.FastScanStrategy().review(request)
        duplicate = {
            "rule_id": "custom-risk",
            "severity": "low",
            "path": "src/formatter.py",
            "line": 1,
            "message": "First.",
        }
        result["findings"] = [duplicate, {**duplicate, "message": "Second."}]
        result["summary"] = {
            "files_reviewed": 2,
            "findings": 2,
            "high": 0,
            "medium": 0,
            "low": 2,
        }

        with self.assertRaisesRegex(
            demo.StrategyContractError,
            r"^duplicate finding identity: custom-risk, src/formatter.py, 1$",
        ):
            demo.validate_review_result(result, request)

    def test_summary_counts_are_non_negative_integers_not_bool_or_float(self):
        demo = self.require_demo()
        request = self.load_json("fixtures/valid/low-risk-review.json")
        cases = (
            ("files_reviewed", True),
            ("findings", 0.0),
            ("high", -1),
        )
        for field, value in cases:
            result = demo.FastScanStrategy().review(request)
            result["summary"][field] = value
            with self.subTest(field=field, value=value):
                with self.assertRaisesRegex(
                    demo.StrategyContractError,
                    rf"^summary\.{field} must be a non-negative integer$",
                ):
                    demo.validate_review_result(result, request)

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

    def test_non_string_explicit_strategy_is_rejected_stably(self):
        demo = self.require_demo()
        request = self.load_json("fixtures/valid/low-risk-review.json")

        with self.assertRaisesRegex(
            demo.ValidationError,
            r"^strategy_id must be a string$",
        ):
            demo.RiskAwareCodeReview().review(request, strategy_id=[])

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

    def test_lone_unicode_surrogate_matches_stable_cli_error(self):
        self.require_demo()
        completed = subprocess.run(
            [
                sys.executable,
                str(DEMO_PATH),
                "fixtures/invalid/lone-surrogate.json",
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
            (SAMPLE / "expected/lone-surrogate-error.txt").read_text(
                encoding="utf-8"
            ),
        )

    def test_duplicate_json_members_at_root_and_nested_depth_are_rejected(self):
        self.require_demo()
        cases = (
            ("duplicate-root-member", "duplicate-root-member-error"),
            ("duplicate-nested-member", "duplicate-nested-member-error"),
        )
        for fixture_stem, error_stem in cases:
            with self.subTest(fixture=fixture_stem):
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(DEMO_PATH),
                        f"fixtures/invalid/{fixture_stem}.json",
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
                    (SAMPLE / f"expected/{error_stem}.txt").read_text(
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
