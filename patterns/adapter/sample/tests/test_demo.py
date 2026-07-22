import ast
from copy import deepcopy
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
TARGETS = ("github", "jira", "linear")


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

    def test_github_adapter_returns_exact_rest_request_descriptor(self):
        _, result = self.assert_fixture_result(
            "fixtures/valid/github.json", "expected/github-result.json"
        )

        self.assertEqual(result["request"]["method"], "POST")
        self.assertEqual(result["request"]["path"], "/repos/acme/payments/issues")
        self.assertEqual(
            result["request"]["headers"],
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        self.assertEqual(
            result["request"]["body"],
            {
                "title": "Checkout retries exhaust",
                "body": (
                    "Payment requests fail after retry budget is exhausted.\n\n"
                    "<!-- skillware-source-id: ISSUE-104 -->\n"
                    "<!-- skillware-severity: critical -->"
                ),
                "labels": ["skillware-severity-critical"],
            },
        )

    def test_jira_adapter_returns_exact_rest_v3_request_descriptor(self):
        _, result = self.assert_fixture_result(
            "fixtures/valid/jira.json", "expected/jira-result.json"
        )

        self.assertEqual(result["request"]["method"], "POST")
        self.assertEqual(result["request"]["path"], "/rest/api/3/issue")
        self.assertEqual(
            result["request"]["headers"],
            {"Accept": "application/json", "Content-Type": "application/json"},
        )
        self.assertEqual(
            result["request"]["body"]["fields"],
            {
                "project": {"key": "PAY"},
                "summary": "Checkout retries exhaust",
                "issuetype": {"id": "10001"},
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": (
                                        "Payment requests fail after retry budget "
                                        "is exhausted."
                                    ),
                                }
                            ],
                        },
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": "Source ID: ISSUE-104"}
                            ],
                        },
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": "Severity: critical"}
                            ],
                        },
                    ],
                },
                "labels": [
                    "skillware-source-ISSUE-104",
                    "skillware-severity-critical",
                ],
            },
        )

    def test_linear_adapter_returns_exact_graphql_request_descriptor(self):
        _, result = self.assert_fixture_result(
            "fixtures/valid/linear.json", "expected/linear-result.json"
        )

        self.assertEqual(result["request"]["method"], "POST")
        self.assertEqual(result["request"]["url"], "https://api.linear.app/graphql")
        self.assertEqual(
            result["request"]["body"]["variables"]["input"],
            {
                "teamId": "9cfb482a-81e3-4154-b5b9-2c805e70a02d",
                "title": "Checkout retries exhaust",
                "description": (
                    "Payment requests fail after retry budget is exhausted.\n\n"
                    "Source ID: ISSUE-104\nSeverity: critical"
                ),
            },
        )
        self.assertIn("issueCreate(input: $input)", result["request"]["body"]["query"])

    def test_target_context_drives_each_request_destination(self):
        github = self.demo.publish_issue(self.load_json("fixtures/valid/github.json"))
        jira = self.demo.publish_issue(self.load_json("fixtures/valid/jira.json"))
        linear = self.demo.publish_issue(self.load_json("fixtures/valid/linear.json"))

        self.assertEqual(github["request"]["path"], "/repos/acme/payments/issues")
        self.assertEqual(
            jira["request"]["body"]["fields"]["project"], {"key": "PAY"}
        )
        self.assertEqual(
            jira["request"]["body"]["fields"]["issuetype"], {"id": "10001"}
        )
        self.assertEqual(
            linear["request"]["body"]["variables"]["input"]["teamId"],
            "9cfb482a-81e3-4154-b5b9-2c805e70a02d",
        )

    def test_every_severity_and_identity_survive_every_request_descriptor(self):
        for severity in ("low", "medium", "high", "critical"):
            for target in TARGETS:
                with self.subTest(severity=severity, target=target):
                    source = self.load_json(f"fixtures/valid/{target}.json")
                    source["issue"]["severity"] = severity
                    result = self.demo.publish_issue(source)
                    serialized = json.dumps(result, sort_keys=True)
                    self.assertIn("ISSUE-104", serialized)
                    self.assertIn(severity, serialized)
                    self.assertNotIn('"priority"', serialized)

    def test_severity_is_preserved_without_priority_policy(self):
        for target in TARGETS:
            with self.subTest(target=target):
                result = self.demo.publish_issue(
                    self.load_json(f"fixtures/valid/{target}.json")
                )
                serialized = json.dumps(result)
                self.assertIn("critical", serialized)
                self.assertNotIn("priority", serialized)

    def test_publish_does_not_mutate_input(self):
        for target in TARGETS:
            with self.subTest(target=target):
                request = self.load_json(f"fixtures/valid/{target}.json")
                before = deepcopy(request)
                self.demo.publish_issue(request)
                self.assertEqual(request, before)

    def test_adapter_copies_canonical_strings_without_normalizing_identity(self):
        request = self.load_json("fixtures/valid/linear.json")
        request["issue"]["id"] = " ISSUE-104 "
        request["issue"]["title"] = " Checkout retries exhaust "
        request["issue"]["description"] = " Keep canonical spacing. "

        result = self.demo.publish_issue(request)
        linear_input = result["request"]["body"]["variables"]["input"]

        self.assertEqual(linear_input["title"], " Checkout retries exhaust ")
        self.assertIn(" Keep canonical spacing. ", linear_input["description"])
        self.assertIn("Source ID:  ISSUE-104 ", linear_input["description"])

    def assert_validation_error(self, fixture, message):
        request = self.load_json(f"fixtures/invalid/{fixture}")
        with self.assertRaisesRegex(self.demo.ValidationError, f"^{message}$"):
            self.demo.publish_issue(request)

    def test_unknown_target_is_rejected(self):
        self.assert_validation_error(
            "unknown-target.json", "target must be one of: github, jira, linear"
        )

    def test_malformed_issue_schema_is_rejected(self):
        self.assert_validation_error(
            "malformed-issue.json",
            "issue fields must be exactly: id, title, description, severity; missing: severity",
        )

    def test_extra_top_level_field_is_rejected(self):
        self.assert_validation_error(
            "extra-request-field.json",
            "request fields must be exactly: target, issue, target_context; unexpected: trace_id",
        )

    def test_extra_issue_field_is_rejected(self):
        self.assert_validation_error(
            "extra-issue-field.json",
            "issue fields must be exactly: id, title, description, severity; unexpected: reporter",
        )

    def test_missing_target_context_is_rejected(self):
        self.assert_validation_error(
            "missing-target-context.json",
            "request fields must be exactly: target, issue, target_context; missing: target_context",
        )

    def test_extra_target_context_field_is_rejected(self):
        self.assert_validation_error(
            "extra-target-context-field.json",
            "target_context fields for github must be exactly: owner, repo; unexpected: organization",
        )

    def test_missing_target_context_field_is_rejected(self):
        self.assert_validation_error(
            "missing-target-context-field.json",
            "target_context fields for jira must be exactly: project_key, issue_type; missing: issue_type",
        )

    def test_wrong_target_context_type_is_rejected(self):
        self.assert_validation_error(
            "wrong-target-context-type.json",
            "target_context for github must be a JSON object",
        )

    def test_blank_target_context_value_is_rejected(self):
        self.assert_validation_error(
            "blank-target-context-value.json",
            "target_context for github requires non-empty string fields: owner, repo",
        )

    def test_wrong_issue_field_type_is_rejected(self):
        self.assert_validation_error(
            "wrong-issue-field-type.json",
            "issue fields must be non-empty strings: id, title, description, severity",
        )

    def test_blank_issue_field_is_rejected(self):
        self.assert_validation_error(
            "blank-issue-field.json",
            "issue fields must be non-empty strings: id, title, description, severity",
        )

    def test_non_object_request_is_rejected(self):
        self.assert_validation_error(
            "non-object-request.json", "request must be a JSON object"
        )

    def test_unsupported_severity_is_rejected(self):
        self.assert_validation_error(
            "unsupported-severity.json",
            "severity must be one of: low, medium, high, critical",
        )

    def test_cli_defaults_to_github_fixture_and_prints_deterministic_json(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=SAMPLE,
            capture_output=True,
            text=True,
            check=False,
        )

        expected = self.load_json("expected/github-result.json")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout), expected)
        self.assertEqual(
            completed.stdout,
            json.dumps(expected, ensure_ascii=False, indent=2) + "\n",
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
        cases = (
            ("unknown-target.json", "unknown-target-error.txt"),
            ("malformed-issue.json", "malformed-issue-error.txt"),
            ("extra-request-field.json", "extra-request-field-error.txt"),
            ("extra-issue-field.json", "extra-issue-field-error.txt"),
            ("missing-target-context.json", "missing-target-context-error.txt"),
            (
                "extra-target-context-field.json",
                "extra-target-context-field-error.txt",
            ),
            (
                "missing-target-context-field.json",
                "missing-target-context-field-error.txt",
            ),
            ("wrong-target-context-type.json", "wrong-target-context-type-error.txt"),
            ("blank-target-context-value.json", "blank-target-context-value-error.txt"),
            ("wrong-issue-field-type.json", "wrong-issue-field-type-error.txt"),
            ("blank-issue-field.json", "blank-issue-field-error.txt"),
            ("non-object-request.json", "non-object-request-error.txt"),
            ("invalid-json.json", "invalid-json-error.txt"),
            ("unsupported-severity.json", "unsupported-severity-error.txt"),
        )
        for fixture, expectation in cases:
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
        participant_map = (RECORD / "participant-map.yaml").read_text(
            encoding="utf-8"
        )

        for participant in ("Client", "Target", "Adaptee", "Adapter"):
            self.assertIn(f"  {participant}:\n", participant_map)
        self.assertIn(
            "path: sample/references/tracker-contracts.md", participant_map
        )
        declared_paths = re.findall(
            r"^\s+(?:path|evidence_path): ([^\s]+)$",
            participant_map,
            flags=re.MULTILINE,
        )
        self.assertTrue(declared_paths)
        for declared_path in declared_paths:
            self.assertTrue((RECORD / declared_path).is_file(), declared_path)

    def test_tracker_contract_cites_official_vendor_documentation(self):
        reference = self.load_text("references/tracker-contracts.md")

        for required in (
            "https://docs.github.com/en/rest/issues/issues?apiVersion=2022-11-28#create-an-issue",
            "https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-post",
            "https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/",
            "https://linear.app/developers/graphql#creating-and-editing-issues",
        ):
            with self.subTest(required=required):
                self.assertIn(required, reference)

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
