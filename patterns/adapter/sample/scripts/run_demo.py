#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import sys


DEFAULT_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures/valid/github.json"
TARGETS = ("github", "jira", "linear")
SEVERITIES = ("low", "medium", "high", "critical")
REQUEST_FIELDS = ("target", "issue", "target_context")
ISSUE_FIELDS = ("id", "title", "description", "severity")
CONTEXT_FIELDS = {
    "github": ("owner", "repo"),
    "jira": ("project_key", "issue_type"),
    "linear": ("team_id",),
}
LINEAR_ISSUE_CREATE = """mutation IssueCreate($input: IssueCreateInput!) {
  issueCreate(input: $input) {
    success
    issue {
      id
      title
    }
  }
}"""


class ValidationError(ValueError):
    pass


def validate_exact_fields(value, expected_fields, label):
    expected = set(expected_fields)
    actual = set(value)
    missing = [field for field in expected_fields if field not in actual]
    unexpected = sorted(actual - expected)
    if not missing and not unexpected:
        return

    details = []
    if missing:
        details.append("missing: " + ", ".join(missing))
    if unexpected:
        details.append("unexpected: " + ", ".join(unexpected))
    raise ValidationError(
        f"{label} must be exactly: {', '.join(expected_fields)}; "
        + "; ".join(details)
    )


def validate_request(request):
    if not isinstance(request, dict):
        raise ValidationError("request must be a JSON object")
    validate_exact_fields(request, REQUEST_FIELDS, "request fields")

    target = request["target"]
    if target not in TARGETS:
        raise ValidationError("target must be one of: github, jira, linear")

    issue = request["issue"]
    if not isinstance(issue, dict):
        raise ValidationError("issue must be a JSON object")
    validate_exact_fields(issue, ISSUE_FIELDS, "issue fields")
    if any(
        not isinstance(issue[field], str) or not issue[field].strip()
        for field in ISSUE_FIELDS
    ):
        raise ValidationError(
            "issue fields must be non-empty strings: id, title, description, severity"
        )
    if issue["severity"] not in SEVERITIES:
        raise ValidationError(
            "severity must be one of: low, medium, high, critical"
        )

    context = request["target_context"]
    if not isinstance(context, dict):
        raise ValidationError(f"target_context for {target} must be a JSON object")
    expected_context = CONTEXT_FIELDS[target]
    validate_exact_fields(
        context,
        expected_context,
        f"target_context fields for {target}",
    )
    if any(
        not isinstance(context[field], str) or not context[field].strip()
        for field in expected_context
    ):
        raise ValidationError(
            f"target_context for {target} requires non-empty string fields: "
            + ", ".join(expected_context)
        )

    canonical_issue = {field: issue[field] for field in ISSUE_FIELDS}
    target_context = {field: context[field] for field in expected_context}
    return target, canonical_issue, target_context


def github_body(issue):
    return (
        f"{issue['description']}\n\n"
        f"<!-- skillware-source-id: {issue['id']} -->\n"
        f"<!-- skillware-severity: {issue['severity']} -->"
    )


def adapt_github(issue, context):
    return {
        "method": "POST",
        "path": f"/repos/{context['owner']}/{context['repo']}/issues",
        "headers": {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        "body": {
            "title": issue["title"],
            "body": github_body(issue),
            "labels": [f"skillware-severity-{issue['severity']}"],
        },
    }


def adf_paragraph(text):
    return {
        "type": "paragraph",
        "content": [{"type": "text", "text": text}],
    }


def adapt_jira(issue, context):
    return {
        "method": "POST",
        "path": "/rest/api/3/issue",
        "headers": {
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        "body": {
            "fields": {
                "project": {"key": context["project_key"]},
                "summary": issue["title"],
                "issuetype": {"id": context["issue_type"]},
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        adf_paragraph(issue["description"]),
                        adf_paragraph(f"Source ID: {issue['id']}"),
                        adf_paragraph(f"Severity: {issue['severity']}"),
                    ],
                },
                "labels": [
                    f"skillware-source-{issue['id']}",
                    f"skillware-severity-{issue['severity']}",
                ],
            }
        },
    }


def linear_description(issue):
    return (
        f"{issue['description']}\n\n"
        f"Source ID: {issue['id']}\n"
        f"Severity: {issue['severity']}"
    )


def adapt_linear(issue, context):
    return {
        "method": "POST",
        "url": "https://api.linear.app/graphql",
        "headers": {"Content-Type": "application/json"},
        "body": {
            "query": LINEAR_ISSUE_CREATE,
            "variables": {
                "input": {
                    "teamId": context["team_id"],
                    "title": issue["title"],
                    "description": linear_description(issue),
                }
            },
        },
    }


ADAPTERS = {
    "github": adapt_github,
    "jira": adapt_jira,
    "linear": adapt_linear,
}


def publish_issue(request):
    target, canonical_issue, target_context = validate_request(request)
    return {
        "target": target,
        "request": ADAPTERS[target](canonical_issue, target_context),
    }


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Build an offline tracker request descriptor."
    )
    parser.add_argument(
        "fixture",
        nargs="?",
        type=Path,
        default=DEFAULT_FIXTURE,
        help="JSON request fixture (defaults to the valid GitHub issue)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        request = json.loads(args.fixture.read_text(encoding="utf-8"))
        result = publish_issue(request)
    except json.JSONDecodeError:
        print("error: fixture must contain valid JSON", file=sys.stderr)
        return 2
    except (OSError, ValidationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
