from copy import deepcopy
import importlib.util
import inspect
import json
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


SAMPLE = Path(__file__).resolve().parents[1]
RECORD = SAMPLE.parent
DEMO_PATH = SAMPLE / "scripts/run_demo.py"


class TemplateMethodDemoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not DEMO_PATH.is_file():
            return
        spec = importlib.util.spec_from_file_location("template_method_demo", DEMO_PATH)
        cls.demo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.demo)

    def require_demo(self):
        self.assertTrue(DEMO_PATH.is_file(), "Template Method demo is not implemented")
        return self.demo

    def load_json(self, relative_path):
        return json.loads((SAMPLE / relative_path).read_text(encoding="utf-8"))

    def run_cli(self, *arguments):
        self.require_demo()
        return subprocess.run(
            [sys.executable, str(DEMO_PATH), *map(str, arguments)],
            cwd=SAMPLE,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

    def test_rfp_pipeline_preserves_required_stage_order(self):
        demo = self.require_demo()

        result = demo.run_rfp("healthcare")

        self.assertEqual(
            result["stages"],
            [
                "extract-requirements",
                "analyze-gaps",
                "apply-domain-hook",
                "draft-response",
                "quality-check",
            ],
        )
        self.assertEqual(result["domain"], "healthcare")

    def test_abstract_class_alone_cannot_run_without_concrete_static_hook(self):
        demo = self.require_demo()

        with self.assertRaisesRegex(
            demo.ValidationError,
            "^concrete_class must be a concrete RfpResponseTemplate ConcreteClass$",
        ):
            demo.run_template(
                demo.RfpResponseTemplate,
                demo.default_request("healthcare"),
            )

    def test_skeleton_owns_order_and_rejects_concrete_reordering(self):
        demo = self.require_demo()

        with self.assertRaisesRegex(
            TypeError,
            "^ConcreteClass may override only apply_domain_hook; forbidden override: run$",
        ):

            class ReorderedDomain(demo.RfpResponseTemplate):
                domain = "healthcare"

                def run(self):
                    return {"stages": list(reversed(demo.REQUIRED_STAGES))}

                @staticmethod
                def apply_domain_hook(hook_request):
                    return demo.healthcare_domain_hook(hook_request)

        with self.assertRaisesRegex(
            TypeError,
            (
                "^ConcreteClass may override only apply_domain_hook; forbidden override: "
                "_quality_check$"
            ),
        ):

            class SkipsQualityCheck(demo.RfpResponseTemplate):
                domain = "healthcare"

                @staticmethod
                def apply_domain_hook(hook_request):
                    return demo.healthcare_domain_hook(hook_request)

                def _quality_check(self, draft):
                    return {"passed": True, "checks": []}

    def test_domain_hook_is_invoked_exactly_once(self):
        demo = self.require_demo()
        calls = []

        class CountingHealthcare(demo.RfpResponseTemplate):
            domain = "healthcare"

            @staticmethod
            def apply_domain_hook(hook_request):
                calls.append(deepcopy(hook_request))
                return demo.healthcare_domain_hook(hook_request)

        result = demo.run_template(
            CountingHealthcare,
            demo.default_request("healthcare"),
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(result["stages"], list(demo.REQUIRED_STAGES))
        self.assertEqual(tuple(calls[0]), demo.HOOK_REQUEST_FIELDS)

    def test_hook_failure_propagates_and_stops_subsequent_stages(self):
        demo = self.require_demo()
        failure = RuntimeError("healthcare policy source unavailable")
        hook_calls = []

        class FailingHealthcare(demo.RfpResponseTemplate):
            domain = "healthcare"

            @staticmethod
            def apply_domain_hook(hook_request):
                hook_calls.append(deepcopy(hook_request))
                raise failure

        with self.assertRaises(RuntimeError) as caught:
            demo.run_template(
                FailingHealthcare,
                demo.default_request("healthcare"),
            )

        self.assertIs(caught.exception, failure)
        self.assertEqual(len(hook_calls), 1)

    def test_domain_concrete_classes_share_exact_hook_contract(self):
        demo = self.require_demo()

        for domain, concrete_class in demo.CONCRETE_CLASSES.items():
            with self.subTest(domain=domain):
                request = demo.default_request(domain)
                hook_request = demo.build_hook_request(request)
                descriptor = inspect.getattr_static(
                    concrete_class, "apply_domain_hook"
                )
                direct = descriptor.__func__(deepcopy(hook_request))
                validated = demo.validate_hook_result(direct, domain)
                result = demo.run_template(concrete_class, request)

                self.assertIsInstance(descriptor, staticmethod)
                self.assertEqual(
                    tuple(inspect.signature(descriptor.__func__).parameters),
                    ("hook_request",),
                )
                self.assertEqual(tuple(hook_request), demo.HOOK_REQUEST_FIELDS)
                self.assertEqual(tuple(validated), demo.HOOK_RESULT_FIELDS)
                self.assertEqual(result["domain_result"], validated)
                self.assertEqual(result["stages"], list(demo.REQUIRED_STAGES))

    def test_bounded_hook_substitution_changes_only_domain_result(self):
        demo = self.require_demo()

        class RuralHealthcare(demo.RfpResponseTemplate):
            domain = "healthcare"

            @staticmethod
            def apply_domain_hook(hook_request):
                demo.validate_hook_request(hook_request, "healthcare")
                return {
                    "domain": "healthcare",
                    "focus_areas": ["rural-care-continuity"],
                    "required_evidence": ["offline-workflow-plan"],
                }

        standard = demo.run_rfp("healthcare")
        rural = demo.run_template(
            RuralHealthcare,
            demo.default_request("healthcare"),
        )

        self.assertNotEqual(standard["domain_result"], rural["domain_result"])
        self.assertEqual(standard["stages"], rural["stages"])
        self.assertEqual(standard["quality"], rural["quality"])
        self.assertEqual(standard["requirement_ids"], rural["requirement_ids"])

    def test_mutating_hook_cannot_change_caller_or_mandatory_stage_data(self):
        demo = self.require_demo()
        request = demo.default_request("healthcare")
        original = deepcopy(request)

        class MutatingHealthcare(demo.RfpResponseTemplate):
            domain = "healthcare"

            @staticmethod
            def apply_domain_hook(hook_request):
                hook_request["requirements"].clear()
                hook_request["gaps"].append("injected-gap")
                return {
                    "domain": "healthcare",
                    "focus_areas": ["bounded-hook"],
                    "required_evidence": ["bounded-hook-evidence"],
                }

        result = demo.run_template(MutatingHealthcare, request)

        self.assertEqual(request, original)
        self.assertEqual(result["requirement_ids"], ["security", "continuity"])
        self.assertEqual(result["gaps"], [])

    def test_malformed_hook_results_are_rejected_before_draft(self):
        demo = self.require_demo()
        cases = (
            (
                None,
                "domain hook result must be a JSON object",
            ),
            (
                {"domain": "healthcare", "focus_areas": []},
                (
                    "domain hook result fields must be exactly: domain, focus_areas, "
                    "required_evidence; missing: required_evidence"
                ),
            ),
            (
                {
                    "domain": "finance",
                    "focus_areas": ["valid"],
                    "required_evidence": ["valid"],
                },
                "domain hook result domain mismatch: expected 'healthcare', found 'finance'",
            ),
            (
                {
                    "domain": "healthcare",
                    "focus_areas": "privacy",
                    "required_evidence": ["valid"],
                },
                "domain hook result.focus_areas must be a JSON array",
            ),
        )

        for hook_result, error in cases:
            with self.subTest(error=error):

                class InvalidHealthcare(demo.RfpResponseTemplate):
                    domain = "healthcare"

                    @staticmethod
                    def apply_domain_hook(hook_request):
                        return deepcopy(hook_result)

                with self.assertRaises(demo.HookContractError) as caught:
                    demo.run_template(
                        InvalidHealthcare,
                        demo.default_request("healthcare"),
                    )
                self.assertEqual(str(caught.exception), error)

    def test_public_api_ignores_multiple_inheritance_run_bypass(self):
        demo = self.require_demo()
        bypass_calls = []

        class BypassMixin:
            def run(self, request):
                bypass_calls.append(deepcopy(request))
                return {
                    "domain": "healthcare",
                    "stages": ["quality-check"],
                }

        class BypassHealthcare(BypassMixin, demo.RfpResponseTemplate):
            domain = "healthcare"

            @staticmethod
            def apply_domain_hook(hook_request):
                return demo.healthcare_domain_hook(hook_request)

        result = demo.run_template(
            BypassHealthcare,
            demo.default_request("healthcare"),
        )

        self.assertEqual(bypass_calls, [])
        self.assertEqual(result["domain"], "healthcare")
        self.assertEqual(result["stages"], list(demo.REQUIRED_STAGES))

    def test_hook_cannot_mutate_local_identity_domain_requirements_or_trace(self):
        demo = self.require_demo()
        request = demo.default_request("healthcare")
        original = deepcopy(request)

        class HostileHealthcare(demo.RfpResponseTemplate):
            domain = "healthcare"

            @staticmethod
            def apply_domain_hook(hook_request):
                hook_request["rfp_id"] = "forged-rfp"
                hook_request["domain"] = "finance"
                hook_request["requirements"].clear()
                hook_request["gaps"].extend(["forged-gap"])
                hook_request["stages"] = ["quality-check", "draft-response"]
                HostileHealthcare.domain = "finance"
                return {
                    "domain": "healthcare",
                    "focus_areas": ["bounded-hook"],
                    "required_evidence": ["bounded-hook-evidence"],
                }

        try:
            result = demo.run_template(HostileHealthcare, request)
        finally:
            HostileHealthcare.domain = "healthcare"

        self.assertEqual(request, original)
        self.assertEqual(result["rfp_id"], "rfp-healthcare-001")
        self.assertEqual(result["domain"], "healthcare")
        self.assertEqual(result["requirement_ids"], ["security", "continuity"])
        self.assertEqual(result["gaps"], [])
        self.assertEqual(result["stages"], list(demo.REQUIRED_STAGES))

    def test_hook_cannot_claim_skip_repeat_or_reordered_mandatory_stages(self):
        demo = self.require_demo()
        claims = (
            ("stages", ["quality-check", "draft-response"]),
            ("skip", ["quality-check"]),
            ("repeat", ["extract-requirements"]),
        )

        for claim_name, claim_value in claims:
            with self.subTest(claim=claim_name):

                class ClaimingHealthcare(demo.RfpResponseTemplate):
                    domain = "healthcare"

                    @staticmethod
                    def apply_domain_hook(hook_request):
                        result = demo.healthcare_domain_hook(hook_request)
                        result[claim_name] = claim_value
                        return result

                with self.assertRaises(demo.HookContractError) as caught:
                    demo.run_template(
                        ClaimingHealthcare,
                        demo.default_request("healthcare"),
                    )
                self.assertIn(f"unexpected: {claim_name}", str(caught.exception))

    def test_hook_has_no_instance_or_mandatory_step_capability(self):
        demo = self.require_demo()

        for name in (
            "_extract_requirements",
            "_analyze_gaps",
            "_draft_response",
            "_quality_check",
        ):
            with self.subTest(name=name):
                self.assertNotIn(name, demo.RfpResponseTemplate.__dict__)

        descriptor = inspect.getattr_static(
            demo.HealthcareRfpResponse, "apply_domain_hook"
        )
        self.assertIsInstance(descriptor, staticmethod)
        self.assertEqual(
            tuple(inspect.signature(descriptor.__func__).parameters),
            ("hook_request",),
        )

    def test_concrete_hook_must_be_static_with_exact_single_argument(self):
        demo = self.require_demo()

        class InstanceHook(demo.RfpResponseTemplate):
            domain = "healthcare"

            def apply_domain_hook(self, hook_request):
                return demo.healthcare_domain_hook(hook_request)

        class WrongSignatureHook(demo.RfpResponseTemplate):
            domain = "healthcare"

            @staticmethod
            def apply_domain_hook():
                return {}

        cases = (
            (
                InstanceHook,
                "ConcreteClass apply_domain_hook must be a concrete staticmethod",
            ),
            (
                WrongSignatureHook,
                "ConcreteClass apply_domain_hook must accept exactly hook_request",
            ),
        )
        for concrete_class, error in cases:
            with self.subTest(error=error):
                with self.assertRaises(demo.ValidationError) as caught:
                    demo.run_template(
                        concrete_class,
                        demo.default_request("healthcare"),
                    )
                self.assertEqual(str(caught.exception), error)

    def test_separately_addressed_domain_hook_validates_nested_input(self):
        demo = self.require_demo()
        valid = demo.build_hook_request(demo.default_request("healthcare"))
        cases = (
            (
                {
                    **valid,
                    "requirements": [
                        {"id": True, "text": "Valid text.", "mandatory": True}
                    ],
                },
                "domain hook request requirement.id must be a string",
            ),
            (
                {
                    **valid,
                    "gaps": ["not-a-requirement"],
                },
                "domain hook request.gaps must reference requirement ids",
            ),
        )

        for hook_request, error in cases:
            with self.subTest(error=error):
                with self.assertRaises(demo.HookContractError) as caught:
                    demo.healthcare_domain_hook(hook_request)
                self.assertEqual(str(caught.exception), error)

    def test_request_validation_is_strict_and_deterministic(self):
        demo = self.require_demo()
        valid = demo.default_request("healthcare")
        cases = (
            (None, "request must be a JSON object"),
            (
                {key: value for key, value in valid.items() if key != "requirements"},
                (
                    "request fields must be exactly: schema, rfp_id, domain, requirements; "
                    "missing: requirements"
                ),
            ),
            (
                {**valid, "extra": True},
                (
                    "request fields must be exactly: schema, rfp_id, domain, requirements; "
                    "unexpected: extra"
                ),
            ),
            ({**valid, "rfp_id": True}, "request.rfp_id must be a string"),
            ({**valid, "domain": "unknown"}, "unknown domain: unknown"),
            (
                {**valid, "requirements": "all"},
                "request.requirements must be a JSON array",
            ),
            (
                {**valid, "requirements": []},
                "request.requirements must contain at least one requirement",
            ),
            (
                {
                    **valid,
                    "requirements": [
                        {"id": "same", "text": "One", "mandatory": True},
                        {"id": "same", "text": "Two", "mandatory": False},
                    ],
                },
                "request.requirements ids must be unique: same",
            ),
            (
                {
                    **valid,
                    "requirements": [
                        {"id": "x", "text": "bad \ud800", "mandatory": True}
                    ],
                },
                "request must not contain lone Unicode surrogates",
            ),
        )

        for request, error in cases:
            with self.subTest(error=error):
                with self.assertRaises(demo.ValidationError) as caught:
                    demo.run_rfp_request(request)
                self.assertEqual(str(caught.exception), error)

    def test_programmatic_cycles_depth_and_non_string_keys_are_controlled(self):
        demo = self.require_demo()
        cyclic = demo.default_request("healthcare")
        cyclic["cycle"] = cyclic
        too_deep = demo.default_request("healthcare")
        nested = []
        too_deep["extra"] = nested
        for _ in range(demo.MAX_NESTING_DEPTH + 2):
            child = []
            nested.append(child)
            nested = child

        cases = (
            (cyclic, "request must not contain cyclic references"),
            (
                too_deep,
                f"request exceeds maximum nesting depth of {demo.MAX_NESTING_DEPTH}",
            ),
            ({1: "invalid"}, "request field names must be strings"),
        )
        for request, error in cases:
            with self.subTest(error=error):
                with self.assertRaises(demo.ValidationError) as caught:
                    demo.run_rfp_request(request)
                self.assertEqual(str(caught.exception), error)

    def test_result_validation_rejects_stage_or_domain_corruption(self):
        demo = self.require_demo()
        result = demo.run_rfp("healthcare")
        request = demo.default_request("healthcare")
        cases = (
            (
                {**result, "stages": list(reversed(result["stages"]))},
                "result.stages must equal the invariant Template Method order",
            ),
            (
                {**result, "domain": "finance"},
                "result.domain mismatch: expected 'healthcare', found 'finance'",
            ),
            (
                {**result, "quality": {"passed": "yes", "checks": []}},
                "result.quality.passed must be a boolean",
            ),
        )
        for candidate, error in cases:
            with self.subTest(error=error):
                with self.assertRaises(demo.ResultContractError) as caught:
                    demo.validate_result(candidate, request)
                self.assertEqual(str(caught.exception), error)

    def test_valid_fixtures_match_exact_expected_results(self):
        demo = self.require_demo()
        cases = ("healthcare-rfp", "finance-rfp")

        for name in cases:
            with self.subTest(name=name):
                request = demo.load_request(SAMPLE / f"fixtures/valid/{name}.json")
                result = demo.run_rfp_request(request)
                self.assertEqual(
                    result,
                    self.load_json(f"expected/{name}-result.json"),
                )

    def test_deterministic_reruns_do_not_mutate_or_alias_results(self):
        demo = self.require_demo()
        request = demo.default_request("healthcare")
        original = deepcopy(request)

        first = demo.run_rfp_request(request)
        first["stages"].reverse()
        first["domain_result"]["focus_areas"].append("caller-mutation")
        second = demo.run_rfp_request(request)
        third = demo.run_rfp("healthcare")

        self.assertEqual(request, original)
        self.assertEqual(second, third)
        self.assertEqual(second, self.load_json("expected/healthcare-rfp-result.json"))

    def test_invalid_fixtures_have_exact_stable_errors(self):
        self.require_demo()
        cases = (
            "malformed-request",
            "unknown-domain",
            "wrong-requirements-type",
            "duplicate-requirement-id",
            "invalid-json",
            "lone-surrogate",
            "duplicate-root-member",
            "duplicate-nested-member",
            "excessive-depth",
        )

        for name in cases:
            with self.subTest(name=name):
                completed = self.run_cli(SAMPLE / f"fixtures/invalid/{name}.json")
                expected = (SAMPLE / f"expected/{name}-error.txt").read_text(
                    encoding="utf-8"
                )
                self.assertEqual(completed.returncode, 2)
                self.assertEqual(completed.stdout, "")
                self.assertEqual(completed.stderr, expected)

    def test_invalid_utf8_and_parser_recursion_have_stable_errors(self):
        demo = self.require_demo()
        with TemporaryDirectory() as temp_dir:
            request = Path(temp_dir) / "non-utf8.json"
            request.write_bytes(b'{"domain":"\xff"}')
            completed = self.run_cli(request)

            parser_request = Path(temp_dir) / "parser.json"
            parser_request.write_text("{}", encoding="utf-8")
            with patch.object(demo.json, "loads", side_effect=RecursionError):
                with self.assertRaises(demo.ValidationError) as caught:
                    demo.load_request(parser_request)

        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(
            completed.stderr,
            (SAMPLE / "expected/non-utf8-request-error.txt").read_text(
                encoding="utf-8"
            ),
        )
        self.assertEqual(
            str(caught.exception),
            "request exceeds parser nesting capacity",
        )

    def test_cli_default_is_exact_and_deterministic(self):
        self.require_demo()
        expected = (SAMPLE / "expected/healthcare-rfp-result.json").read_text(
            encoding="utf-8"
        )

        first = self.run_cli()
        second = self.run_cli()

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, expected)
        self.assertEqual(first.stderr, "")
        self.assertEqual(second.stdout, first.stdout)

    def test_manifest_declares_invariant_order_and_bounded_hook(self):
        self.require_demo()
        manifest = (SAMPLE / "skillware.yaml").read_text(encoding="utf-8")
        order_block = """    order:
      - extract-requirements
      - analyze-gaps
      - apply-domain-hook
      - draft-response
      - quality-check
"""

        self.assertIn("  role: AbstractClass\n", manifest)
        self.assertIn(order_block, manifest)
        self.assertIn(
            "  overridable_operations:\n    - apply-domain-hook\n",
            manifest,
        )
        self.assertEqual(manifest.count("  - role: ConcreteClass\n"), 2)
        self.assertIn("    id: healthcare\n", manifest)
        self.assertIn("    id: finance\n", manifest)
        self.assertIn("hook_binding: staticmethod\n", manifest)
        self.assertIn(
            "template_dispatch: explicit-abstract-class-implementation\n",
            manifest,
        )

    def test_root_and_child_skills_declare_contract_and_automatic_harness(self):
        self.require_demo()
        root = (SAMPLE / "SKILL.md").read_text(encoding="utf-8")
        for phrase in (
            "AbstractClass",
            "ConcreteClass",
            "Agent Host and Agent Runtime are execution context",
            "apply-domain-hook",
            "python3 scripts/run_demo.py",
            "python3 -m unittest discover tests -v",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, root)

        for relative_path in (
            "references/rfp-domain-hook-contract.md",
            "child-skills/healthcare/SKILL.md",
            "child-skills/finance/SKILL.md",
        ):
            with self.subTest(path=relative_path):
                self.assertTrue((SAMPLE / relative_path).is_file())

    def test_record_uses_only_canonical_roles_and_pinned_candidate_evidence(self):
        self.require_demo()
        participant_map = (RECORD / "participant-map.yaml").read_text(
            encoding="utf-8"
        )
        participant_section = participant_map.split("participants:\n", 1)[1].split(
            "execution_context:\n", 1
        )[0]
        context_section = participant_map.split("execution_context:\n", 1)[1].split(
            "implementation_paths:\n", 1
        )[0]
        self.assertEqual(
            set(re.findall(r"^  ([A-Za-z]+):$", participant_section, re.MULTILINE)),
            {"AbstractClass", "ConcreteClass"},
        )
        self.assertEqual(
            set(re.findall(r"^  ([^:\n]+):$", context_section, re.MULTILINE)),
            {"Agent Host", "Agent Runtime"},
        )

        evidence = (RECORD / "evidence/superpowers-frozen-case.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "896224c4b1879920ab573417e68fd51d2ccc9072",
            "skills/brainstorming/SKILL.md",
            "skills/test-driven-development/SKILL.md",
            "candidate correspondence",
            "bounded domain hook",
            "ConcreteClass substitution",
            "Agent Runtime behavior",
            "unverified",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, evidence)


if __name__ == "__main__":
    unittest.main()
