#!/usr/bin/env python3
import argparse
from collections.abc import Mapping
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import unicodedata


SAMPLE = Path(__file__).resolve().parents[1]
DEFAULT_REQUEST = SAMPLE / "fixtures/valid/urgent-access.json"
FILTER_IDS = ("normalize", "redact", "classify", "prioritize", "draft")
RECORD_FIELDS = ("schema", "text", "category", "priority", "draft")
RESULT_FIELDS = ("record", "trace")
RECORD_SCHEMA = "support-ticket.v1"
CATEGORIES = ("unclassified", "access", "billing", "general")
PRIORITIES = ("low", "normal", "high")
MAX_TEXT_BYTES = 65_536
MAX_SERIALIZED_INPUT_BYTES = MAX_TEXT_BYTES * 6 + 1_024
MAX_JSON_DEPTH = 32
EMAIL_PATTERN = re.compile(
    r"(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])",
    re.IGNORECASE,
)


class PipelineError(ValueError):
    pass


class PipelineInputError(PipelineError):
    pass


class PipelineConfigurationError(PipelineError):
    pass


class PipelineResultError(PipelineError):
    pass


class RecordContractError(PipelineError):
    pass


class PipelineStageError(PipelineError):
    def __init__(self, stage, message):
        self.stage = stage
        super().__init__(message)


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


def _exact_fields_error(subject, expected, actual):
    expected_set = set(expected)
    missing = [field for field in expected if field not in actual]
    unexpected = sorted(set(actual) - expected_set)
    details = []
    if missing:
        details.append("missing: " + ", ".join(missing))
    if unexpected:
        details.append("unexpected: " + ", ".join(unexpected))
    return f"{subject} must be exactly: {', '.join(expected)}; " + "; ".join(details)


def _require_string_keys(value, subject, error_type):
    names = tuple(value)
    if any(not isinstance(name, str) or not name for name in names):
        raise error_type(f"{subject} field names must be non-empty strings")
    return names


def _require_valid_unicode(value, subject, error_type):
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:
        raise error_type(f"{subject} must contain valid Unicode") from exc


def _require_max_depth(value, subject, error_type):
    active = set()

    def visit(item, depth):
        if depth > MAX_JSON_DEPTH:
            raise error_type(
                f"{subject} exceeds maximum nesting depth of {MAX_JSON_DEPTH}"
            )
        if isinstance(item, Mapping):
            identity = id(item)
            if identity in active:
                raise error_type(f"{subject} must be acyclic")
            active.add(identity)
            try:
                for key, child in item.items():
                    visit(key, depth + 1)
                    visit(child, depth + 1)
            finally:
                active.remove(identity)
        elif isinstance(item, (list, tuple)):
            identity = id(item)
            if identity in active:
                raise error_type(f"{subject} must be acyclic")
            active.add(identity)
            try:
                for child in item:
                    visit(child, depth + 1)
            finally:
                active.remove(identity)

    try:
        visit(value, 0)
    except RecursionError as exc:
        raise error_type(
            f"{subject} exceeds maximum nesting depth of {MAX_JSON_DEPTH}"
        ) from exc


def validate_request(request):
    if not isinstance(request, Mapping):
        raise PipelineInputError("request must be a mapping")
    _require_max_depth(request, "request", PipelineInputError)
    field_names = _require_string_keys(request, "request", PipelineInputError)
    if set(field_names) != {"text"}:
        raise PipelineInputError(
            _exact_fields_error("request fields", ("text",), field_names)
        )
    text = request["text"]
    if not isinstance(text, str):
        raise PipelineInputError("request.text must be a string")
    _require_valid_unicode(text, "request.text", PipelineInputError)
    if not text.strip():
        raise PipelineInputError("request.text must not be blank")
    if len(text.encode("utf-8")) > MAX_TEXT_BYTES:
        raise PipelineInputError(
            f"request.text exceeds {MAX_TEXT_BYTES} UTF-8 bytes"
        )
    return {"text": text}


def validate_record(record):
    if not isinstance(record, Mapping):
        raise RecordContractError("record must be a mapping")
    _require_max_depth(record, "record", RecordContractError)
    field_names = _require_string_keys(record, "record", RecordContractError)
    if set(field_names) != set(RECORD_FIELDS):
        raise RecordContractError(
            _exact_fields_error("record fields", RECORD_FIELDS, field_names)
        )

    schema = record["schema"]
    if not isinstance(schema, str) or schema != RECORD_SCHEMA:
        raise RecordContractError(f"record.schema must equal '{RECORD_SCHEMA}'")

    text = record["text"]
    if not isinstance(text, str):
        raise RecordContractError("record.text must be a string")
    _require_valid_unicode(text, "record.text", RecordContractError)
    if not text.strip():
        raise RecordContractError("record.text must not be blank")

    category = record["category"]
    if not isinstance(category, str):
        raise RecordContractError("record.category must be a string")
    if category not in CATEGORIES:
        raise RecordContractError(
            "record.category must be one of: " + ", ".join(CATEGORIES)
        )

    priority = record["priority"]
    if not isinstance(priority, str):
        raise RecordContractError("record.priority must be a string")
    if priority not in PRIORITIES:
        raise RecordContractError(
            "record.priority must be one of: " + ", ".join(PRIORITIES)
        )

    draft = record["draft"]
    if not isinstance(draft, str):
        raise RecordContractError("record.draft must be a string")
    _require_valid_unicode(draft, "record.draft", RecordContractError)

    return {field: deepcopy(record[field]) for field in RECORD_FIELDS}


def validate_result(result):
    if not isinstance(result, Mapping):
        raise PipelineResultError("result must be a mapping")
    _require_max_depth(result, "result", PipelineResultError)
    field_names = _require_string_keys(result, "result", PipelineResultError)
    if set(field_names) != set(RESULT_FIELDS):
        raise PipelineResultError(
            _exact_fields_error("result fields", RESULT_FIELDS, field_names)
        )
    try:
        record = validate_record(result["record"])
    except RecordContractError as exc:
        raise PipelineResultError(f"result.record rejected: {exc}") from exc
    trace = result["trace"]
    if not isinstance(trace, list):
        raise PipelineResultError("result.trace must be a list")
    if any(not isinstance(item, str) for item in trace):
        raise PipelineResultError("result.trace entries must be strings")
    if trace != list(FILTER_IDS):
        raise PipelineResultError("result.trace must equal the canonical filter order")
    return {"record": record, "trace": list(trace)}


class TicketDataSource:
    def emit(self, request):
        copied = validate_request(request)
        return {
            "schema": RECORD_SCHEMA,
            "text": copied["text"],
            "category": "unclassified",
            "priority": "normal",
            "draft": "",
        }


class RecordPipe:
    contract = RECORD_SCHEMA

    def transfer(self, record):
        return validate_record(record)


class Filter:
    __slots__ = ("_filter_id", "_skill_path", "_transform")

    def __init__(self, filter_id, skill_path, transform):
        object.__setattr__(self, "_filter_id", filter_id)
        object.__setattr__(self, "_skill_path", skill_path)
        object.__setattr__(self, "_transform", transform)

    def __setattr__(self, _name, _value):
        raise AttributeError("Filter descriptors are immutable")

    @property
    def filter_id(self):
        return self._filter_id

    @property
    def skill_path(self):
        return self._skill_path

    @property
    def transform(self):
        return self._transform

    def apply(self, record):
        return self.transform(record)


class TicketDataSink:
    def consume(self, record, trace):
        if record["category"] == "unclassified":
            raise PipelineResultError("data sink requires a classified record")
        if not record["draft"].strip():
            raise PipelineResultError("data sink requires a non-blank draft")
        return validate_result({"record": deepcopy(record), "trace": list(trace)})


def normalize_filter(record):
    collapsed = " ".join(unicodedata.normalize("NFC", record["text"]).split())
    record["text"] = unicodedata.normalize("NFC", collapsed.casefold())
    return record


def redact_filter(record):
    record["text"] = EMAIL_PATTERN.sub("[redacted-email]", record["text"])
    return record


def classify_filter(record):
    text = record["text"]
    if any(term in text for term in ("cannot login", "log in", "login", "password", "locked", "sign in")):
        record["category"] = "access"
    elif any(term in text for term in ("billing", "invoice", "payment", "refund", "charge")):
        record["category"] = "billing"
    else:
        record["category"] = "general"
    return record


def prioritize_filter(record):
    text = record["text"]
    if any(term in text for term in ("urgent", "critical", "asap", "outage")):
        record["priority"] = "high"
    elif any(term in text for term in ("feedback", "suggestion")):
        record["priority"] = "low"
    else:
        record["priority"] = "normal"
    return record


def draft_filter(record):
    labels = {
        "access": "access",
        "billing": "billing",
        "general": "support",
        "unclassified": "support",
    }
    record["draft"] = (
        f"We received your {labels[record['category']]} ticket. "
        f"Priority: {record['priority']}."
    )
    return record


DEFAULT_FILTERS = (
    Filter("normalize", "child-skills/normalize/SKILL.md", normalize_filter),
    Filter("redact", "child-skills/redact/SKILL.md", redact_filter),
    Filter("classify", "child-skills/classify/SKILL.md", classify_filter),
    Filter("prioritize", "child-skills/prioritize/SKILL.md", prioritize_filter),
    Filter("draft", "child-skills/draft/SKILL.md", draft_filter),
)


def validate_filters(filters):
    try:
        supplied = tuple(filters)
    except TypeError as exc:
        raise PipelineConfigurationError("filters must be an iterable") from exc
    if any(not isinstance(item, Filter) for item in supplied):
        raise PipelineConfigurationError("filters must contain only Filter instances")
    for item in supplied:
        if not isinstance(item.filter_id, str) or not item.filter_id:
            raise PipelineConfigurationError("filter id must be a non-empty string")
        if not isinstance(item.skill_path, str) or not item.skill_path:
            raise PipelineConfigurationError("filter skill_path must be a non-empty string")
        if not callable(item.transform):
            raise PipelineConfigurationError("filter transform must be callable")

    by_id = {}
    for item in supplied:
        if item.filter_id in by_id:
            raise PipelineConfigurationError(f"duplicate filter: {item.filter_id}")
        by_id[item.filter_id] = item
    if set(by_id) != set(FILTER_IDS):
        raise PipelineConfigurationError(
            _exact_fields_error("filters", FILTER_IDS, tuple(by_id))
        )
    return tuple(by_id[filter_id] for filter_id in FILTER_IDS)


class PipelineRunner:
    def __init__(self, filters=DEFAULT_FILTERS, source=None, pipe=None, sink=None):
        admitted = validate_filters(filters)
        self._stages = tuple(
            (item.filter_id, item.transform) for item in admitted
        )
        self.source = source if source is not None else TicketDataSource()
        self.pipe = pipe if pipe is not None else RecordPipe()
        self.sink = sink if sink is not None else TicketDataSink()

    def run(self, request):
        current = self.source.emit(request)
        trace = []
        for filter_id, transform in self._stages:
            try:
                filter_input = self.pipe.transfer(current)
            except RecordContractError as exc:
                raise PipelineStageError(
                    filter_id,
                    f"stage '{filter_id}' input rejected: {exc}",
                ) from exc
            try:
                candidate = transform(filter_input)
            except Exception as exc:
                raise PipelineStageError(
                    filter_id,
                    f"stage '{filter_id}' failed: {type(exc).__name__}: {exc}",
                ) from exc
            try:
                current = self.pipe.transfer(candidate)
            except RecordContractError as exc:
                raise PipelineStageError(
                    filter_id,
                    f"stage '{filter_id}' output rejected: {exc}",
                ) from exc
            trace.append(filter_id)

        try:
            sink_input = self.pipe.transfer(current)
        except RecordContractError as exc:
            raise PipelineResultError(f"data sink input rejected: {exc}") from exc
        return self.sink.consume(sink_input, trace)


def run_pipeline(request, filters=DEFAULT_FILTERS):
    return PipelineRunner(filters=filters).run(request)


def load_request(path):
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise PipelineInputError(f"unable to read ticket input: {exc}") from exc
    if len(data) > MAX_SERIALIZED_INPUT_BYTES:
        raise PipelineInputError(
            "ticket input exceeds "
            f"{MAX_SERIALIZED_INPUT_BYTES} serialized bytes"
        )
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise PipelineInputError("invalid UTF-8 ticket input") from exc
    try:
        request = json.loads(
            text,
            object_pairs_hook=reject_duplicate_members,
            parse_constant=reject_non_finite,
        )
    except DuplicateMemberError as exc:
        raise PipelineInputError(f"duplicate JSON member: {exc}") from exc
    except RecursionError as exc:
        raise PipelineInputError(
            f"request exceeds maximum nesting depth of {MAX_JSON_DEPTH}"
        ) from exc
    except (json.JSONDecodeError, ValueError) as exc:
        raise PipelineInputError("invalid JSON ticket input") from exc
    _require_max_depth(request, "request", PipelineInputError)
    return request


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run the support ticket pipeline")
    parser.add_argument("request", nargs="?", type=Path, default=DEFAULT_REQUEST)
    args = parser.parse_args(argv)
    try:
        result = run_pipeline(load_request(args.request))
    except PipelineError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
