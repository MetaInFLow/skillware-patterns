#!/usr/bin/env python3
import argparse
from collections.abc import Mapping
from dataclasses import dataclass
import json
from pathlib import Path
import sys
import unicodedata


SAMPLE = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATE_PATH = SAMPLE / "fixtures/valid/approved-expense.json"
FIELD_ORDER = ("receipt", "budget", "amount", "department")
MAX_AMOUNT = 1_000_000_000
MAX_DEPARTMENT_BYTES = 128
MAX_INPUT_BYTES = 65_536
MAX_JSON_DEPTH = 16


class SpecificationError(ValueError):
    pass


class SpecificationConfigurationError(SpecificationError):
    pass


class CandidateValidationError(SpecificationError):
    pass


class CandidateInputError(SpecificationError):
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
            raise CandidateValidationError(f"unsupported candidate field: {field}")
    return admitted


def _ordered_union(specifications):
    required = {
        field
        for specification in specifications
        for field in specification.required_fields
    }
    return tuple(field for field in FIELD_ORDER if field in required)


def _leaf_trace(specification, result, explanation):
    return {
        "specification": specification,
        "result": result,
        "explanation": explanation,
    }


class Specification:
    __slots__ = ()

    @property
    def name(self):
        raise NotImplementedError

    @property
    def required_fields(self):
        raise NotImplementedError

    def _evaluate_with_trace(self, candidate, evaluate_all):
        raise NotImplementedError

    def is_satisfied_by(self, candidate):
        admitted = validate_candidate(candidate, self.required_fields)
        result, _evaluations, _skipped, _explanation = self._evaluate_with_trace(
            admitted, False
        )
        return result

    def explain(self, candidate, *, evaluate_all=False):
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
        left = self.specifications if isinstance(self, AndSpecification) else (self,)
        right = (
            other.specifications if isinstance(other, AndSpecification) else (other,)
        )
        return AndSpecification(left + right)

    def __or__(self, other):
        if not isinstance(other, Specification):
            raise TypeError("can only compose Specification instances")
        left = self.specifications if isinstance(self, OrSpecification) else (self,)
        right = (
            other.specifications if isinstance(other, OrSpecification) else (other,)
        )
        return OrSpecification(left + right)

    def __invert__(self):
        return NotSpecification(self)


@dataclass(frozen=True, slots=True)
class HasReceipt(Specification):
    @property
    def name(self):
        return "HasReceipt"

    @property
    def required_fields(self):
        return ("receipt",)

    def _evaluate_with_trace(self, candidate, _evaluate_all):
        result = candidate["receipt"] is True
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

    def _evaluate_with_trace(self, candidate, _evaluate_all):
        result = candidate["amount"] <= candidate["budget"]
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

    def _evaluate_with_trace(self, candidate, _evaluate_all):
        result = candidate["amount"] <= self.maximum
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

    def _evaluate_with_trace(self, candidate, _evaluate_all):
        result = candidate["department"] == self.expected
        explanation = (
            f"department must equal {self.expected!r}; "
            f"observed {candidate['department']!r}"
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
        if len(specifications) < 2 or any(
            not isinstance(item, Specification) for item in specifications
        ):
            raise SpecificationConfigurationError(
                "AND requires at least two Specification instances"
            )
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
        if len(specifications) < 2 or any(
            not isinstance(item, Specification) for item in specifications
        ):
            raise SpecificationConfigurationError(
                "OR requires at least two Specification instances"
            )
        object.__setattr__(self, "specifications", specifications)

    @property
    def name(self):
        return " OR ".join(item.name for item in self.specifications)

    @property
    def required_fields(self):
        return _ordered_union(self.specifications)

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
        if not isinstance(self.specification, Specification):
            raise SpecificationConfigurationError(
                "NOT requires one Specification instance"
            )

    @property
    def name(self):
        if isinstance(self.specification, (AndSpecification, OrSpecification)):
            return f"NOT ({self.specification.name})"
        return f"NOT {self.specification.name}"

    @property
    def required_fields(self):
        return self.specification.required_fields

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
        data = path.read_bytes()
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
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if result["result"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
