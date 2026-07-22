#!/usr/bin/env python3
import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import sys


SAMPLE = Path(__file__).resolve().parents[1]
DEFAULT_REQUEST = SAMPLE / "fixtures/valid/enhanced-contract.json"
COMPONENT_CONTRACT = "contract-review-v1"
REQUEST_FIELDS = ("text",)
RESULT_FIELDS = ("summary", "findings")
FINDING_FIELDS = ("type", "message")
DECORATOR_IDS = ("privacy-check", "citation-check", "compliance-check")
MAX_TEXT_CHARACTERS = 10_000
MAX_SUMMARY_CHARACTERS = 500
MAX_FINDING_FIELD_CHARACTERS = 200
MAX_NESTING_DEPTH = 64
BASE_SUMMARY = "Base contract review completed."
EMAIL_PATTERN = re.compile(
    r"(?<![A-Za-z0-9.!#$%&'*+/=?^_`{|}~-])"
    r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+"
    r"(?![A-Za-z0-9-])"
)


class ValidationError(ValueError):
    pass


class ComponentContractError(ValueError):
    pass


class DuplicateMemberError(ValueError):
    pass


def validate_exact_fields(value, fields, label, error_type=ValidationError):
    if not isinstance(value, dict):
        raise error_type(f"{label} must be a JSON object")
    if any(not isinstance(key, str) for key in value):
        raise error_type(f"{label} field names must be strings")
    expected = set(fields)
    actual = set(value)
    missing = [field for field in fields if field not in actual]
    unexpected = sorted(actual - expected)
    if not missing and not unexpected:
        return
    details = []
    if missing:
        details.append("missing: " + ", ".join(missing))
    if unexpected:
        details.append("unexpected: " + ", ".join(unexpected))
    raise error_type(
        f"{label} fields must be exactly: {', '.join(fields)}; "
        + "; ".join(details)
    )


def validate_structure(value, label, error_type=ValidationError):
    active_container_ids = set()
    stack = [("enter", value, 0)]

    while stack:
        action, current, depth = stack.pop()
        if action == "exit":
            active_container_ids.remove(id(current))
            continue
        if isinstance(current, str):
            if any(
                0xD800 <= ord(character) <= 0xDFFF for character in current
            ):
                raise error_type(
                    f"{label} must not contain lone Unicode surrogates"
                )
            continue
        if not isinstance(current, (dict, list, tuple)):
            continue
        if depth > MAX_NESTING_DEPTH:
            raise error_type(
                f"{label} exceeds maximum nesting depth of {MAX_NESTING_DEPTH}"
            )

        identity = id(current)
        if identity in active_container_ids:
            raise error_type(f"{label} must not contain cyclic references")
        active_container_ids.add(identity)
        stack.append(("exit", current, depth))

        if isinstance(current, dict):
            children = []
            for key, item in current.items():
                children.extend((key, item))
        else:
            children = list(current)
        for child in reversed(children):
            stack.append(("enter", child, depth + 1))


def require_bounded_string(
    value,
    label,
    maximum,
    error_type,
    empty_message=None,
):
    if not isinstance(value, str):
        raise error_type(f"{label} must be a string")
    if not value.strip():
        raise error_type(empty_message or f"{label} must be non-empty")
    if len(value) > maximum:
        raise error_type(f"{label} must contain at most {maximum} characters")


def validate_request(request):
    validate_structure(request, "request")
    validate_exact_fields(request, REQUEST_FIELDS, "request")
    require_bounded_string(
        request["text"],
        "request.text",
        MAX_TEXT_CHARACTERS,
        ValidationError,
    )
    return {"text": request["text"]}


def validate_result(result, label="result"):
    error_type = ComponentContractError
    validate_structure(result, label, error_type)
    validate_exact_fields(result, RESULT_FIELDS, label, error_type)
    require_bounded_string(
        result["summary"],
        f"{label}.summary",
        MAX_SUMMARY_CHARACTERS,
        error_type,
    )
    findings = result["findings"]
    if not isinstance(findings, list):
        raise error_type(f"{label}.findings must be a JSON array")

    canonical_findings = []
    identities = set()
    for item in findings:
        item_label = "component finding" if label == "component result" else "finding"
        validate_exact_fields(item, FINDING_FIELDS, item_label, error_type)
        for field in FINDING_FIELDS:
            require_bounded_string(
                item[field],
                f"{item_label}.{field}",
                MAX_FINDING_FIELD_CHARACTERS,
                error_type,
            )
        canonical = {field: deepcopy(item[field]) for field in FINDING_FIELDS}
        identity = (canonical["type"], canonical["message"])
        if identity in identities:
            raise error_type(
                f"{label} findings must have unique (type, message) identity: "
                f"{identity[0]} | {identity[1]}"
            )
        identities.add(identity)
        canonical_findings.append(canonical)

    return {
        "summary": deepcopy(result["summary"]),
        "findings": canonical_findings,
    }


def base_review(contract):
    """ConcreteComponent for the compact contract-review-v1 interface."""
    validate_request(contract)
    return {"summary": BASE_SUMMARY, "findings": []}


def _decorate(component, finding_type, finding_message, predicate):
    if not callable(component):
        raise ComponentContractError("wrapped component must be callable")

    def wrapped(contract):
        request = validate_request(contract)
        component_result = component(deepcopy(request))
        result = validate_result(component_result, label="component result")
        added_finding = {"type": finding_type, "message": finding_message}
        added_identity = (finding_type, finding_message)
        existing_identities = {
            (item["type"], item["message"]) for item in result["findings"]
        }
        if predicate(request["text"]) and added_identity not in existing_identities:
            result["findings"].append(added_finding)
        return validate_result(result)

    wrapped.__name__ = f"with_{finding_type}_check_component"
    return wrapped


def with_privacy_check(component):
    """Wrap a Component and add one privacy finding after delegation."""
    return _decorate(
        component,
        "privacy",
        "Email address detected.",
        lambda text: EMAIL_PATTERN.search(text) is not None,
    )


def with_citation_check(component):
    """Wrap a Component and add one citation finding after delegation."""
    return _decorate(
        component,
        "citation",
        "Missing citation marker detected.",
        lambda text: "[missing]" in text,
    )


def with_compliance_check(component):
    """Wrap a Component and add one optional compliance finding."""
    return _decorate(
        component,
        "compliance",
        "Compliance exception marker detected.",
        lambda text: "[noncompliant]" in text,
    )


DECORATORS = {
    "privacy-check": with_privacy_check,
    "citation-check": with_citation_check,
    "compliance-check": with_compliance_check,
    "privacy": with_privacy_check,
    "citation": with_citation_check,
    "compliance": with_compliance_check,
}


def compose_review(
    decorator_ids=("privacy-check", "citation-check"),
    component=base_review,
):
    if (
        not isinstance(decorator_ids, (list, tuple))
        or isinstance(decorator_ids, str)
        or any(not isinstance(item, str) for item in decorator_ids)
    ):
        raise ValidationError("decorator ids must be an array of strings")
    if not callable(component):
        raise ComponentContractError("wrapped component must be callable")

    composed = component
    for decorator_id in decorator_ids:
        if decorator_id not in DECORATORS:
            raise ValidationError(f"unknown decorator id: {decorator_id}")
        composed = DECORATORS[decorator_id](composed)
    return composed


def reject_duplicate_members(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateMemberError(key)
        result[key] = value
    return result


def load_request(path):
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise ValidationError(f"unable to read request: {exc}") from exc
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationError("request must be valid UTF-8") from exc
    try:
        request = json.loads(text, object_pairs_hook=reject_duplicate_members)
    except DuplicateMemberError as exc:
        raise ValidationError(
            f"request contains duplicate JSON object member: {exc.args[0]}"
        ) from exc
    except RecursionError as exc:
        raise ValidationError("request exceeds parser nesting capacity") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError("request must be valid JSON") from exc
    return validate_request(request)


def parse_decorators(value):
    decorator_ids = value.split(",") if value else []
    return tuple(decorator_ids)


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Run contract-review decorators")
    parser.add_argument("request", nargs="?", type=Path, default=DEFAULT_REQUEST)
    parser.add_argument(
        "--decorators",
        default="privacy-check,citation-check",
        help="comma-separated inside-to-outside decorator ids",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        request = load_request(args.request)
        component = compose_review(parse_decorators(args.decorators))
        result = component(request)
    except (ValidationError, ComponentContractError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
