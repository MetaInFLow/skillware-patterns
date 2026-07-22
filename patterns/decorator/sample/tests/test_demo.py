from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


SAMPLE = Path(__file__).resolve().parents[1]
RECORD = SAMPLE.parent
DEMO_PATH = SAMPLE / "scripts/run_demo.py"


class DecoratorDemoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not DEMO_PATH.is_file():
            return
        spec = importlib.util.spec_from_file_location("decorator_demo", DEMO_PATH)
        cls.demo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.demo)

    def require_demo(self):
        self.assertTrue(DEMO_PATH.is_file(), "Decorator demo is not implemented")
        return self.demo

    def load_json(self, relative_path):
        return json.loads((SAMPLE / relative_path).read_text(encoding="utf-8"))

    def run_cli(self, *arguments):
        return subprocess.run(
            [sys.executable, str(DEMO_PATH), *map(str, arguments)],
            cwd=SAMPLE,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

    def test_plan_compatibility_api_is_verbatim_and_exact(self):
        demo = self.require_demo()

        wrapped = demo.with_citation_check(
            demo.with_privacy_check(demo.base_review)
        )
        result = wrapped({"text": "Email a@example.com cites [missing]."})

        self.assertEqual(set(result), {"summary", "findings"})
        self.assertEqual(
            [item["type"] for item in result["findings"]],
            ["privacy", "citation"],
        )
        self.assertEqual(tuple(result), ("summary", "findings"))

    def test_each_component_preserves_the_exact_request_result_contract(self):
        demo = self.require_demo()
        request = {"text": "Email a@example.com cites [missing]."}
        components = (
            demo.base_review,
            demo.with_privacy_check(demo.base_review),
            demo.with_citation_check(demo.base_review),
            demo.with_citation_check(
                demo.with_privacy_check(demo.base_review)
            ),
        )

        for component in components:
            with self.subTest(component=getattr(component, "__name__", repr(component))):
                result = component(deepcopy(request))
                self.assertEqual(tuple(result), demo.RESULT_FIELDS)
                self.assertEqual(demo.validate_result(result), result)

    def test_nested_decorator_order_is_the_finding_order(self):
        demo = self.require_demo()
        request = {"text": "Email a@example.com cites [missing]."}

        privacy_then_citation = demo.with_citation_check(
            demo.with_privacy_check(demo.base_review)
        )
        citation_then_privacy = demo.with_privacy_check(
            demo.with_citation_check(demo.base_review)
        )

        self.assertEqual(
            [item["type"] for item in privacy_then_citation(request)["findings"]],
            ["privacy", "citation"],
        )
        self.assertEqual(
            [item["type"] for item in citation_then_privacy(request)["findings"]],
            ["citation", "privacy"],
        )

    def test_decorators_add_only_their_bounded_responsibility(self):
        demo = self.require_demo()
        cases = (
            ("No enhanced checks apply.", []),
            ("Contact legal@example.com.", ["privacy"]),
            ("Evidence cites [missing].", ["citation"]),
            (
                "Contact legal@example.com and cite [missing].",
                ["privacy", "citation"],
            ),
        )

        wrapped = demo.compose_review(("privacy-check", "citation-check"))
        for text, expected_types in cases:
            with self.subTest(text=text):
                result = wrapped({"text": text})
                self.assertEqual(
                    [item["type"] for item in result["findings"]],
                    expected_types,
                )
                self.assertEqual(result["summary"], demo.BASE_SUMMARY)

    def test_wrappers_delegate_once_and_do_not_copy_base_logic(self):
        demo = self.require_demo()
        calls = []

        def component(request):
            calls.append(deepcopy(request))
            return {
                "summary": "Injected component summary.",
                "findings": [
                    {"type": "base", "message": "Injected base finding."}
                ],
            }

        wrapped = demo.with_citation_check(
            demo.with_privacy_check(component)
        )
        request = {"text": "Email a@example.com cites [missing]."}

        result = wrapped(request)

        self.assertEqual(calls, [request])
        self.assertEqual(result["summary"], "Injected component summary.")
        self.assertEqual(
            [item["type"] for item in result["findings"]],
            ["base", "privacy", "citation"],
        )

    def test_wrapper_boundary_prevents_input_and_result_alias_leaks(self):
        demo = self.require_demo()
        original = {"text": "Email a@example.com cites [missing]."}
        shared = {
            "summary": "Shared summary.",
            "findings": [{"type": "base", "message": "Shared finding."}],
        }

        def mutating_component(request):
            request["text"] = "mutated by wrapped component"
            return shared

        wrapped = demo.with_citation_check(
            demo.with_privacy_check(mutating_component)
        )

        first = wrapped(original)
        first["summary"] = "caller mutation"
        first["findings"][0]["message"] = "caller mutation"
        first["findings"].append({"type": "caller", "message": "mutation"})
        second = wrapped(original)

        self.assertEqual(
            original,
            {"text": "Email a@example.com cites [missing]."},
        )
        self.assertEqual(
            shared,
            {
                "summary": "Shared summary.",
                "findings": [
                    {"type": "base", "message": "Shared finding."}
                ],
            },
        )
        self.assertEqual(
            [item["type"] for item in second["findings"]],
            ["base", "privacy", "citation"],
        )
        self.assertEqual(second["summary"], "Shared summary.")

    def test_wrapper_propagates_component_failure_without_synthesizing_result(self):
        demo = self.require_demo()
        failure = RuntimeError("base review failed")

        def failing_component(_request):
            raise failure

        wrapped = demo.with_privacy_check(failing_component)

        with self.assertRaises(RuntimeError) as caught:
            wrapped({"text": "Email a@example.com."})
        self.assertIs(caught.exception, failure)

    def test_wrapper_rejects_non_callable_and_malformed_component_results(self):
        demo = self.require_demo()

        with self.assertRaisesRegex(
            demo.ComponentContractError,
            "^wrapped component must be callable$",
        ):
            demo.with_privacy_check({})

        cases = (
            (
                lambda _request: None,
                "component result must be a JSON object",
            ),
            (
                lambda _request: {"summary": "ok"},
                "component result fields must be exactly: summary, findings; missing: findings",
            ),
            (
                lambda _request: {"summary": "ok", "findings": "none"},
                "component result.findings must be a JSON array",
            ),
            (
                lambda _request: {
                    "summary": "ok",
                    "findings": [{"type": "base", "message": "ok", "extra": 1}],
                },
                "component finding fields must be exactly: type, message; unexpected: extra",
            ),
            (
                lambda _request: {
                    "summary": "ok",
                    "findings": [{"type": "base", "message": "\ud800"}],
                },
                "component result must not contain lone Unicode surrogates",
            ),
        )

        for component, error in cases:
            with self.subTest(error=error):
                wrapped = demo.with_citation_check(component)
                with self.assertRaisesRegex(
                    demo.ComponentContractError,
                    f"^{error}$",
                ):
                    wrapped({"text": "A valid contract."})

    def test_request_validation_is_strict_and_bool_is_not_a_string(self):
        demo = self.require_demo()
        cases = (
            (None, "request must be a JSON object"),
            (
                {},
                "request fields must be exactly: text; missing: text",
            ),
            (
                {"text": "ok", "extra": True},
                "request fields must be exactly: text; unexpected: extra",
            ),
            ({"text": True}, "request.text must be a string"),
            ({"text": "   "}, "request.text must be non-empty"),
            (
                {"text": "x" * (demo.MAX_TEXT_CHARACTERS + 1)},
                f"request.text must contain at most {demo.MAX_TEXT_CHARACTERS} characters",
            ),
            (
                {"text": "bad \ud800 text"},
                "request must not contain lone Unicode surrogates",
            ),
        )

        for request, error in cases:
            with self.subTest(error=error):
                with self.assertRaisesRegex(demo.ValidationError, f"^{error}$"):
                    demo.base_review(request)

    def test_result_validation_canonicalizes_members_without_reordering_findings(self):
        demo = self.require_demo()
        candidate = {
            "findings": [
                {"message": "Second in source order.", "type": "second"},
                {"message": "First in source order.", "type": "first"},
            ],
            "summary": "Valid summary.",
        }

        result = demo.validate_result(candidate)

        self.assertEqual(tuple(result), demo.RESULT_FIELDS)
        self.assertEqual(
            [tuple(item) for item in result["findings"]],
            [demo.FINDING_FIELDS, demo.FINDING_FIELDS],
        )
        self.assertEqual(
            [item["type"] for item in result["findings"]],
            ["second", "first"],
        )

    def test_manifest_default_composition_uses_executable_canonical_ids(self):
        demo = self.require_demo()
        manifest = (SAMPLE / "skillware.yaml").read_text(encoding="utf-8")
        decorator_ids = ("privacy-check", "citation-check")

        self.assertIn(f"component_contract: {demo.COMPONENT_CONTRACT}", manifest)
        for decorator_id in demo.DECORATOR_IDS:
            self.assertIn(f"  - id: {decorator_id}", manifest)
        self.assertIn("inside_to_outside: [privacy-check, citation-check]", manifest)
        self.assertIn("finding_order: [privacy, citation]", manifest)

        result = demo.compose_review(decorator_ids)(
            {"text": "Email a@example.com cites [missing]."}
        )

        self.assertEqual(
            [item["type"] for item in result["findings"]],
            ["privacy", "citation"],
        )
        self.assertTrue(
            set(decorator_ids).issubset(demo.DECORATORS),
            "manifest decorator ids must be executable without translation",
        )

    def test_result_contract_has_no_finite_findings_count_cap(self):
        demo = self.require_demo()
        findings = [
            {"type": f"base-{index}", "message": f"Finding {index}."}
            for index in range(125)
        ]

        def large_component(_request):
            return {"summary": "Large valid result.", "findings": findings}

        wrapped = demo.with_privacy_check(large_component)
        result = wrapped({"text": "Contact legal@example.com."})

        self.assertEqual(len(result["findings"]), 126)
        self.assertEqual(result["findings"][:125], findings)
        self.assertEqual(result["findings"][-1]["type"], "privacy")

    def test_many_composed_wrappers_remain_substitutable_and_idempotent(self):
        demo = self.require_demo()
        decorator_ids = (
            ["privacy-check", "citation-check", "compliance-check"] * 40
        )
        component = demo.compose_review(decorator_ids)

        result = component(
            {
                "text": (
                    "Email a@example.com cites [missing] and marks "
                    "[noncompliant]."
                )
            }
        )

        self.assertEqual(tuple(result), demo.RESULT_FIELDS)
        self.assertEqual(
            [item["type"] for item in result["findings"]],
            ["privacy", "citation", "compliance"],
        )

    def test_repeated_or_preexisting_identical_finding_is_not_duplicated(self):
        demo = self.require_demo()
        request = {"text": "Contact legal@example.com."}
        repeated = demo.with_privacy_check(
            demo.with_privacy_check(demo.with_privacy_check(demo.base_review))
        )

        self.assertEqual(
            [item["type"] for item in repeated(request)["findings"]],
            ["privacy"],
        )

        def preexisting(_request):
            return {
                "summary": "Existing result.",
                "findings": [
                    {
                        "type": "privacy",
                        "message": "Email address detected.",
                    }
                ],
            }

        result = demo.with_privacy_check(preexisting)(request)
        self.assertEqual(len(result["findings"]), 1)

    def test_duplicate_finding_identity_is_rejected(self):
        demo = self.require_demo()
        finding = {"type": "privacy", "message": "Email address detected."}

        with self.assertRaises(demo.ComponentContractError) as caught:
            demo.validate_result(
                {
                    "summary": "Invalid duplicates.",
                    "findings": [finding, deepcopy(finding)],
                }
            )

        self.assertEqual(
            str(caught.exception),
            (
                "result findings must have unique (type, message) identity: "
                "privacy | Email address detected."
            ),
        )

    def test_optional_compliance_decorator_preserves_the_component_contract(self):
        demo = self.require_demo()
        component = demo.compose_review(
            ("privacy-check", "citation-check", "compliance-check")
        )

        result = component(
            {
                "text": (
                    "Email a@example.com cites [missing] and marks "
                    "[noncompliant]."
                )
            }
        )

        self.assertEqual(tuple(result), demo.RESULT_FIELDS)
        self.assertEqual(
            [item["type"] for item in result["findings"]],
            ["privacy", "citation", "compliance"],
        )

    def test_compose_review_rejects_unknown_or_malformed_decorator_ids(self):
        demo = self.require_demo()
        cases = (
            (
                ("privacy-check", "unknown"),
                "unknown decorator id: unknown",
            ),
            ("privacy", "decorator ids must be an array of strings"),
        )

        for decorators, error in cases:
            with self.subTest(error=error):
                with self.assertRaisesRegex(demo.ValidationError, f"^{error}$"):
                    demo.compose_review(decorators)

    def test_valid_fixtures_match_exact_expected_results(self):
        demo = self.require_demo()
        cases = (
            (
                "fixtures/valid/enhanced-contract.json",
                "expected/enhanced-contract-result.json",
            ),
            (
                "fixtures/valid/clean-contract.json",
                "expected/clean-contract-result.json",
            ),
        )

        for fixture_path, expected_path in cases:
            with self.subTest(fixture=fixture_path):
                request = demo.load_request(SAMPLE / fixture_path)
                result = demo.compose_review(
                    ("privacy-check", "citation-check")
                )(request)
                self.assertEqual(result, self.load_json(expected_path))

    def test_exact_field_validation_rejects_non_string_mapping_keys(self):
        demo = self.require_demo()

        with self.assertRaises(demo.ValidationError) as request_error:
            demo.base_review({1: "not a JSON member name"})
        self.assertEqual(
            str(request_error.exception),
            "request field names must be strings",
        )

        with self.assertRaises(demo.ComponentContractError) as result_error:
            demo.validate_result(
                {"summary": "ok", "findings": [{1: "invalid"}]}
            )
        self.assertEqual(
            str(result_error.exception),
            "finding field names must be strings",
        )

    def test_surrogate_validation_is_cycle_safe_for_programmatic_values(self):
        demo = self.require_demo()
        cyclic_request = {"text": "valid"}
        cyclic_request["cycle"] = cyclic_request
        cyclic_result = {"summary": "valid", "findings": []}
        cyclic_result["findings"].append(cyclic_result)

        with self.assertRaises(demo.ValidationError) as request_error:
            demo.base_review(cyclic_request)
        self.assertEqual(
            str(request_error.exception),
            "request must not contain cyclic references",
        )

        with self.assertRaises(demo.ComponentContractError) as result_error:
            demo.validate_result(cyclic_result)
        self.assertEqual(
            str(result_error.exception),
            "result must not contain cyclic references",
        )

    def test_result_string_bounds_are_enforced(self):
        demo = self.require_demo()
        cases = (
            (
                {
                    "summary": "x" * (demo.MAX_SUMMARY_CHARACTERS + 1),
                    "findings": [],
                },
                (
                    "result.summary must contain at most "
                    f"{demo.MAX_SUMMARY_CHARACTERS} characters"
                ),
            ),
            (
                {
                    "summary": "ok",
                    "findings": [
                        {
                            "type": "x" * (
                                demo.MAX_FINDING_FIELD_CHARACTERS + 1
                            ),
                            "message": "ok",
                        }
                    ],
                },
                (
                    "finding.type must contain at most "
                    f"{demo.MAX_FINDING_FIELD_CHARACTERS} characters"
                ),
            ),
            (
                {
                    "summary": "ok",
                    "findings": [
                        {
                            "type": "bounded",
                            "message": "x" * (
                                demo.MAX_FINDING_FIELD_CHARACTERS + 1
                            ),
                        }
                    ],
                },
                (
                    "finding.message must contain at most "
                    f"{demo.MAX_FINDING_FIELD_CHARACTERS} characters"
                ),
            ),
        )

        for result, error in cases:
            with self.subTest(error=error):
                with self.assertRaises(demo.ComponentContractError) as caught:
                    demo.validate_result(result)
                self.assertEqual(str(caught.exception), error)

    def test_invalid_fixtures_have_exact_stable_errors(self):
        cases = (
            ("malformed-request",),
            ("wrong-text-type",),
            ("blank-text",),
            ("invalid-json",),
            ("lone-surrogate",),
            ("duplicate-root-member",),
            ("duplicate-nested-member",),
            ("excessive-depth",),
        )

        for (name,) in cases:
            with self.subTest(name=name):
                completed = self.run_cli(
                    SAMPLE / f"fixtures/invalid/{name}.json"
                )
                expected = (SAMPLE / f"expected/{name}-error.txt").read_text(
                    encoding="utf-8"
                )
                self.assertEqual(completed.returncode, 2)
                self.assertEqual(completed.stdout, "")
                self.assertEqual(completed.stderr, expected)

    def test_invalid_utf8_has_exact_stable_error(self):
        with TemporaryDirectory() as temp_dir:
            request = Path(temp_dir) / "non-utf8.json"
            request.write_bytes(b'{"text":"\xff"}')

            completed = self.run_cli(request)

        expected = (SAMPLE / "expected/non-utf8-request-error.txt").read_text(
            encoding="utf-8"
        )
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(completed.stderr, expected)

    def test_parser_recursion_error_has_stable_validation_message(self):
        demo = self.require_demo()
        with TemporaryDirectory() as temp_dir:
            request = Path(temp_dir) / "parser-depth.json"
            request.write_text('{"text":"valid"}', encoding="utf-8")

            with patch.object(demo.json, "loads", side_effect=RecursionError):
                with self.assertRaises(demo.ValidationError) as caught:
                    demo.load_request(request)

        self.assertEqual(
            str(caught.exception),
            "request exceeds parser nesting capacity",
        )

    def test_cli_default_runs_root_composition_and_is_deterministic(self):
        expected = (SAMPLE / "expected/enhanced-contract-result.json").read_text(
            encoding="utf-8"
        )

        first = self.run_cli()
        second = self.run_cli()

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, expected)
        self.assertEqual(first.stderr, "")
        self.assertEqual(second.stdout, first.stdout)

    def test_root_skill_declares_automatic_harness_and_contract_boundary(self):
        text = (SAMPLE / "SKILL.md").read_text(encoding="utf-8")

        for phrase in (
            "Component",
            "ConcreteComponent",
            "Decorator",
            "ConcreteDecorator",
            "Agent Host and Agent Runtime are execution context",
            "python3 scripts/run_demo.py",
            "python3 -m unittest discover tests -v",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_contract_reference_and_child_skills_are_present(self):
        required = (
            "references/contract-review-component.md",
            "child-skills/base-contract-review/SKILL.md",
            "child-skills/privacy-check/SKILL.md",
            "child-skills/citation-check/SKILL.md",
            "child-skills/compliance-check/SKILL.md",
        )
        for relative_path in required:
            with self.subTest(path=relative_path):
                self.assertTrue((SAMPLE / relative_path).is_file())


if __name__ == "__main__":
    unittest.main()
