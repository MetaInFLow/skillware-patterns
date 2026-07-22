#!/usr/bin/env python3
import argparse
from copy import deepcopy
import json
from pathlib import Path, PurePosixPath
import re
import sys


SAMPLE = Path(__file__).resolve().parents[1]
DEFAULT_REQUEST = SAMPLE / "fixtures/valid/low-risk-review.json"
REQUEST_SCHEMA = "risk-aware-code-review-request-v1"
RESULT_SCHEMA = "risk-aware-code-review-result-v1"
STRATEGY_CONTRACT = "risk-aware-code-review-v1"
DEEP_REVIEW_FILE_THRESHOLD = 4
REQUEST_FIELDS = ("schema", "review_id", "security_sensitive", "files")
FILE_FIELDS = ("path", "additions")
RESULT_FIELDS = (
    "schema",
    "review_id",
    "strategy",
    "reviewed_files",
    "findings",
    "summary",
)
FINDING_FIELDS = ("rule_id", "severity", "path", "line", "message")
SUMMARY_FIELDS = ("files_reviewed", "findings", "high", "medium", "low")
STRATEGY_IDS = ("fast-scan", "deep-review")


class ValidationError(ValueError):
    pass


class StrategyContractError(ValueError):
    pass


def validate_exact_fields(value, fields, label, error_type=ValidationError):
    if not isinstance(value, dict):
        raise error_type(f"{label} must be a JSON object")
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


def require_non_empty_string(value, label, maximum):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{label} must be a non-empty string")
    if len(value) > maximum:
        raise ValidationError(f"{label} must contain at most {maximum} characters")


def validate_safe_path(value):
    require_non_empty_string(value, "file.path", 240)
    path = PurePosixPath(value)
    raw_parts = value.split("/")
    if (
        path.is_absolute()
        or "\\" in value
        or any(part in {"", ".", ".."} for part in raw_parts)
    ):
        raise ValidationError("file.path must be a safe relative POSIX path")


def validate_request(request):
    validate_exact_fields(request, REQUEST_FIELDS, "request")
    if tuple(request) != REQUEST_FIELDS:
        raise ValidationError(
            "request field order must be: " + ", ".join(REQUEST_FIELDS)
        )
    if request["schema"] != REQUEST_SCHEMA:
        raise ValidationError(f"request.schema must be '{REQUEST_SCHEMA}'")
    require_non_empty_string(request["review_id"], "request.review_id", 64)
    if not isinstance(request["security_sensitive"], bool):
        raise ValidationError("request.security_sensitive must be a boolean")
    files = request["files"]
    if not isinstance(files, list) or not 1 <= len(files) <= 50:
        raise ValidationError("request files must contain between 1 and 50 items")

    seen_paths = set()
    for file_record in files:
        validate_exact_fields(file_record, FILE_FIELDS, "file")
        if tuple(file_record) != FILE_FIELDS:
            raise ValidationError("file field order must be: " + ", ".join(FILE_FIELDS))
        path = file_record["path"]
        validate_safe_path(path)
        if path in seen_paths:
            raise ValidationError(f"request file paths must be unique: {path}")
        seen_paths.add(path)

        additions = file_record["additions"]
        if not isinstance(additions, list):
            raise ValidationError("file.additions must be a JSON array")
        if len(additions) > 200:
            raise ValidationError("file.additions must contain at most 200 lines")
        for line_number, line in enumerate(additions, start=1):
            if not isinstance(line, str):
                raise ValidationError(
                    f"file.additions line {line_number} must be a string"
                )
            if len(line) > 500:
                raise ValidationError(
                    f"file.additions line {line_number} must contain at most 500 characters"
                )
    return request


def finding(rule_id, severity, path, line, message):
    return {
        "rule_id": rule_id,
        "severity": severity,
        "path": path,
        "line": line,
        "message": message,
    }


HIGH_SIGNAL_RULES = (
    (
        "dynamic-execution",
        "high",
        re.compile(r"\beval\s*\("),
        "Dynamic evaluation can execute untrusted input.",
    ),
    (
        "hardcoded-secret",
        "high",
        re.compile(r"\b(?:password|api_key|secret)\s*=\s*['\"][^'\"]+['\"]", re.I),
        "A credential-like value is hard coded.",
    ),
    (
        "insecure-tls",
        "high",
        re.compile(r"\bverify\s*=\s*False\b"),
        "TLS certificate verification is disabled.",
    ),
)

CONTEXT_RULES = (
    (
        "sql-concatenation",
        "high",
        re.compile(r"\b(?:SELECT|INSERT|UPDATE|DELETE)\b.*\+", re.I),
        "SQL text is constructed by concatenation.",
    ),
    (
        "authorization-bypass",
        "high",
        re.compile(r"\b(?:skip_auth|allow_all)\s*=\s*True\b"),
        "Authorization is explicitly bypassed.",
    ),
    (
        "wildcard-permission",
        "medium",
        re.compile(r"['\"](?:Action|permission)['\"]\s*:\s*['\"]\*['\"]", re.I),
        "A wildcard permission broadens access.",
    ),
)


def run_rules(request, rules):
    findings = []
    for file_record in request["files"]:
        for line_number, line in enumerate(file_record["additions"], start=1):
            for rule_id, severity, pattern, message in rules:
                if pattern.search(line):
                    findings.append(
                        finding(
                            rule_id,
                            severity,
                            file_record["path"],
                            line_number,
                            message,
                        )
                    )
    return findings


def build_result(request, strategy_id, findings):
    severity_counts = {
        severity: sum(item["severity"] == severity for item in findings)
        for severity in ("high", "medium", "low")
    }
    return {
        "schema": RESULT_SCHEMA,
        "review_id": request["review_id"],
        "strategy": strategy_id,
        "reviewed_files": [item["path"] for item in request["files"]],
        "findings": findings,
        "summary": {
            "files_reviewed": len(request["files"]),
            "findings": len(findings),
            **severity_counts,
        },
    }


class FastScanStrategy:
    strategy_id = "fast-scan"

    def review(self, request):
        validate_request(request)
        return build_result(request, self.strategy_id, run_rules(request, HIGH_SIGNAL_RULES))


class DeepReviewStrategy:
    strategy_id = "deep-review"

    def review(self, request):
        validate_request(request)
        return build_result(
            request,
            self.strategy_id,
            run_rules(request, HIGH_SIGNAL_RULES + CONTEXT_RULES),
        )


def select_strategy(request):
    validate_request(request)
    if request["security_sensitive"]:
        return "deep-review"
    if len(request["files"]) >= DEEP_REVIEW_FILE_THRESHOLD:
        return "deep-review"
    return "fast-scan"


def validate_review_result(result, request):
    validate_request(request)
    validate_exact_fields(
        result,
        RESULT_FIELDS,
        "strategy result",
        error_type=StrategyContractError,
    )
    if tuple(result) != RESULT_FIELDS:
        raise StrategyContractError(
            "strategy result field order must be: " + ", ".join(RESULT_FIELDS)
        )
    if result["schema"] != RESULT_SCHEMA:
        raise StrategyContractError(f"strategy result schema must be '{RESULT_SCHEMA}'")
    if result["review_id"] != request["review_id"]:
        raise StrategyContractError("strategy result review_id must match request.review_id")
    if result["strategy"] not in STRATEGY_IDS:
        raise StrategyContractError(
            "strategy result strategy must be one of: " + ", ".join(STRATEGY_IDS)
        )
    expected_paths = [item["path"] for item in request["files"]]
    if result["reviewed_files"] != expected_paths:
        raise StrategyContractError(
            "strategy result reviewed_files must match request file order"
        )
    findings = result["findings"]
    if not isinstance(findings, list):
        raise StrategyContractError("strategy result findings must be a JSON array")
    additions_by_path = {
        item["path"]: item["additions"] for item in request["files"]
    }
    for item in findings:
        validate_exact_fields(
            item,
            FINDING_FIELDS,
            "finding",
            error_type=StrategyContractError,
        )
        if tuple(item) != FINDING_FIELDS:
            raise StrategyContractError(
                "finding field order must be: " + ", ".join(FINDING_FIELDS)
            )
        if not isinstance(item["rule_id"], str) or not item["rule_id"]:
            raise StrategyContractError("finding.rule_id must be a non-empty string")
        if item["severity"] not in {"high", "medium", "low"}:
            raise StrategyContractError(
                "finding.severity must be one of: high, medium, low"
            )
        if item["path"] not in additions_by_path:
            raise StrategyContractError("finding.path must name a requested file")
        if (
            not isinstance(item["line"], int)
            or isinstance(item["line"], bool)
            or not 1 <= item["line"] <= len(additions_by_path[item["path"]])
        ):
            raise StrategyContractError("finding.line must name an added line")
        if not isinstance(item["message"], str) or not item["message"].strip():
            raise StrategyContractError("finding.message must be a non-empty string")

    validate_exact_fields(
        result["summary"],
        SUMMARY_FIELDS,
        "summary",
        error_type=StrategyContractError,
    )
    if tuple(result["summary"]) != SUMMARY_FIELDS:
        raise StrategyContractError(
            "summary field order must be: " + ", ".join(SUMMARY_FIELDS)
        )
    expected_summary = {
        "files_reviewed": len(expected_paths),
        "findings": len(findings),
        "high": sum(item["severity"] == "high" for item in findings),
        "medium": sum(item["severity"] == "medium" for item in findings),
        "low": sum(item["severity"] == "low" for item in findings),
    }
    if result["summary"] != expected_summary:
        raise StrategyContractError("strategy result summary does not match findings")
    return result


class RiskAwareCodeReview:
    def __init__(self, strategies=None):
        if strategies is None:
            strategies = {
                "fast-scan": FastScanStrategy(),
                "deep-review": DeepReviewStrategy(),
            }
        if not isinstance(strategies, dict) or set(strategies) != set(STRATEGY_IDS):
            raise StrategyContractError(
                "strategy registry must contain exactly: " + ", ".join(STRATEGY_IDS)
            )
        for strategy_id in STRATEGY_IDS:
            strategy = strategies[strategy_id]
            review = getattr(strategy, "review", None)
            if not callable(review):
                raise StrategyContractError(
                    f"strategy '{strategy_id}' review must be callable"
                )
            actual_id = getattr(strategy, "strategy_id", None)
            if actual_id != strategy_id:
                raise StrategyContractError(
                    f"strategy registry key '{strategy_id}' does not match strategy_id '{actual_id}'"
                )
        self._strategies = dict(strategies)

    def review(self, request, strategy_id=None):
        validate_request(request)
        selected = select_strategy(request) if strategy_id is None else strategy_id
        if selected not in self._strategies:
            raise ValidationError(
                "strategy_id must be one of: " + ", ".join(STRATEGY_IDS)
            )
        strategy_request = deepcopy(request)
        result = self._strategies[selected].review(strategy_request)
        validated = validate_review_result(result, request)
        if validated["strategy"] != selected:
            raise StrategyContractError(
                "strategy result strategy must match the addressed strategy"
            )
        return deepcopy(validated)


def load_request(path):
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeError as exc:
        raise ValidationError("request file must be valid UTF-8") from exc
    except OSError as exc:
        raise ValidationError(f"unable to read request file: {exc}") from exc
    try:
        request = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError("request file must contain valid JSON") from exc
    return validate_request(request)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Run a deterministic code review")
    parser.add_argument("request", nargs="?", default=str(DEFAULT_REQUEST))
    parser.add_argument("--strategy", default=None)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        request = load_request(Path(args.request))
        result = RiskAwareCodeReview().review(request, strategy_id=args.strategy)
    except (ValidationError, StrategyContractError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
