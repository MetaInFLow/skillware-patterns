import ast
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

import yaml


SAMPLE = Path(__file__).resolve().parents[1]
RECORD = SAMPLE.parent
SCRIPT = SAMPLE / "scripts/run_demo.py"
CONTRACT_KEYS = ("id", "title", "content", "evidence", "children")
LEAF_IDS = (
    "market-analysis",
    "financial-analysis",
    "competition-analysis",
    "risk-analysis",
)


def load_demo_module():
    spec = importlib.util.spec_from_file_location("composite_run_demo", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CompositeDemoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.demo = load_demo_module()

    def load_json(self, relative_path):
        return json.loads((SAMPLE / relative_path).read_text(encoding="utf-8"))

    def load_text(self, relative_path):
        return (SAMPLE / relative_path).read_text(encoding="utf-8")

    def assert_uniform_contract(self, section):
        self.assertEqual(tuple(section), CONTRACT_KEYS)
        self.assertIsInstance(section["id"], str)
        self.assertIsInstance(section["title"], str)
        self.assertIsInstance(section["content"], str)
        self.assertIsInstance(section["evidence"], list)
        self.assertTrue(
            all(isinstance(item, str) for item in section["evidence"])
        )
        self.assertIsInstance(section["children"], list)
        for child in section["children"]:
            self.assert_uniform_contract(child)

    def assert_cli_error(self, fixture, expectation):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), str(SAMPLE / fixture)],
            cwd=SAMPLE,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(completed.stderr, self.load_text(expectation))

    def test_leaf_and_composite_results_share_the_exact_contract(self):
        workflow = self.load_json("fixtures/valid/investment-memo.json")
        result = self.demo.build_memo(workflow)

        self.assert_uniform_contract(result)
        self.assertEqual(tuple(result), CONTRACT_KEYS)
        self.assertEqual(tuple(child["id"] for child in result["children"]), LEAF_IDS)
        for child in result["children"]:
            self.assertEqual(child["children"], [])

    def test_one_component_operation_invokes_a_leaf_or_composite(self):
        workflow = self.load_json("fixtures/valid/investment-memo.json")

        composite = self.demo.build_component(workflow, "investment-memo")
        leaf = self.demo.build_component(workflow, "market-analysis")

        self.assertEqual(tuple(composite), CONTRACT_KEYS)
        self.assertEqual(tuple(leaf), CONTRACT_KEYS)
        self.assertEqual(composite["id"], "investment-memo")
        self.assertEqual(leaf["id"], "market-analysis")
        self.assertEqual(leaf["children"], [])

    def test_root_assembles_all_four_leaves_in_declared_order(self):
        workflow = self.load_json("fixtures/valid/investment-memo.json")
        declared = workflow["nodes"][0]["children"]
        result = self.demo.build_memo(workflow)

        self.assertEqual(declared, list(LEAF_IDS))
        self.assertEqual(
            [child["id"] for child in result["children"]],
            list(LEAF_IDS),
        )

    def test_valid_fixture_matches_the_exact_expected_memo(self):
        workflow = self.load_json("fixtures/valid/investment-memo.json")

        self.assertEqual(
            self.demo.build_memo(workflow),
            self.load_json("expected/investment-memo.json"),
        )

    def test_recursive_builder_supports_a_nested_composite(self):
        workflow = self.load_json("fixtures/valid/investment-memo.json")
        workflow["root"] = "memo-package"
        workflow["nodes"].append(
            {
                "id": "memo-package",
                "kind": "composite",
                "title": "Investment Committee Package",
                "content": "Prepared package.",
                "evidence": ["fixture:package-request"],
                "children": ["investment-memo"],
            }
        )

        result = self.demo.build_memo(workflow)

        self.assertEqual(result["id"], "memo-package")
        self.assertEqual(result["children"][0]["id"], "investment-memo")
        self.assertEqual(
            [child["id"] for child in result["children"][0]["children"]],
            list(LEAF_IDS),
        )
        self.assert_uniform_contract(result)

    def test_builder_does_not_mutate_the_workflow(self):
        workflow = self.load_json("fixtures/valid/investment-memo.json")
        original = deepcopy(workflow)

        self.demo.build_memo(workflow)

        self.assertEqual(workflow, original)

    def test_cycle_error_includes_the_full_serialized_reference_path(self):
        workflow = self.load_json("fixtures/invalid/cycle.json")

        with self.assertRaisesRegex(
            self.demo.ValidationError,
            "^cycle detected: investment-memo -> due-diligence -> "
            "risk-analysis -> investment-memo$",
        ):
            self.demo.build_memo(workflow)

    def test_missing_child_and_missing_root_are_rejected(self):
        cases = (
            (
                "fixtures/invalid/missing-child.json",
                "node 'investment-memo' references missing child 'risk-analysis'",
            ),
            (
                "fixtures/invalid/missing-root.json",
                "root references missing node 'investment-memo'",
            ),
        )
        for fixture, message in cases:
            with self.subTest(fixture=fixture):
                with self.assertRaisesRegex(
                    self.demo.ValidationError, f"^{re.escape(message)}$"
                ):
                    self.demo.build_memo(self.load_json(fixture))

    def test_duplicate_node_id_is_rejected_before_registry_overwrite(self):
        workflow = self.load_json("fixtures/invalid/duplicate-id.json")

        with self.assertRaisesRegex(
            self.demo.ValidationError,
            r"^duplicate node id 'market-analysis' at nodes\[1\] and nodes\[2\]$",
        ):
            self.demo.build_memo(workflow)

    def test_invalid_kind_and_node_schema_are_rejected(self):
        cases = (
            (
                "fixtures/invalid/invalid-kind.json",
                "nodes[1].kind must be one of: leaf, composite",
            ),
            (
                "fixtures/invalid/malformed-node.json",
                "nodes[1] fields must be exactly: id, kind, title, content, "
                "evidence, children; missing: evidence",
            ),
            (
                "fixtures/invalid/leaf-with-children.json",
                "leaf node 'market-analysis' must declare children as []",
            ),
        )
        for fixture, message in cases:
            with self.subTest(fixture=fixture):
                with self.assertRaisesRegex(
                    self.demo.ValidationError, f"^{re.escape(message)}$"
                ):
                    self.demo.build_memo(self.load_json(fixture))

    def test_contract_validator_rejects_a_different_leaf_shape(self):
        malformed = {
            "id": "market-analysis",
            "title": "Market",
            "content": "Content",
            "evidence": ["fixture:market"],
        }

        with self.assertRaisesRegex(
            self.demo.ValidationError,
            "^section 'market-analysis' fields must be exactly: id, title, "
            "content, evidence, children; missing: children$",
        ):
            self.demo.validate_section_record(malformed)

    def test_cli_defaults_to_the_valid_workflow_and_prints_exact_json(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=SAMPLE,
            capture_output=True,
            text=True,
            check=False,
        )
        expected = self.load_json("expected/investment-memo.json")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout), expected)
        self.assertEqual(
            completed.stdout,
            json.dumps(expected, ensure_ascii=False, indent=2) + "\n",
        )

    def test_cli_accepts_an_optional_workflow_path(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(SAMPLE / "fixtures/valid/investment-memo.json"),
            ],
            cwd=SAMPLE,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            json.loads(completed.stdout),
            self.load_json("expected/investment-memo.json"),
        )

    def test_cli_errors_exactly_match_committed_expectations(self):
        cases = (
            ("fixtures/invalid/cycle.json", "expected/cycle-error.txt"),
            (
                "fixtures/invalid/missing-child.json",
                "expected/missing-child-error.txt",
            ),
            (
                "fixtures/invalid/missing-root.json",
                "expected/missing-root-error.txt",
            ),
            (
                "fixtures/invalid/duplicate-id.json",
                "expected/duplicate-id-error.txt",
            ),
            (
                "fixtures/invalid/malformed-node.json",
                "expected/malformed-node-error.txt",
            ),
            (
                "fixtures/invalid/invalid-kind.json",
                "expected/invalid-kind-error.txt",
            ),
            (
                "fixtures/invalid/leaf-with-children.json",
                "expected/leaf-with-children-error.txt",
            ),
            ("fixtures/invalid/invalid-json.json", "expected/invalid-json-error.txt"),
        )
        for fixture, expectation in cases:
            with self.subTest(fixture=fixture):
                self.assert_cli_error(fixture, expectation)

    def test_participant_and_evidence_paths_resolve_locally(self):
        participant_map = yaml.safe_load(
            (RECORD / "participant-map.yaml").read_text(encoding="utf-8")
        )

        self.assertEqual(
            set(participant_map["participants"]),
            {"Client", "Component", "Leaf", "Composite"},
        )
        self.assertEqual(
            participant_map["participants"]["Component"]["path"],
            "sample/references/section-contract.md",
        )
        self.assertEqual(
            participant_map["participants"]["Leaf"]["paths"],
            [
                "sample/child-skills/market-analysis/SKILL.md",
                "sample/child-skills/financial-analysis/SKILL.md",
                "sample/child-skills/competition-analysis/SKILL.md",
                "sample/child-skills/risk-analysis/SKILL.md",
            ],
        )
        self.assertEqual(
            set(participant_map["execution_context"]),
            {"Agent Host", "Agent Runtime"},
        )
        for role in participant_map["execution_context"].values():
            self.assertEqual(role["evidence_status"], "not observable")
            self.assertNotIn("path", role)
        self.assertTrue((RECORD / participant_map["evidence_path"]).is_file())

    def test_openmontage_record_preserves_candidate_claim_boundary(self):
        evidence = (RECORD / "evidence/openmontage-frozen-case.md").read_text(
            encoding="utf-8"
        )
        correspondence = (RECORD / "correspondence.md").read_text(
            encoding="utf-8"
        )

        for required in (
            "db91727598d08d40919d7d68a47864a5467bd448",
            ".agents/skills/create-video/SKILL.md",
            "AGENT_GUIDE.md",
            "lib/pipeline_loader.py",
            "candidate correspondence",
            "Missing or partial evidence",
        ):
            with self.subTest(required=required):
                self.assertIn(required, evidence)
        self.assertIn(
            "[frozen evidence](evidence/openmontage-frozen-case.md)",
            correspondence,
        )
        self.assertNotIn("confirmed correspondence", correspondence.lower())

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
        self.assertNotIn("urllib", source)
        self.assertNotIn("requests", source)


if __name__ == "__main__":
    unittest.main()
