import ast
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest


SAMPLE = Path(__file__).resolve().parents[1]
RECORD = SAMPLE.parent
SCRIPT = SAMPLE / "scripts/run_demo.py"


def load_demo_module():
    spec = importlib.util.spec_from_file_location("facade_run_demo", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FacadeDemoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.demo = load_demo_module()

    def load_json(self, relative_path):
        return json.loads((SAMPLE / relative_path).read_text(encoding="utf-8"))

    def test_known_signal_returns_the_stable_contract_and_expected_result(self):
        request = self.load_json("fixtures/valid/incident.json")

        result = self.demo.respond_to_incident(request)

        self.assertEqual(
            list(result), ["summary", "impact", "actions", "communication"]
        )
        self.assertEqual(result, self.load_json("expected/incident-result.json"))
        self.assertNotIn("route", json.dumps(result))

    def test_unknown_signal_uses_the_declared_fallback(self):
        request = self.load_json("fixtures/invalid/unknown-signal.json")

        result = self.demo.respond_to_incident(request)

        self.assertEqual(result, self.load_json("expected/fallback-result.json"))
        self.assertEqual(result["actions"], ["request-human-triage"])
        self.assertEqual(
            list(result), ["summary", "impact", "actions", "communication"]
        )

    def test_facade_passes_context_and_prior_results_between_specialists(self):
        calls = []

        def diagnose(service, signal):
            calls.append(("diagnose", service, signal))
            return {"summary": "diagnosis", "actions": ["contain"]}

        def assess_impact(service, signal, diagnosis):
            calls.append(("assess-impact", service, signal, diagnosis))
            return {
                "statement": "assessed impact",
                "communication": "assessed impact is confirmed",
            }

        def draft_communication(service, signal, impact):
            calls.append(("draft-communication", service, signal, impact))
            return f"update from {impact['communication']}"

        result = self.demo.respond_to_incident(
            {"service": "orders-api", "signal": "5xx spike"},
            diagnose=diagnose,
            assess_impact=assess_impact,
            draft_communication=draft_communication,
        )

        diagnosis = {"summary": "diagnosis", "actions": ["contain"]}
        impact = {
            "statement": "assessed impact",
            "communication": "assessed impact is confirmed",
        }
        self.assertEqual(
            calls,
            [
                ("diagnose", "orders-api", "5xx spike"),
                ("assess-impact", "orders-api", "5xx spike", diagnosis),
                ("draft-communication", "orders-api", "5xx spike", impact),
            ],
        )
        self.assertEqual(
            result,
            {
                "summary": "diagnosis",
                "impact": "assessed impact",
                "actions": ["contain"],
                "communication": "update from assessed impact is confirmed",
            },
        )

    def test_second_service_has_no_checkout_leakage(self):
        result = self.demo.respond_to_incident(
            {"service": "inventory-api", "signal": "5xx spike"}
        )

        self.assertIn("inventory", result["impact"])
        self.assertNotIn("checkout", json.dumps(result).lower())

    def test_communication_uses_the_returned_impact_clause(self):
        communication = self.demo.draft_5xx_communication(
            "inventory-api",
            "5xx spike",
            {
                "statement": "Inventory requests are delayed.",
                "communication": "inventory impact is confirmed",
            },
        )

        self.assertEqual(
            communication,
            "Investigating elevated 5xx responses for inventory-api; "
            "inventory impact is confirmed.",
        )

    def test_missing_required_field_raises_clear_validation_error(self):
        request = self.load_json("fixtures/invalid/malformed-request.json")

        with self.assertRaisesRegex(
            self.demo.ValidationError, "service and signal are required"
        ):
            self.demo.respond_to_incident(request)

    def test_cli_exits_nonzero_for_a_malformed_request(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(SAMPLE / "fixtures/invalid/malformed-request.json"),
            ],
            cwd=SAMPLE,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("service and signal are required", completed.stderr)

    def test_participant_map_resolves_root_and_child_skills(self):
        participant_map = (RECORD / "participant-map.yaml").read_text(
            encoding="utf-8"
        )

        self.assertIn("role: Operator or task-level agent execution", participant_map)
        self.assertIn("  Facade:\n", participant_map)
        self.assertIn("path: sample/SKILL.md", participant_map)
        subsystem_paths = re.findall(
            r"^\s+- (sample/child-skills/[^\s]+/SKILL\.md)$",
            participant_map,
            flags=re.MULTILINE,
        )
        self.assertEqual(len(subsystem_paths), 3)
        for path in subsystem_paths:
            self.assertTrue((RECORD / path).is_file(), path)

    def test_demo_uses_only_the_standard_library_and_no_other_pattern(self):
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        imports = {
            node.names[0].name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
        }
        imports.update(
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        )

        self.assertLessEqual(imports, {"argparse", "json", "pathlib", "sys"})
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("patterns/", source)
        self.assertNotIn("../", source)


if __name__ == "__main__":
    unittest.main()
