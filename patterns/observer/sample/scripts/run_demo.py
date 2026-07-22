#!/usr/bin/env python3
import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import sys


SAMPLE = Path(__file__).resolve().parents[1]
DEFAULT_WORKFLOW = SAMPLE / "fixtures/valid/release.json"
EVENT_TYPE = "release.published.v1"
OBSERVER_CONTRACT = "release-observer-v1"
WORKFLOW_FIELDS = (
    "event_type",
    "observer_contract",
    "release",
    "subscription_operations",
)
RELEASE_FIELDS = (
    "release_id",
    "version",
    "commit",
    "channel",
    "published_at",
    "notes",
)
EVENT_FIELDS = ("type",) + RELEASE_FIELDS
REGISTER_FIELDS = ("operation", "observer_id", "skill")
UNREGISTER_FIELDS = ("operation", "observer_id")
AUDIT_SKILL = "child-skills/audit/SKILL.md"
CHANGELOG_SKILL = "child-skills/changelog/SKILL.md"
TEAM_NOTIFICATION_SKILL = "child-skills/team-notification/SKILL.md"
VERSION_PATTERN = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z.-]+)?$"
)
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{7,40}$")
PUBLISHED_AT_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class ValidationError(ValueError):
    pass


class PublicationReentryError(RuntimeError):
    pass


def validate_exact_fields(value, expected_fields, label):
    if not isinstance(value, dict):
        raise ValidationError(f"{label} must be a JSON object")
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
        f"{label} fields must be exactly: {', '.join(expected_fields)}; "
        + "; ".join(details)
    )


def require_non_empty_string(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{label} must be a non-empty string")


def validate_release(release):
    validate_exact_fields(release, RELEASE_FIELDS, "release")
    for field in RELEASE_FIELDS[:-1]:
        require_non_empty_string(release[field], f"release.{field}")
    if not VERSION_PATTERN.fullmatch(release["version"]):
        raise ValidationError("release.version must be a semantic version")
    if not COMMIT_PATTERN.fullmatch(release["commit"]):
        raise ValidationError("release.commit must contain 7 to 40 lowercase hex characters")
    if release["channel"] not in {"stable", "beta", "canary"}:
        raise ValidationError("release.channel must be one of: stable, beta, canary")
    if not PUBLISHED_AT_PATTERN.fullmatch(release["published_at"]):
        raise ValidationError("release.published_at must be an RFC 3339 UTC timestamp")
    if not isinstance(release["notes"], list) or not release["notes"] or any(
        not isinstance(note, str) or not note.strip() for note in release["notes"]
    ):
        raise ValidationError("release.notes must be a non-empty list of non-empty strings")
    return release


def build_release_event(release):
    validate_release(release)
    event = {"type": EVENT_TYPE}
    event.update({field: deepcopy(release[field]) for field in RELEASE_FIELDS})
    return event


def update_audit(event):
    validate_event(event)
    return f"audit:{event['release_id']}"


def update_changelog(event):
    validate_event(event)
    return f"changelog:{event['version']}"


def update_team_notification(event):
    validate_event(event)
    return f"team-notification:{event['channel']}:{event['version']}"


DEFAULT_OBSERVER_UPDATES = {
    AUDIT_SKILL: update_audit,
    CHANGELOG_SKILL: update_changelog,
    TEAM_NOTIFICATION_SKILL: update_team_notification,
}


def validate_event(event):
    validate_exact_fields(event, EVENT_FIELDS, "release event")
    if tuple(event) != EVENT_FIELDS:
        raise ValidationError(
            "release event field order must be: " + ", ".join(EVENT_FIELDS)
        )
    if event["type"] != EVENT_TYPE:
        raise ValidationError(f"release event type must be '{EVENT_TYPE}'")
    validate_release({field: event[field] for field in RELEASE_FIELDS})
    return event


class ReleaseSubject:
    def __init__(self):
        self._registrations = {}
        self._publishing = False

    @property
    def registered_observer_ids(self):
        return tuple(self._registrations)

    def register(self, observer_id, skill, update):
        if self._publishing:
            raise ValidationError("subscription changes are not allowed during publication")
        require_non_empty_string(observer_id, "observer_id")
        require_non_empty_string(skill, "observer skill")
        if not callable(update):
            raise ValidationError(f"observer '{observer_id}' update must be callable")
        if observer_id in self._registrations:
            raise ValidationError(f"observer '{observer_id}' is already registered")
        self._registrations[observer_id] = {"skill": skill, "update": update}

    def unregister(self, observer_id):
        if self._publishing:
            raise ValidationError("subscription changes are not allowed during publication")
        require_non_empty_string(observer_id, "observer_id")
        if observer_id not in self._registrations:
            raise ValidationError(f"observer '{observer_id}' is not registered")
        del self._registrations[observer_id]

    def publish(self, release):
        if self._publishing:
            raise PublicationReentryError("publication re-entry is not allowed")
        event = build_release_event(release)
        deliveries = []
        self._publishing = True
        try:
            for observer_id, registration in tuple(self._registrations.items()):
                try:
                    receipt = registration["update"](deepcopy(event))
                    require_non_empty_string(
                        receipt, f"observer '{observer_id}' receipt"
                    )
                    status = "delivered"
                    error = None
                except Exception as exc:
                    receipt = None
                    status = "failed"
                    error = str(exc) or exc.__class__.__name__
                deliveries.append(
                    {
                        "observer_id": observer_id,
                        "skill": registration["skill"],
                        "status": status,
                        "receipt": receipt,
                        "error": error,
                    }
                )
        finally:
            self._publishing = False

        delivered = sum(item["status"] == "delivered" for item in deliveries)
        return {
            "event": event,
            "deliveries": deliveries,
            "summary": {
                "attempted": len(deliveries),
                "delivered": delivered,
                "failed": len(deliveries) - delivered,
            },
        }


def validate_workflow(workflow):
    validate_exact_fields(workflow, WORKFLOW_FIELDS, "workflow")
    if workflow["event_type"] != EVENT_TYPE:
        raise ValidationError(f"event_type must be '{EVENT_TYPE}'")
    if workflow["observer_contract"] != OBSERVER_CONTRACT:
        raise ValidationError(f"observer_contract must be '{OBSERVER_CONTRACT}'")
    validate_release(workflow["release"])
    operations = workflow["subscription_operations"]
    if not isinstance(operations, list):
        raise ValidationError("subscription_operations must be a list")
    for index, operation in enumerate(operations):
        label = f"subscription_operations[{index}]"
        if not isinstance(operation, dict):
            raise ValidationError(f"{label} must be a JSON object")
        kind = operation.get("operation")
        if kind == "register":
            validate_exact_fields(operation, REGISTER_FIELDS, label)
            require_non_empty_string(operation["observer_id"], f"{label}.observer_id")
            require_non_empty_string(operation["skill"], f"{label}.skill")
        elif kind == "unregister":
            validate_exact_fields(operation, UNREGISTER_FIELDS, label)
            require_non_empty_string(operation["observer_id"], f"{label}.observer_id")
        else:
            raise ValidationError(f"{label}.operation must be one of: register, unregister")
    return workflow


def run_release_workflow(workflow, observer_updates=None):
    validate_workflow(workflow)
    updates = DEFAULT_OBSERVER_UPDATES if observer_updates is None else observer_updates
    subject = ReleaseSubject()
    for operation in workflow["subscription_operations"]:
        observer_id = operation["observer_id"]
        if operation["operation"] == "unregister":
            subject.unregister(observer_id)
            continue
        skill = operation["skill"]
        update = updates.get(skill)
        if not callable(update):
            raise ValidationError(f"no observer update registered for skill '{skill}'")
        subject.register(observer_id, skill, update)
    return subject.publish(deepcopy(workflow["release"]))


def publish_release(version, observers):
    release = {
        "release_id": f"release-{version}",
        "version": version,
        "commit": "0000000",
        "channel": "stable",
        "published_at": "2000-01-01T00:00:00Z",
        "notes": ["Programmatic publication."],
    }
    subject = ReleaseSubject()
    for observer in observers:
        observer_id = getattr(observer, "observer_id", None) or getattr(
            observer, "__name__", ""
        )
        subject.register(observer_id, f"injected:{observer_id}", observer)
    result = subject.publish(release)
    return {
        delivery["observer_id"]: delivery["status"]
        for delivery in result["deliveries"]
    }


def load_workflow(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"workflow file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        try:
            display_path = path.relative_to(SAMPLE)
        except ValueError:
            display_path = path
        raise ValidationError(
            f"invalid JSON in {display_path}: {exc.msg} at line {exc.lineno} "
            f"column {exc.colno}"
        ) from exc


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Run the Observer release sample.")
    parser.add_argument("workflow", nargs="?", default=str(DEFAULT_WORKFLOW))
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    workflow_path = Path(args.workflow)
    if not workflow_path.is_absolute():
        workflow_path = SAMPLE / workflow_path
    try:
        result = run_release_workflow(load_workflow(workflow_path))
    except (OSError, UnicodeError, ValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
