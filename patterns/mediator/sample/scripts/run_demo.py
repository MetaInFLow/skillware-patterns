#!/usr/bin/env python3
import argparse
from collections.abc import Mapping
import json
from pathlib import Path
import stat
import sys


SAMPLE = Path(__file__).resolve().parents[1]
DEFAULT_WORKFLOW = SAMPLE / "fixtures/valid/release-ready.json"
PARTICIPANT_IDS = ("build", "security", "docs", "approval")
STATUS_VALUES = ("pass", "fail")
COMMUNICATION_PATH = "participants->mediator->release"
MAX_WORKFLOW_BYTES = 65_536


class CoordinationError(ValueError):
    pass


class DuplicateMemberError(ValueError):
    pass


def reject_duplicate_members(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateMemberError(key)
        result[key] = value
    return result


def reject_non_finite(_value):
    raise ValueError("non-finite number")


def exact_fields_error(subject, actual):
    expected = set(PARTICIPANT_IDS)
    missing = [item for item in PARTICIPANT_IDS if item not in actual]
    unexpected = sorted(set(actual) - expected)
    details = []
    if missing:
        details.append("missing: " + ", ".join(missing))
    if unexpected:
        details.append("unexpected: " + ", ".join(unexpected))
    return (
        f"{subject} must be exactly: {', '.join(PARTICIPANT_IDS)}; "
        + "; ".join(details)
    )


def validate_statuses(statuses):
    if not isinstance(statuses, Mapping):
        raise CoordinationError("statuses must be a mapping")
    field_names = tuple(statuses)
    if any(not isinstance(field, str) or not field for field in field_names):
        raise CoordinationError("statuses field names must be non-empty strings")
    if set(field_names) != set(PARTICIPANT_IDS):
        raise CoordinationError(exact_fields_error("statuses fields", field_names))

    copied = {}
    for participant_id in PARTICIPANT_IDS:
        status = statuses[participant_id]
        if not isinstance(status, str) or status not in STATUS_VALUES:
            raise CoordinationError(
                f"statuses.{participant_id} must be 'pass' or 'fail'"
            )
        copied[participant_id] = status
    return copied


class Mediator:
    @property
    def address(self):
        raise NotImplementedError

    def receive(self, colleague, status):
        raise NotImplementedError


class Colleague:
    def __init__(self, participant_id, skill_path, specialist=None):
        self.participant_id = participant_id
        self.skill_path = skill_path
        self._specialist = specialist if specialist is not None else lambda status: status
        if not callable(self._specialist):
            raise CoordinationError("colleague specialist must be callable")
        self._mediator = None

    @property
    def mediator_address(self):
        if self._mediator is None:
            return None
        return self._mediator.address

    def bind(self, mediator):
        if not isinstance(mediator, Mediator):
            raise CoordinationError("colleague mediator must implement Mediator")
        if self._mediator is not None and self._mediator is not mediator:
            raise CoordinationError(
                f"colleague {self.participant_id} is already bound to another mediator"
            )
        self._mediator = mediator

    def report(self, status):
        if self._mediator is None:
            raise CoordinationError(
                f"colleague {self.participant_id} is not bound to a mediator"
            )
        assessed_status = self._specialist(status)
        self._mediator.receive(self, assessed_status)


class DeploymentCoordinator(Mediator):
    def __init__(self, colleagues):
        try:
            supplied = tuple(colleagues)
        except TypeError as exc:
            raise CoordinationError("colleagues must be an iterable") from exc
        for colleague in supplied:
            if not isinstance(colleague, Colleague):
                raise CoordinationError(
                    "colleagues must contain only Colleague instances"
                )
        for colleague in supplied:
            if (
                not isinstance(colleague.participant_id, str)
                or not colleague.participant_id
            ):
                raise CoordinationError(
                    "colleague participant_id must be a non-empty string"
                )

        by_id = {}
        for colleague in supplied:
            if colleague.participant_id in by_id:
                raise CoordinationError(
                    f"duplicate colleague participant: {colleague.participant_id}"
                )
            by_id[colleague.participant_id] = colleague
        if set(by_id) != set(PARTICIPANT_IDS):
            raise CoordinationError(
                exact_fields_error("colleague participants", by_id)
            )

        ordered = tuple(by_id[participant_id] for participant_id in PARTICIPANT_IDS)
        for colleague in ordered:
            if colleague._mediator is not None:
                raise CoordinationError(
                    f"colleague {colleague.participant_id} is already bound to another mediator"
                )
        self._colleagues = ordered
        self._reports = {}
        self._active_colleague = None
        for colleague in self._colleagues:
            colleague.bind(self)

    @property
    def address(self):
        return "deployment-coordinator"

    def receive(self, colleague, status):
        if colleague is not self._active_colleague:
            raise CoordinationError("mediator received a report from an unaddressed colleague")
        participant_id = colleague.participant_id
        if participant_id in self._reports:
            raise CoordinationError(
                f"mediator received duplicate report from {participant_id}"
            )
        if not isinstance(status, str) or status not in STATUS_VALUES:
            raise CoordinationError(
                f"colleague {participant_id} returned an invalid status"
            )
        self._reports[participant_id] = status

    def coordinate(self, statuses):
        copied_statuses = validate_statuses(statuses)
        return self._coordinate_validated(copied_statuses)

    def _coordinate_validated(self, copied_statuses):
        self._reports = {}
        for colleague in self._colleagues:
            self._active_colleague = colleague
            try:
                colleague.report(copied_statuses[colleague.participant_id])
            except Exception:
                self._reports[colleague.participant_id] = "fail"
            finally:
                self._active_colleague = None

        ordered_reports = {
            participant_id: self._reports.get(participant_id, "fail")
            for participant_id in PARTICIPANT_IDS
        }
        decision = (
            "release"
            if all(status == "pass" for status in ordered_reports.values())
            else "blocked"
        )
        return {
            "decision": decision,
            "communication_path": COMMUNICATION_PATH,
            "statuses": ordered_reports,
        }


def default_colleagues():
    return [
        Colleague(
            participant_id,
            f"child-skills/{participant_id}/SKILL.md",
        )
        for participant_id in PARTICIPANT_IDS
    ]


def coordinate(statuses, colleagues=None):
    copied_statuses = validate_statuses(statuses)
    selected = default_colleagues() if colleagues is None else colleagues
    return DeploymentCoordinator(selected)._coordinate_validated(copied_statuses)


def validate_workflow(workflow):
    if not isinstance(workflow, dict):
        raise CoordinationError("workflow must be a JSON object")
    actual = set(workflow)
    if actual != {"statuses"}:
        details = []
        if "statuses" not in actual:
            details.append("missing: statuses")
        unexpected = sorted(actual - {"statuses"})
        if unexpected:
            details.append("unexpected: " + ", ".join(unexpected))
        raise CoordinationError(
            "workflow fields must be exactly: statuses; " + "; ".join(details)
        )
    validate_statuses(workflow["statuses"])
    return workflow


def run_workflow(workflow, colleagues=None):
    validate_workflow(workflow)
    return coordinate(workflow["statuses"], colleagues=colleagues)


def load_workflow(path):
    path = Path(path)
    if path.is_symlink():
        raise CoordinationError("workflow path must not be a symbolic link")
    try:
        metadata = path.stat()
    except FileNotFoundError as exc:
        raise CoordinationError("workflow file is missing") from exc
    except OSError as exc:
        raise CoordinationError(f"unable to inspect workflow: {exc}") from exc
    if not stat.S_ISREG(metadata.st_mode):
        raise CoordinationError("workflow path must be a regular file")
    try:
        with path.open("rb") as stream:
            raw = stream.read(MAX_WORKFLOW_BYTES + 1)
    except OSError as exc:
        raise CoordinationError(f"unable to read workflow: {exc}") from exc
    if len(raw) > MAX_WORKFLOW_BYTES:
        raise CoordinationError(
            f"workflow exceeds maximum size of {MAX_WORKFLOW_BYTES} bytes"
        )
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CoordinationError("workflow must be valid UTF-8") from exc
    try:
        workflow = json.loads(
            text,
            object_pairs_hook=reject_duplicate_members,
            parse_constant=reject_non_finite,
        )
    except DuplicateMemberError as exc:
        raise CoordinationError(
            f"workflow contains duplicate JSON object member: {exc.args[0]}"
        ) from exc
    except (json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise CoordinationError("workflow must be valid JSON") from exc
    return validate_workflow(workflow)


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Run the Deployment Coordinator demo.")
    parser.add_argument("workflow", nargs="?", type=Path, default=DEFAULT_WORKFLOW)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        result = run_workflow(load_workflow(args.workflow))
    except CoordinationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
