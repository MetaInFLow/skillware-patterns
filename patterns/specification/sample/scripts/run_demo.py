#!/usr/bin/env python3
import argparse
from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass
import json
import math
from pathlib import Path
import sys
import unicodedata


SAMPLE = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATE_PATH = SAMPLE / "fixtures/valid/approved-expense.json"
MAX_AMOUNT = 1_000_000_000
MAX_DEPARTMENT_BYTES = 128
MAX_INPUT_BYTES = 65_536
MAX_JSON_DEPTH = 16
MAX_REQUIRED_FIELDS = 32
MAX_FIELD_NAME_BYTES = 128
MAX_SPECIFICATION_NAME_BYTES = 128
MAX_CUSTOM_STRING_BYTES = 4_096
MAX_CUSTOM_COLLECTION_ITEMS = 128
MAX_CUSTOM_INTEGER = 1_000_000_000
MAX_CUSTOM_NUMBER = 1_000_000_000
MAX_EXPLANATION_BYTES = 4_096


class SpecificationError(ValueError):
    pass


class SpecificationConfigurationError(SpecificationError):
    pass


class CandidateValidationError(SpecificationError):
    pass


class CandidateInputError(SpecificationError):
    pass


class SpecificationEvaluationError(SpecificationError):
    pass


class DuplicateMemberError(ValueError):
    pass


def _exact_fields_error(expected, actual):
    expected_set = set(expected)
    missing = [field for field in expected if field not in actual]
    unexpected = sorted(set(actual) - expected_set)
    details = []
    if missing:
        details.append("missing: " + ", ".join(missing))
    if unexpected:
        details.append("unexpected: " + ", ".join(unexpected))
    return (
        f"candidate fields must be exactly: {', '.join(expected)}; "
        + "; ".join(details)
    )


def _require_valid_unicode(value, subject, error_type):
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:
        raise error_type(f"{subject} must contain valid Unicode") from exc


def _require_max_depth(value):
    active = set()

    def visit(item, depth):
        if depth > MAX_JSON_DEPTH:
            raise CandidateValidationError(
                f"candidate exceeds maximum nesting depth of {MAX_JSON_DEPTH}"
            )
        if isinstance(item, Mapping):
            identity = id(item)
            if identity in active:
                raise CandidateValidationError("candidate must be acyclic")
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
                raise CandidateValidationError("candidate must be acyclic")
            active.add(identity)
            try:
                for child in item:
                    visit(child, depth + 1)
            finally:
                active.remove(identity)

    try:
        visit(value, 0)
    except RecursionError as exc:
        raise CandidateValidationError(
            f"candidate exceeds maximum nesting depth of {MAX_JSON_DEPTH}"
        ) from exc


def _validate_amount(value, subject, error_type):
    if type(value) is not int:
        raise error_type(f"{subject} must be an integer")
    if not 0 <= value <= MAX_AMOUNT:
        raise error_type(f"{subject} must be between 0 and {MAX_AMOUNT}")
    return value


def _validate_department(value, subject, error_type):
    if not isinstance(value, str):
        raise error_type(f"{subject} must be a string")
    _require_valid_unicode(value, subject, error_type)
    normalized = unicodedata.normalize("NFC", value)
    if not normalized.strip():
        raise error_type(f"{subject} must not be blank")
    if len(normalized.encode("utf-8")) > MAX_DEPARTMENT_BYTES:
        raise error_type(
            f"{subject} exceeds {MAX_DEPARTMENT_BYTES} UTF-8 bytes"
        )
    return normalized


def _validate_required_fields(required_fields):
    if isinstance(required_fields, (str, bytes, set, frozenset, Mapping)):
        raise SpecificationConfigurationError(
            "Predicate required_fields must be an ordered iterable of field names"
        )
    try:
        fields = tuple(required_fields)
    except TypeError as exc:
        raise SpecificationConfigurationError(
            "Predicate required_fields must be an ordered iterable of field names"
        ) from exc
    if not fields:
        raise SpecificationConfigurationError(
            "Predicate required_fields must not be empty"
        )
    if len(fields) > MAX_REQUIRED_FIELDS:
        raise SpecificationConfigurationError(
            f"Predicate required_fields exceeds {MAX_REQUIRED_FIELDS} fields"
        )
    seen = set()
    for field_name in fields:
        if not isinstance(field_name, str) or not field_name.strip():
            raise SpecificationConfigurationError(
                "Predicate required_fields must contain non-blank strings"
            )
        _require_valid_unicode(
            field_name,
            "Predicate required field names",
            SpecificationConfigurationError,
        )
        if len(field_name.encode("utf-8")) > MAX_FIELD_NAME_BYTES:
            raise SpecificationConfigurationError(
                "Predicate required field name exceeds "
                f"{MAX_FIELD_NAME_BYTES} UTF-8 bytes"
            )
        if field_name in seen:
            raise SpecificationConfigurationError(
                f"Predicate required_fields contains duplicate: {field_name}"
            )
        seen.add(field_name)
    return fields


def _validate_custom_json(value, subject):
    if value is None or type(value) is bool:
        return value
    if type(value) is int:
        if abs(value) > MAX_CUSTOM_INTEGER:
            raise CandidateValidationError(
                f"{subject} integer exceeds absolute bound of {MAX_CUSTOM_INTEGER}"
            )
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise CandidateValidationError(f"{subject} must be a finite number")
        if abs(value) > MAX_CUSTOM_NUMBER:
            raise CandidateValidationError(
                f"{subject} number exceeds absolute bound of {MAX_CUSTOM_NUMBER}"
            )
        return value
    if isinstance(value, str):
        _require_valid_unicode(value, subject, CandidateValidationError)
        if len(value.encode("utf-8")) > MAX_CUSTOM_STRING_BYTES:
            raise CandidateValidationError(
                f"{subject} exceeds {MAX_CUSTOM_STRING_BYTES} UTF-8 bytes"
            )
        return value
    if isinstance(value, list):
        if len(value) > MAX_CUSTOM_COLLECTION_ITEMS:
            raise CandidateValidationError(
                f"{subject} exceeds {MAX_CUSTOM_COLLECTION_ITEMS} items"
            )
        return [
            _validate_custom_json(item, f"{subject}[{index}]")
            for index, item in enumerate(value)
        ]
    if isinstance(value, Mapping):
        if len(value) > MAX_CUSTOM_COLLECTION_ITEMS:
            raise CandidateValidationError(
                f"{subject} exceeds {MAX_CUSTOM_COLLECTION_ITEMS} members"
            )
        copied = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key:
                raise CandidateValidationError(
                    f"{subject} member names must be non-empty strings"
                )
            _require_valid_unicode(
                key, f"{subject} member names", CandidateValidationError
            )
            if len(key.encode("utf-8")) > MAX_FIELD_NAME_BYTES:
                raise CandidateValidationError(
                    f"{subject} member name exceeds {MAX_FIELD_NAME_BYTES} UTF-8 bytes"
                )
            copied[key] = _validate_custom_json(item, f"{subject}.{key}")
        return copied
    raise CandidateValidationError(f"{subject} must be JSON-compatible")


def validate_candidate(candidate, required_fields):
    if not isinstance(candidate, Mapping):
        raise CandidateValidationError("candidate must be a mapping")
    _require_max_depth(candidate)
    field_names = tuple(candidate)
    if any(not isinstance(name, str) or not name for name in field_names):
        raise CandidateValidationError(
            "candidate field names must be non-empty strings"
        )
    for name in field_names:
        _require_valid_unicode(
            name, "candidate field names", CandidateValidationError
        )
    if set(field_names) != set(required_fields):
        raise CandidateValidationError(
            _exact_fields_error(required_fields, field_names)
        )

    admitted = {}
    for field in required_fields:
        value = candidate[field]
        if field == "receipt":
            if type(value) is not bool:
                raise CandidateValidationError(
                    "candidate.receipt must be a boolean"
                )
            admitted[field] = value
        elif field in {"budget", "amount"}:
            admitted[field] = _validate_amount(
                value, f"candidate.{field}", CandidateValidationError
            )
        elif field == "department":
            admitted[field] = _validate_department(
                value, "candidate.department", CandidateValidationError
            )
        else:
            admitted[field] = _validate_custom_json(
                value, f"candidate.{field}"
            )
    serialized = json.dumps(
        admitted,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")
    if len(serialized) > MAX_INPUT_BYTES:
        raise CandidateValidationError(
            f"candidate exceeds {MAX_INPUT_BYTES} UTF-8 bytes after validation"
        )
    return admitted


def _ordered_union(specifications):
    ordered = []
    seen = set()
    for specification in specifications:
        for field_name in specification.required_fields:
            if field_name not in seen:
                seen.add(field_name)
                ordered.append(field_name)
    return tuple(ordered)


def _leaf_trace(specification, result, explanation):
    return {
        "specification": specification,
        "result": result,
        "explanation": explanation,
    }


class Specification:
    __slots__ = ()

    def _evaluate_with_trace(self, candidate, evaluate_all):
        raise NotImplementedError

    def _evaluate_boolean(self, candidate):
        raise NotImplementedError

    def is_satisfied_by(self, candidate):
        _require_supported_specification(self)
        admitted = validate_candidate(candidate, self.required_fields)
        return self._evaluate_boolean(admitted)

    def explain(self, candidate, *, evaluate_all=False):
        _require_supported_specification(self)
        if type(evaluate_all) is not bool:
            raise TypeError("evaluate_all must be a boolean")
        admitted = validate_candidate(candidate, self.required_fields)
        result, evaluations, skipped, explanation = self._evaluate_with_trace(
            admitted, evaluate_all
        )
        return {
            "specification": self.name,
            "result": result,
            "evaluation": "all" if evaluate_all else "short-circuit",
            "explanation": explanation,
            "evaluations": evaluations,
            "skipped": skipped,
        }

    def __and__(self, other):
        if not isinstance(other, Specification):
            raise TypeError("can only compose Specification instances")
        _require_supported_specification(self)
        _require_supported_specification(other)
        left = self.specifications if isinstance(self, AndSpecification) else (self,)
        right = (
            other.specifications if isinstance(other, AndSpecification) else (other,)
        )
        return AndSpecification(left + right)

    def __or__(self, other):
        if not isinstance(other, Specification):
            raise TypeError("can only compose Specification instances")
        _require_supported_specification(self)
        _require_supported_specification(other)
        left = self.specifications if isinstance(self, OrSpecification) else (self,)
        right = (
            other.specifications if isinstance(other, OrSpecification) else (other,)
        )
        return OrSpecification(left + right)

    def __invert__(self):
        _require_supported_specification(self)
        return NotSpecification(self)


@dataclass(frozen=True, slots=True)
class HasReceipt(Specification):
    @property
    def name(self):
        return "HasReceipt"

    @property
    def required_fields(self):
        return ("receipt",)

    def _evaluate_boolean(self, candidate):
        return candidate["receipt"] is True

    def _evaluate_with_trace(self, candidate, _evaluate_all):
        result = self._evaluate_boolean(candidate)
        explanation = (
            "receipt must be true; observed "
            + ("true" if candidate["receipt"] else "false")
        )
        return result, [_leaf_trace(self.name, result, explanation)], [], explanation


@dataclass(frozen=True, slots=True)
class WithinBudget(Specification):
    @property
    def name(self):
        return "WithinBudget"

    @property
    def required_fields(self):
        return ("budget", "amount")

    def _evaluate_boolean(self, candidate):
        return candidate["amount"] <= candidate["budget"]

    def _evaluate_with_trace(self, candidate, _evaluate_all):
        result = self._evaluate_boolean(candidate)
        relation = "within budget" if result else "over budget"
        explanation = (
            f"amount {candidate['amount']} must be <= budget "
            f"{candidate['budget']}; observed {relation}"
        )
        return result, [_leaf_trace(self.name, result, explanation)], [], explanation


@dataclass(frozen=True, slots=True)
class AuthorizedAmount(Specification):
    maximum: int

    def __post_init__(self):
        _validate_amount(
            self.maximum,
            "authorized maximum",
            SpecificationConfigurationError,
        )

    @property
    def name(self):
        return f"AuthorizedAmount({self.maximum})"

    @property
    def required_fields(self):
        return ("amount",)

    def _evaluate_boolean(self, candidate):
        return candidate["amount"] <= self.maximum

    def _evaluate_with_trace(self, candidate, _evaluate_all):
        result = self._evaluate_boolean(candidate)
        relation = "authorized" if result else "not authorized"
        explanation = (
            f"amount {candidate['amount']} must be <= authorized maximum "
            f"{self.maximum}; observed {relation}"
        )
        return result, [_leaf_trace(self.name, result, explanation)], [], explanation


@dataclass(frozen=True, slots=True)
class Department(Specification):
    expected: str

    def __post_init__(self):
        normalized = _validate_department(
            self.expected,
            "department specification",
            SpecificationConfigurationError,
        )
        object.__setattr__(self, "expected", normalized)

    @property
    def name(self):
        return f"Department({self.expected!r})"

    @property
    def required_fields(self):
        return ("department",)

    def _evaluate_boolean(self, candidate):
        return candidate["department"] == self.expected

    def _evaluate_with_trace(self, candidate, _evaluate_all):
        result = self._evaluate_boolean(candidate)
        explanation = (
            f"department must equal {self.expected!r}; "
            f"observed {candidate['department']!r}"
        )
        return result, [_leaf_trace(self.name, result, explanation)], [], explanation


@dataclass(frozen=True, slots=True)
class Predicate(Specification):
    name: str
    required_fields: tuple
    evaluator: object
    explanation: object

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise SpecificationConfigurationError(
                "Predicate name must be a non-blank string"
            )
        _require_valid_unicode(
            self.name, "Predicate name", SpecificationConfigurationError
        )
        if self.name != self.name.strip():
            raise SpecificationConfigurationError(
                "Predicate name must not have leading or trailing whitespace"
            )
        if len(self.name.encode("utf-8")) > MAX_SPECIFICATION_NAME_BYTES:
            raise SpecificationConfigurationError(
                f"Predicate name exceeds {MAX_SPECIFICATION_NAME_BYTES} UTF-8 bytes"
            )
        fields = _validate_required_fields(self.required_fields)
        if not callable(self.evaluator):
            raise SpecificationConfigurationError(
                "Predicate evaluator must be callable"
            )
        if not callable(self.explanation):
            raise SpecificationConfigurationError(
                "Predicate explanation must be callable"
            )
        object.__setattr__(self, "required_fields", fields)

    def _evaluate_boolean(self, candidate):
        try:
            result = self.evaluator(deepcopy(candidate))
        except Exception as exc:
            raise SpecificationEvaluationError(
                f"Predicate {self.name!r} evaluator failed: "
                f"{type(exc).__name__}: {exc}"
            ) from exc
        if type(result) is not bool:
            raise SpecificationEvaluationError(
                f"Predicate {self.name!r} evaluator must return a boolean"
            )
        return result

    def _evaluate_with_trace(self, candidate, _evaluate_all):
        result = self._evaluate_boolean(candidate)
        try:
            explanation = self.explanation(deepcopy(candidate), result)
        except Exception as exc:
            raise SpecificationEvaluationError(
                f"Predicate {self.name!r} explanation failed: "
                f"{type(exc).__name__}: {exc}"
            ) from exc
        if not isinstance(explanation, str):
            raise SpecificationEvaluationError(
                f"Predicate {self.name!r} explanation must return a string"
            )
        _require_valid_unicode(
            explanation,
            f"Predicate {self.name!r} explanation",
            SpecificationEvaluationError,
        )
        if len(explanation.encode("utf-8")) > MAX_EXPLANATION_BYTES:
            raise SpecificationEvaluationError(
                f"Predicate {self.name!r} explanation exceeds "
                f"{MAX_EXPLANATION_BYTES} UTF-8 bytes"
            )
        return result, [_leaf_trace(self.name, result, explanation)], [], explanation


@dataclass(frozen=True, slots=True)
class AndSpecification(Specification):
    specifications: tuple

    def __post_init__(self):
        try:
            specifications = tuple(self.specifications)
        except TypeError as exc:
            raise SpecificationConfigurationError(
                "AND requires at least two Specification instances"
            ) from exc
        if len(specifications) < 2:
            raise SpecificationConfigurationError(
                "AND requires at least two Specification instances"
            )
        for specification in specifications:
            _require_supported_specification(specification)
        object.__setattr__(self, "specifications", specifications)

    @property
    def name(self):
        return " AND ".join(
            f"({item.name})" if isinstance(item, OrSpecification) else item.name
            for item in self.specifications
        )

    @property
    def required_fields(self):
        return _ordered_union(self.specifications)

    def _evaluate_boolean(self, candidate):
        return all(
            specification._evaluate_boolean(candidate)
            for specification in self.specifications
        )

    def _evaluate_with_trace(self, candidate, evaluate_all):
        evaluations = []
        skipped = []
        first_failure = None
        result = True
        for index, specification in enumerate(self.specifications):
            child_result, child_evaluations, child_skipped, _ = (
                specification._evaluate_with_trace(candidate, evaluate_all)
            )
            evaluations.extend(child_evaluations)
            skipped.extend(child_skipped)
            if not child_result:
                result = False
                if first_failure is None:
                    first_failure = specification.name
                if not evaluate_all:
                    skipped.extend(
                        item.name for item in self.specifications[index + 1 :]
                    )
                    break
        if result:
            explanation = (
                f"AND satisfied all {len(self.specifications)} specifications."
            )
        else:
            explanation = f"AND failed because {first_failure} was false."
        return result, evaluations, skipped, explanation


@dataclass(frozen=True, slots=True)
class OrSpecification(Specification):
    specifications: tuple

    def __post_init__(self):
        try:
            specifications = tuple(self.specifications)
        except TypeError as exc:
            raise SpecificationConfigurationError(
                "OR requires at least two Specification instances"
            ) from exc
        if len(specifications) < 2:
            raise SpecificationConfigurationError(
                "OR requires at least two Specification instances"
            )
        for specification in specifications:
            _require_supported_specification(specification)
        object.__setattr__(self, "specifications", specifications)

    @property
    def name(self):
        return " OR ".join(item.name for item in self.specifications)

    @property
    def required_fields(self):
        return _ordered_union(self.specifications)

    def _evaluate_boolean(self, candidate):
        return any(
            specification._evaluate_boolean(candidate)
            for specification in self.specifications
        )

    def _evaluate_with_trace(self, candidate, evaluate_all):
        evaluations = []
        skipped = []
        first_success = None
        result = False
        for index, specification in enumerate(self.specifications):
            child_result, child_evaluations, child_skipped, _ = (
                specification._evaluate_with_trace(candidate, evaluate_all)
            )
            evaluations.extend(child_evaluations)
            skipped.extend(child_skipped)
            if child_result:
                result = True
                if first_success is None:
                    first_success = specification.name
                if not evaluate_all:
                    skipped.extend(
                        item.name for item in self.specifications[index + 1 :]
                    )
                    break
        if result:
            explanation = f"OR satisfied because {first_success} was true."
        else:
            explanation = (
                f"OR failed because all {len(self.specifications)} specifications "
                "were false."
            )
        return result, evaluations, skipped, explanation


@dataclass(frozen=True, slots=True)
class NotSpecification(Specification):
    specification: Specification

    def __post_init__(self):
        _require_supported_specification(self.specification)

    @property
    def name(self):
        if isinstance(self.specification, (AndSpecification, OrSpecification)):
            return f"NOT ({self.specification.name})"
        return f"NOT {self.specification.name}"

    @property
    def required_fields(self):
        return self.specification.required_fields

    def _evaluate_boolean(self, candidate):
        return not self.specification._evaluate_boolean(candidate)

    def _evaluate_with_trace(self, candidate, evaluate_all):
        child_result, evaluations, skipped, _ = (
            self.specification._evaluate_with_trace(candidate, evaluate_all)
        )
        result = not child_result
        explanation = (
            f"NOT {'satisfied' if result else 'failed'} because "
            f"{self.specification.name} was "
            f"{'false' if result else 'true'}."
        )
        return result, evaluations, skipped, explanation


def _require_supported_specification(specification):
    supported_types = (
        HasReceipt,
        WithinBudget,
        AuthorizedAmount,
        Department,
        Predicate,
        AndSpecification,
        OrSpecification,
        NotSpecification,
    )
    if type(specification) not in supported_types:
        raise SpecificationConfigurationError(
            "unsupported Specification implementation: "
            f"{type(specification).__name__}; use Predicate for custom rules"
        )


DEFAULT_EXPENSE_POLICY = (
    HasReceipt()
    & WithinBudget()
    & AuthorizedAmount(1000)
    & ~Department("restricted")
)


def reject_duplicate_members(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateMemberError(key)
        result[key] = value
    return result


def reject_non_finite(value):
    raise ValueError(f"non-finite number: {value}")


def load_candidate(path):
    try:
        with path.open("rb") as input_file:
            data = input_file.read(MAX_INPUT_BYTES + 1)
    except OSError as exc:
        raise CandidateInputError(f"unable to read candidate input: {exc}") from exc
    if len(data) > MAX_INPUT_BYTES:
        raise CandidateInputError(
            f"candidate input exceeds {MAX_INPUT_BYTES} bytes"
        )
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise CandidateInputError("candidate input must be valid UTF-8") from exc
    try:
        candidate = json.loads(
            text,
            object_pairs_hook=reject_duplicate_members,
            parse_constant=reject_non_finite,
        )
    except DuplicateMemberError as exc:
        raise CandidateInputError(
            f"candidate input contains duplicate member: {exc.args[0]}"
        ) from exc
    except (json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise CandidateInputError("candidate input contains invalid JSON") from exc
    return candidate


def build_parser():
    parser = argparse.ArgumentParser(
        description="Evaluate the reusable expense approval Specification."
    )
    parser.add_argument(
        "candidate",
        nargs="?",
        type=Path,
        default=DEFAULT_CANDIDATE_PATH,
        help="JSON expense Candidate (defaults to the approved fixture)",
    )
    parser.add_argument(
        "--evaluation",
        choices=("short-circuit", "all"),
        default="all",
        help="trace mode (boolean policy semantics always short-circuit)",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        candidate = load_candidate(args.candidate)
        result = DEFAULT_EXPENSE_POLICY.explain(
            candidate, evaluate_all=args.evaluation == "all"
        )
    except SpecificationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=True, indent=2, allow_nan=False))
    return 0 if result["result"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
