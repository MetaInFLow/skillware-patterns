#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import sys


DEFAULT_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures/valid/github.json"
TARGETS = ("github", "jira", "linear")
SEVERITIES = ("low", "medium", "high", "critical")
JIRA_PRIORITIES = {
    "low": "Low",
    "medium": "Medium",
    "high": "High",
    "critical": "Highest",
}
LINEAR_PRIORITIES = {
    "low": 4,
    "medium": 3,
    "high": 2,
    "critical": 1,
}


class ValidationError(ValueError):
    pass


def validate_request(request):
    if not isinstance(request, dict):
        raise ValidationError("request must be a JSON object")

    target = request.get("target")
    if target not in TARGETS:
        raise ValidationError("target must be one of: github, jira, linear")

    issue = request.get("issue")
    required_fields = ("id", "title", "description", "severity")
    if not isinstance(issue, dict) or any(
        not isinstance(issue.get(field), str) or not issue[field].strip()
        for field in required_fields
    ):
        raise ValidationError(
            "issue requires non-empty string fields: id, title, description, severity"
        )

    canonical = {field: issue[field] for field in required_fields}
    if canonical["severity"] not in SEVERITIES:
        raise ValidationError(
            "severity must be one of: low, medium, high, critical"
        )
    return target, canonical


def adapt_github(issue):
    return {
        "external_id": issue["id"],
        "title": issue["title"],
        "body": issue["description"],
        "labels": [f"severity:{issue['severity']}"],
    }


def adapt_jira(issue):
    return {
        "external_id": issue["id"],
        "summary": issue["title"],
        "description": issue["description"],
        "priority": {"name": JIRA_PRIORITIES[issue["severity"]]},
    }


def adapt_linear(issue):
    return {
        "external_id": issue["id"],
        "title": issue["title"],
        "description": issue["description"],
        "priority": LINEAR_PRIORITIES[issue["severity"]],
    }


ADAPTERS = {
    "github": adapt_github,
    "jira": adapt_jira,
    "linear": adapt_linear,
}


def publish_issue(request):
    target, canonical_issue = validate_request(request)
    return {
        "target": target,
        "payload": ADAPTERS[target](canonical_issue),
    }


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Run the standalone Multi-Tracker Issue Publisher sample."
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
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
