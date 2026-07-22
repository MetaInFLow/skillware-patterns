import ast
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

import yaml


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
        participant_map = yaml.safe_load(
            (RECORD / "participant-map.yaml").read_text(encoding="utf-8")
        )

        self.assertEqual(
            participant_map["participants"]["Client"]["role"],
            "Operator or task-level agent execution",
        )
        self.assertEqual(
            participant_map["participants"]["Facade"]["path"],
            "sample/SKILL.md",
        )
        subsystem_paths = participant_map["participants"]["Subsystem"]["paths"]
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
