import ast
from copy import deepcopy
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
    spec = importlib.util.spec_from_file_location("adapter_run_demo", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AdapterDemoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.demo = load_demo_module()

    def load_json(self, relative_path):
        return json.loads((SAMPLE / relative_path).read_text(encoding="utf-8"))

    def load_text(self, relative_path):
        return (SAMPLE / relative_path).read_text(encoding="utf-8")

    def assert_fixture_result(self, fixture, expected):
        request = self.load_json(fixture)
        result = self.demo.publish_issue(request)
        self.assertEqual(result, self.load_json(expected))
        return request, result

    def test_github_adapter_returns_exact_target_payload(self):
        _, result = self.assert_fixture_result(
            "fixtures/valid/github.json", "expected/github-result.json"
        )

        self.assertEqual(
            result,
            {
                "target": "github",
                "payload": {
                    "external_id": "ISSUE-104",
                    "title": "Checkout retries exhaust",
                    "body": "Payment requests fail after retry budget is exhausted.",
                    "labels": ["severity:critical"],
                },
            },
        )

    def test_jira_adapter_returns_exact_target_payload(self):
        _, result = self.assert_fixture_result(
            "fixtures/valid/jira.json", "expected/jira-result.json"
        )

        self.assertEqual(
            result,
            {
                "target": "jira",
                "payload": {
                    "external_id": "ISSUE-104",
                    "summary": "Checkout retries exhaust",
                    "description": "Payment requests fail after retry budget is exhausted.",
                    "priority": {"name": "Highest"},
                },
            },
        )

    def test_linear_adapter_returns_exact_target_payload(self):
        _, result = self.assert_fixture_result(
            "fixtures/valid/linear.json", "expected/linear-result.json"
        )

        self.assertEqual(
            result,
            {
                "target": "linear",
                "payload": {
                    "external_id": "ISSUE-104",
                    "title": "Checkout retries exhaust",
                    "description": "Payment requests fail after retry budget is exhausted.",
                    "priority": 1,
                },
            },
        )

    def test_all_adapters_preserve_identity_and_meaning(self):
        expected_descriptions = {
            "github": ("body", "Payment requests fail after retry budget is exhausted."),
            "jira": (
                "description",
                "Payment requests fail after retry budget is exhausted.",
            ),
            "linear": (
                "description",
                "Payment requests fail after retry budget is exhausted.",
            ),
        }
        severity_representations = {
            "github": ("labels", ["severity:critical"]),
            "jira": ("priority", {"name": "Highest"}),
            "linear": ("priority", 1),
        }

        for target in ("github", "jira", "linear"):
            with self.subTest(target=target):
                request = self.load_json(f"fixtures/valid/{target}.json")
                result = self.demo.publish_issue(request)
                payload = result["payload"]
                self.assertEqual(payload["external_id"], request["issue"]["id"])
                self.assertEqual(
                    payload["title" if target != "jira" else "summary"],
                    request["issue"]["title"],
                )
                description_field, description = expected_descriptions[target]
                self.assertEqual(payload[description_field], description)
                severity_field, severity = severity_representations[target]
                self.assertEqual(payload[severity_field], severity)

    def test_every_canonical_severity_has_an_exact_mapping_for_every_target(self):
        severity_mappings = {
            "low": {
                "github": ["severity:low"],
                "jira": {"name": "Low"},
                "linear": 4,
            },
            "medium": {
                "github": ["severity:medium"],
                "jira": {"name": "Medium"},
                "linear": 3,
            },
            "high": {
                "github": ["severity:high"],
                "jira": {"name": "High"},
                "linear": 2,
            },
            "critical": {
                "github": ["severity:critical"],
                "jira": {"name": "Highest"},
                "linear": 1,
            },
        }

        for severity, target_values in severity_mappings.items():
            for target, target_value in target_values.items():
                with self.subTest(severity=severity, target=target):
                    request = self.load_json("fixtures/valid/github.json")
                    request["target"] = target
                    request["issue"]["severity"] = severity
                    payload = self.demo.publish_issue(request)["payload"]
                    title_field = "summary" if target == "jira" else "title"
                    description_field = "body" if target == "github" else "description"
                    severity_field = "labels" if target == "github" else "priority"
                    self.assertEqual(
                        payload,
                        {
                            "external_id": "ISSUE-104",
                            title_field: "Checkout retries exhaust",
                            description_field: (
                                "Payment requests fail after retry budget is exhausted."
                            ),
                            severity_field: target_value,
                        },
                    )

    def test_publish_does_not_mutate_input(self):
        for target in ("github", "jira", "linear"):
            with self.subTest(target=target):
                request = self.load_json(f"fixtures/valid/{target}.json")
                before = deepcopy(request)
                self.demo.publish_issue(request)
                self.assertEqual(request, before)

    def test_adapter_copies_canonical_strings_without_normalizing_identity(self):
        request = self.load_json("fixtures/valid/github.json")
        request["issue"]["id"] = " ISSUE-104 "
        request["issue"]["title"] = " Checkout retries exhaust "
        request["issue"]["description"] = " Keep canonical spacing. "

        result = self.demo.publish_issue(request)

        self.assertEqual(result["payload"]["external_id"], " ISSUE-104 ")
        self.assertEqual(result["payload"]["title"], " Checkout retries exhaust ")
        self.assertEqual(result["payload"]["body"], " Keep canonical spacing. ")

    def test_unknown_target_is_rejected_clearly(self):
        request = self.load_json("fixtures/invalid/unknown-target.json")

        with self.assertRaisesRegex(
            self.demo.ValidationError,
            "target must be one of: github, jira, linear",
        ):
            self.demo.publish_issue(request)

    def test_malformed_issue_is_rejected_clearly(self):
        request = self.load_json("fixtures/invalid/malformed-issue.json")

        with self.assertRaisesRegex(
            self.demo.ValidationError,
            "issue requires non-empty string fields: id, title, description, severity",
        ):
            self.demo.publish_issue(request)

    def test_extra_top_level_field_is_rejected_clearly(self):
        request = self.load_json("fixtures/invalid/extra-request-field.json")

        with self.assertRaisesRegex(
            self.demo.ValidationError,
            "request fields must be exactly: target, issue; unexpected: trace_id",
        ):
            self.demo.publish_issue(request)

    def test_extra_issue_field_is_rejected_clearly(self):
        request = self.load_json("fixtures/invalid/extra-issue-field.json")

        with self.assertRaisesRegex(
            self.demo.ValidationError,
            "issue fields must be exactly: id, title, description, severity; unexpected: reporter",
        ):
            self.demo.publish_issue(request)

    def test_unsupported_severity_is_rejected_clearly(self):
        request = self.load_json("fixtures/valid/github.json")
        request["issue"]["severity"] = "urgent"

        with self.assertRaisesRegex(
            self.demo.ValidationError,
            "severity must be one of: low, medium, high, critical",
        ):
            self.demo.publish_issue(request)

    def test_severity_values_are_exact_not_case_normalized(self):
        request = self.load_json("fixtures/valid/github.json")
        request["issue"]["severity"] = "Critical"

        with self.assertRaisesRegex(
            self.demo.ValidationError,
            "severity must be one of: low, medium, high, critical",
        ):
            self.demo.publish_issue(request)

    def test_cli_defaults_to_github_fixture_and_prints_deterministic_json(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=SAMPLE,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            json.loads(completed.stdout), self.load_json("expected/github-result.json")
        )
        self.assertEqual(
            completed.stdout,
            json.dumps(
                self.load_json("expected/github-result.json"),
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
        )

    def test_cli_accepts_optional_fixture_path(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(SAMPLE / "fixtures/valid/linear.json"),
            ],
            cwd=SAMPLE,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            json.loads(completed.stdout), self.load_json("expected/linear-result.json")
        )

    def test_cli_errors_exactly_match_committed_expectations(self):
        for fixture, expectation in (
            ("unknown-target.json", "unknown-target-error.txt"),
            ("malformed-issue.json", "malformed-issue-error.txt"),
            ("extra-request-field.json", "extra-request-field-error.txt"),
            ("extra-issue-field.json", "extra-issue-field-error.txt"),
        ):
            with self.subTest(fixture=fixture):
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        str(SAMPLE / "fixtures/invalid" / fixture),
                    ],
                    cwd=SAMPLE,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertNotEqual(completed.returncode, 0)
                self.assertEqual(
                    completed.stderr,
                    self.load_text(f"expected/{expectation}"),
                )

    def test_participant_and_evidence_paths_resolve_locally(self):
        participant_map = yaml.safe_load(
            (RECORD / "participant-map.yaml").read_text(encoding="utf-8")
        )

        self.assertEqual(
            set(participant_map["participants"]),
            {"Client", "Target", "Adaptee", "Adapter"},
        )
        for implementation in participant_map["participants"]["Adapter"][
            "implementations"
        ]:
            self.assertTrue((RECORD / implementation["path"]).is_file())
        self.assertTrue((RECORD / participant_map["evidence_path"]).is_file())

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
