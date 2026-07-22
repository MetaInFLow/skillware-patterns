#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory, mkstemp


SAMPLE = Path(__file__).resolve().parents[1]
DEFAULT_WORKFLOW = SAMPLE / "fixtures/valid/vendor-onboarding.json"
STATE_SCHEMA = "vendor-onboarding-state-v1"
WORKFLOW_FIELDS = ("vendor_id", "persisted_state", "actions")
STATE_FIELDS = ("schema", "vendor_id", "state", "revision")


class WorkflowError(ValueError):
    pass


class ValidationError(WorkflowError):
    pass


class CorruptedStateError(WorkflowError):
    pass


class IllegalTransitionError(WorkflowError):
    pass


def require_non_empty_string(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{label} must be a non-empty string")


def validate_exact_fields(value, expected_fields, label, error_type=ValidationError):
    if not isinstance(value, dict):
        raise error_type(f"{label} must be a JSON object")
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
    raise error_type(
        f"{label} fields must be exactly: {', '.join(expected_fields)}; "
        + "; ".join(details)
    )


class State:
    name = ""
    allowed_actions = ()

    def handle(self, context, action):
        raise NotImplementedError

    def reject(self, action):
        allowed = ", ".join(self.allowed_actions) or "none"
        raise IllegalTransitionError(
            f"illegal transition: {self.name} -> {action}; allowed actions: {allowed}"
        )


class DraftState(State):
    name = "draft"
    allowed_actions = ("verify",)

    def handle(self, context, action):
        if action != "verify":
            self.reject(action)
        return context._commit(
            action,
            VerifiedState(),
            "Verification completed; evidence is ready for approval.",
        )


class VerifiedState(State):
    name = "verified"
    allowed_actions = ("approve",)

    def handle(self, context, action):
        if action != "approve":
            self.reject(action)
        return context._commit(
            action,
            ApprovedState(),
            "Approval recorded; the vendor is ready for activation.",
        )


class ApprovedState(State):
    name = "approved"
    allowed_actions = ("activate",)

    def handle(self, context, action):
        if action != "activate":
            self.reject(action)
        return context._commit(
            action,
            ActivatedState(),
            "Activation completed; the vendor is active.",
        )


class ActivatedState(State):
    name = "activated"
    allowed_actions = ()

    def handle(self, context, action):
        self.reject(action)


STATE_TYPES = {
    state_type.name: state_type
    for state_type in (DraftState, VerifiedState, ApprovedState, ActivatedState)
}
STATE_REVISIONS = {
    "draft": 0,
    "verified": 1,
    "approved": 2,
    "activated": 3,
}


class VendorWorkflow:
    """GoF Context that delegates legal-transition decisions to its State."""

    def __init__(self, path, vendor_id="vendor-acme"):
        require_non_empty_string(vendor_id, "vendor_id")
        self.path = Path(path)
        self.vendor_id = vendor_id
        if self.path.exists():
            self._reload()
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._state = DraftState()
            self._revision = 0
            self._write_record(self._state.name, self._revision)

    @property
    def state(self):
        return self._state.name

    @property
    def current_state(self):
        return self._state

    @property
    def revision(self):
        return self._revision

    @property
    def available_actions(self):
        return self._state.allowed_actions

    def transition(self, action):
        require_non_empty_string(action, "action")
        self._reload()
        return self._state.handle(self, action)

    def _commit(self, action, target_state, behavior):
        source_state = self._state.name
        target_revision = self._revision + 1
        self._write_record(target_state.name, target_revision)
        self._state = target_state
        self._revision = target_revision
        return {
            "action": action,
            "from": source_state,
            "to": target_state.name,
            "behavior": behavior,
            "revision": target_revision,
        }

    def _reload(self):
        record = self._read_record()
        self._state = STATE_TYPES[record["state"]]()
        self._revision = record["revision"]

    def _read_record(self):
        try:
            record = json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            raise CorruptedStateError(
                "corrupted state: state record is missing"
            ) from None
        except UnicodeError:
            raise CorruptedStateError("corrupted state: invalid UTF-8") from None
        except json.JSONDecodeError:
            raise CorruptedStateError("corrupted state: invalid JSON") from None
        except OSError:
            raise

        validate_exact_fields(
            record,
            STATE_FIELDS,
            "corrupted state",
            error_type=CorruptedStateError,
        )
        if record["schema"] != STATE_SCHEMA:
            raise CorruptedStateError(
                f"corrupted state: unsupported schema '{record['schema']}'"
            )
        persisted_vendor = record["vendor_id"]
        if not isinstance(persisted_vendor, str) or not persisted_vendor.strip():
            raise CorruptedStateError(
                "corrupted state: vendor_id must be a non-empty string"
            )
        if persisted_vendor != self.vendor_id:
            raise CorruptedStateError(
                "corrupted state: vendor_id mismatch; "
                f"expected '{self.vendor_id}', found '{persisted_vendor}'"
            )
        state_name = record["state"]
        if not isinstance(state_name, str):
            raise CorruptedStateError("corrupted state: state must be a string")
        if state_name not in STATE_TYPES:
            raise CorruptedStateError(
                f"corrupted state: unknown state '{state_name}'"
            )
        revision = record["revision"]
        if isinstance(revision, bool) or not isinstance(revision, int) or revision < 0:
            raise CorruptedStateError(
                "corrupted state: revision must be a non-negative integer"
            )
        expected_revision = STATE_REVISIONS[state_name]
        if revision != expected_revision:
            raise CorruptedStateError(
                f"corrupted state: revision {revision} is inconsistent with "
                f"state '{state_name}'"
            )
        return record

    def _write_record(self, state_name, revision):
        record = {
            "schema": STATE_SCHEMA,
            "vendor_id": self.vendor_id,
            "state": state_name,
            "revision": revision,
        }
        descriptor, temporary_name = mkstemp(
            prefix=f".{self.path.name}.",
            suffix=".tmp",
            dir=self.path.parent,
        )
        temporary_path = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                json.dump(record, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_path, self.path)
        except BaseException:
            temporary_path.unlink(missing_ok=True)
            raise


def validate_workflow(workflow):
    validate_exact_fields(workflow, WORKFLOW_FIELDS, "workflow")
    require_non_empty_string(workflow["vendor_id"], "workflow.vendor_id")
    persisted_state = workflow["persisted_state"]
    if persisted_state is not None and not isinstance(persisted_state, dict):
        raise ValidationError("workflow.persisted_state must be null or a JSON object")
    actions = workflow["actions"]
    if not isinstance(actions, list) or any(
        not isinstance(action, str) or not action.strip() for action in actions
    ):
        raise ValidationError(
            "workflow.actions must be a list of non-empty action strings"
        )
    return workflow


def run_vendor_workflow(workflow):
    validate_workflow(workflow)
    vendor_id = workflow["vendor_id"]
    with TemporaryDirectory() as temp_dir:
        state_path = Path(temp_dir) / "vendor-state.json"
        if workflow["persisted_state"] is not None:
            state_path.write_text(
                json.dumps(workflow["persisted_state"], ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
        context = VendorWorkflow(state_path, vendor_id=vendor_id)
        initial_state = context.state
        steps = [context.transition(action) for action in workflow["actions"]]
        recovered = VendorWorkflow(state_path, vendor_id=vendor_id)
        return {
            "vendor_id": vendor_id,
            "initial_state": initial_state,
            "steps": steps,
            "final_state": context.state,
            "recovered_state": recovered.state,
            "revision": recovered.revision,
        }


def load_workflow(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except UnicodeError:
        raise ValidationError("fixture is not valid UTF-8") from None
    except json.JSONDecodeError:
        raise ValidationError("fixture is not valid JSON") from None


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run the State vendor workflow demo.")
    parser.add_argument(
        "fixture",
        nargs="?",
        type=Path,
        default=DEFAULT_WORKFLOW,
        help="workflow fixture (default: fixtures/valid/vendor-onboarding.json)",
    )
    arguments = parser.parse_args(argv)
    try:
        result = run_vendor_workflow(load_workflow(arguments.fixture))
    except (WorkflowError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
