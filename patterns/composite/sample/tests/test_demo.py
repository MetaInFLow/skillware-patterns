import ast
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
from urllib.parse import urlparse


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
LEAF_SKILL_PATHS = (
    "child-skills/market-analysis/SKILL.md",
    "child-skills/financial-analysis/SKILL.md",
    "child-skills/competition-analysis/SKILL.md",
    "child-skills/risk-analysis/SKILL.md",
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
        self.assertTrue(section["id"].strip())
        self.assertIsInstance(section["title"], str)
        self.assertTrue(section["title"].strip())
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

    def test_each_injected_leaf_executor_runs_once_in_declared_order(self):
        workflow = self.load_json("fixtures/valid/investment-memo.json")
        expected = self.load_json("expected/investment-memo.json")
        expected_by_id = {child["id"]: child for child in expected["children"]}
        calls = []

        def recording_executor(skill_path):
            def execute(request):
                output = deepcopy(expected_by_id[request["id"]])
                calls.append(
                    {
                        "skill_key": skill_path,
                        "request": deepcopy(request),
                        "output": deepcopy(output),
                    }
                )
                return output

            return execute

        executors = {
            path: recording_executor(path) for path in LEAF_SKILL_PATHS
        }
        result = self.demo.build_memo(workflow, leaf_executors=executors)

        leaf_nodes = workflow["nodes"][1:]
        self.assertEqual(
            [call["request"] for call in calls],
            [
                {
                    "id": node["id"],
                    "title": node["title"],
                    "skill": node["skill"],
                    "input": node["input"],
                }
                for node in leaf_nodes
            ],
        )
        self.assertEqual(
            [call["skill_key"] for call in calls], list(LEAF_SKILL_PATHS)
        )
        self.assertEqual(
            [call["output"] for call in calls], expected["children"]
        )
        self.assertEqual(result, expected)

    def test_default_executors_are_keyed_to_each_child_skill(self):
        self.assertEqual(tuple(self.demo.DEFAULT_LEAF_EXECUTORS), LEAF_SKILL_PATHS)

    def test_leaf_executor_result_is_validated_before_composition(self):
        workflow = self.load_json("fixtures/valid/investment-memo.json")

        def invalid_executor(request):
            return {
                "id": request["id"],
                "title": request["title"],
                "content": "invalid",
                "evidence": [],
            }

        executors = dict(self.demo.DEFAULT_LEAF_EXECUTORS)
        executors[LEAF_SKILL_PATHS[0]] = invalid_executor
        with self.assertRaisesRegex(
            self.demo.ValidationError,
            "^section 'market-analysis' fields must be exactly: id, title, "
            "content, evidence, children; missing: children$",
        ):
            self.demo.build_memo(workflow, leaf_executors=executors)

    def test_injected_leaf_result_rejects_out_of_order_contract_keys(self):
        workflow = self.load_json("fixtures/valid/investment-memo.json")

        def out_of_order_executor(request):
            return {
                "title": request["title"],
                "id": request["id"],
                "content": "invalid order",
                "evidence": [],
                "children": [],
            }

        executors = dict(self.demo.DEFAULT_LEAF_EXECUTORS)
        executors[LEAF_SKILL_PATHS[0]] = out_of_order_executor
        with self.assertRaisesRegex(
            self.demo.ValidationError,
            "^section 'market-analysis' field order must be: id, title, "
            "content, evidence, children$",
        ):
            self.demo.build_memo(workflow, leaf_executors=executors)

    def test_self_referential_leaf_children_fail_without_recursive_descent(self):
        workflow = self.load_json("fixtures/valid/investment-memo.json")

        def self_referential_executor(request):
            section = {
                "id": request["id"],
                "title": request["title"],
                "content": "invalid child",
                "evidence": [],
                "children": [],
            }
            section["children"].append(section)
            return section

        executors = dict(self.demo.DEFAULT_LEAF_EXECUTORS)
        executors[LEAF_SKILL_PATHS[0]] = self_referential_executor
        with self.assertRaisesRegex(
            self.demo.ValidationError,
            r"^leaf executor for 'child-skills/market-analysis/SKILL.md' "
            r"must return children as \[\]$",
        ):
            self.demo.build_memo(workflow, leaf_executors=executors)

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

    def test_reordered_semantically_identical_workflow_input_is_accepted(self):
        source = self.load_json("fixtures/valid/investment-memo.json")
        reordered_nodes = []
        for node in source["nodes"]:
            reordered = {
                key: (
                    {
                        input_key: node["input"][input_key]
                        for input_key in reversed(tuple(node["input"]))
                    }
                    if key == "input"
                    else node[key]
                )
                for key in reversed(tuple(node))
            }
            reordered_nodes.append(reordered)
        workflow = {
            "nodes": reordered_nodes,
            "root": source["root"],
            "component_contract": source["component_contract"],
        }

        self.assertEqual(
            self.demo.build_memo(workflow),
            self.load_json("expected/investment-memo.json"),
        )

    def test_default_leaf_executor_accepts_reordered_request_fields(self):
        workflow = self.load_json("fixtures/valid/investment-memo.json")
        market = workflow["nodes"][1]
        request = {
            "input": {
                key: market["input"][key]
                for key in reversed(tuple(market["input"]))
            },
            "skill": market["skill"],
            "title": market["title"],
            "id": market["id"],
        }

        self.assertEqual(
            self.demo.execute_market_analysis(request),
            self.load_json("expected/investment-memo.json")["children"][0],
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

    def test_tree_validation_rejects_shared_repeated_and_unreachable_nodes(self):
        cases = (
            (
                "fixtures/invalid/shared-child.json",
                "node 'risk-analysis' must have exactly one parent; found 2: "
                "diligence-a, diligence-b",
            ),
            (
                "fixtures/invalid/repeated-child.json",
                "node 'investment-memo' repeats child 'market-analysis'",
            ),
            (
                "fixtures/invalid/unreachable-node.json",
                "unreachable nodes from root 'investment-memo': orphan-analysis",
            ),
            (
                "fixtures/invalid/root-has-parent.json",
                "root node 'investment-memo' must have zero parents; found 1: "
                "orphan-parent",
            ),
        )
        for fixture, message in cases:
            with self.subTest(fixture=fixture):
                with self.assertRaisesRegex(
                    self.demo.ValidationError, f"^{re.escape(message)}$"
                ):
                    self.demo.build_memo(self.load_json(fixture))

    def test_disconnected_cycle_is_detected_before_reachability(self):
        workflow = self.load_json("fixtures/invalid/disconnected-cycle.json")

        with self.assertRaisesRegex(
            self.demo.ValidationError,
            "^cycle detected: orphan-a -> orphan-b -> orphan-a$",
        ):
            self.demo.build_memo(workflow)

    def test_whole_tree_validation_runs_before_any_leaf_executor(self):
        workflow = self.load_json("fixtures/invalid/unreachable-node.json")
        calls = []

        def should_not_run(request):
            calls.append(request)
            return {}

        executors = {path: should_not_run for path in LEAF_SKILL_PATHS}
        with self.assertRaisesRegex(
            self.demo.ValidationError,
            "^unreachable nodes from root 'investment-memo': orphan-analysis$",
        ):
            self.demo.build_memo(workflow, leaf_executors=executors)
        self.assertEqual(calls, [])

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
                "nodes[1] fields must be exactly: id, kind, title, skill, "
                "input, children; missing: input",
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

    def test_contract_validator_rejects_empty_or_non_string_id_and_title(self):
        valid = {
            "id": "market-analysis",
            "title": "Market Analysis",
            "content": "Content",
            "evidence": [],
            "children": [],
        }
        cases = (
            ("id", "", "section.id must be a non-empty string"),
            ("id", 7, "section.id must be a non-empty string"),
            (
                "title",
                "   ",
                "section 'market-analysis'.title must be a non-empty string",
            ),
            (
                "title",
                ["Market"],
                "section 'market-analysis'.title must be a non-empty string",
            ),
        )
        for field, value, message in cases:
            with self.subTest(field=field, value=value):
                section = deepcopy(valid)
                section[field] = value
                with self.assertRaisesRegex(
                    self.demo.ValidationError, f"^{re.escape(message)}$"
                ):
                    self.demo.validate_section_record(section)

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
            (
                "fixtures/invalid/shared-child.json",
                "expected/shared-child-error.txt",
            ),
            (
                "fixtures/invalid/repeated-child.json",
                "expected/repeated-child-error.txt",
            ),
            (
                "fixtures/invalid/unreachable-node.json",
                "expected/unreachable-node-error.txt",
            ),
            (
                "fixtures/invalid/disconnected-cycle.json",
                "expected/disconnected-cycle-error.txt",
            ),
            (
                "fixtures/invalid/root-has-parent.json",
                "expected/root-has-parent-error.txt",
            ),
            ("fixtures/invalid/invalid-json.json", "expected/invalid-json-error.txt"),
        )
        for fixture, expectation in cases:
            with self.subTest(fixture=fixture):
                self.assert_cli_error(fixture, expectation)

    def test_participant_and_evidence_paths_resolve_locally(self):
        participant_map = (RECORD / "participant-map.yaml").read_text(
            encoding="utf-8"
        )

        for participant in ("Client", "Component", "Leaf", "Composite"):
            self.assertIn(f"  {participant}:\n", participant_map)
        self.assertIn("path: sample/references/section-contract.md", participant_map)
        leaf_paths = [
            "sample/child-skills/market-analysis/SKILL.md",
            "sample/child-skills/financial-analysis/SKILL.md",
            "sample/child-skills/competition-analysis/SKILL.md",
            "sample/child-skills/risk-analysis/SKILL.md",
        ]
        for leaf_path in leaf_paths:
            self.assertIn(f"- {leaf_path}", participant_map)
            self.assertTrue((RECORD / leaf_path).is_file())
        self.assertIn("  Agent Host:\n", participant_map)
        self.assertIn("  Agent Runtime:\n", participant_map)
        self.assertEqual(participant_map.count("evidence_status: not observable"), 2)
        evidence = re.search(
            r"^evidence_path: ([^\s]+)$", participant_map, flags=re.MULTILINE
        )
        self.assertIsNotNone(evidence)
        self.assertTrue((RECORD / evidence.group(1)).is_file())

    def test_openmontage_record_preserves_candidate_claim_boundary(self):
        evidence = (RECORD / "evidence/openmontage-frozen-case.md").read_text(
            encoding="utf-8"
        )
        correspondence = (RECORD / "correspondence.md").read_text(
            encoding="utf-8"
        )

        for required in (
            "db91727598d08d40919d7d68a47864a5467bd448",
            "pipeline_defs/animation.yaml",
            "skills/pipelines/animation/executive-producer.md",
            "skills/pipelines/animation/research-director.md",
            ".agents/skills/create-video/SKILL.md",
            "lib/pipeline_loader.py",
            "vendor/API guidance, not pipeline-stage evidence",
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

    def test_openmontage_evidence_urls_use_exact_public_pinned_paths(self):
        evidence = (RECORD / "evidence/openmontage-frozen-case.md").read_text(
            encoding="utf-8"
        )
        urls = re.findall(r"https://github\.com/[^)\s]+", evidence)
        expected_paths = {
            "pipeline_defs/animation.yaml",
            "skills/pipelines/animation/executive-producer.md",
            "skills/pipelines/animation/research-director.md",
            "lib/pipeline_loader.py",
            ".agents/skills/create-video/SKILL.md",
        }
        pinned_paths = set()

        for url in urls:
            parsed = urlparse(url)
            parts = parsed.path.strip("/").split("/")
            if len(parts) < 5 or parts[2] not in {"blob", "tree"}:
                continue
            owner, repository, _, revision = parts[:4]
            upstream_path = "/".join(parts[4:])
            with self.subTest(url=url):
                self.assertEqual(parsed.scheme, "https")
                self.assertEqual(parsed.netloc, "github.com")
                self.assertEqual((owner, repository), ("calesthio", "OpenMontage"))
                self.assertEqual(
                    revision, "db91727598d08d40919d7d68a47864a5467bd448"
                )
                self.assertIn(upstream_path, expected_paths)
            pinned_paths.add(upstream_path)

        self.assertEqual(pinned_paths, expected_paths)

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

        self.assertLessEqual(
            imports, {"argparse", "copy", "json", "pathlib", "sys"}
        )
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("patterns/", source)
        self.assertNotIn("../", source)
        self.assertNotIn("urllib", source)
        self.assertNotIn("requests", source)


if __name__ == "__main__":
    unittest.main()
