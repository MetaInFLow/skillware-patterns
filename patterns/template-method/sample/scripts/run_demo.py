#!/usr/bin/env python3
import argparse
from abc import ABC, abstractmethod
from copy import deepcopy
import json
from pathlib import Path
import sys


SAMPLE = Path(__file__).resolve().parents[1]
DEFAULT_REQUEST = SAMPLE / "fixtures/valid/healthcare-rfp.json"
REQUEST_SCHEMA = "enterprise-rfp-v1"
REQUEST_FIELDS = ("schema", "rfp_id", "domain", "requirements")
REQUIREMENT_FIELDS = ("id", "text", "mandatory")
HOOK_REQUEST_FIELDS = ("rfp_id", "domain", "requirements", "gaps")
HOOK_RESULT_FIELDS = ("domain", "focus_areas", "required_evidence")
RESULT_FIELDS = (
    "rfp_id",
    "domain",
    "requirement_ids",
    "gaps",
    "domain_result",
    "draft",
    "quality",
    "stages",
)
DRAFT_FIELDS = ("summary", "requirement_ids", "domain_focus")
QUALITY_FIELDS = ("passed", "checks")
REQUIRED_STAGES = (
    "extract-requirements",
    "analyze-gaps",
    "apply-domain-hook",
    "draft-response",
    "quality-check",
)
FORBIDDEN_OVERRIDES = (
    "run",
    "_extract_requirements",
    "_analyze_gaps",
    "_draft_response",
    "_quality_check",
)
SUPPORTED_DOMAINS = ("healthcare", "finance")
MAX_NESTING_DEPTH = 64
MAX_RFP_ID_CHARACTERS = 120
MAX_REQUIREMENT_ID_CHARACTERS = 80
MAX_REQUIREMENT_TEXT_CHARACTERS = 2_000
MAX_HOOK_ITEM_CHARACTERS = 200
MAX_REQUIREMENTS = 200
MAX_HOOK_ITEMS = 100


class ValidationError(ValueError):
    pass


class HookContractError(ValueError):
    pass


class ResultContractError(ValueError):
    pass


class DuplicateMemberError(ValueError):
    pass


def validate_structure(value, label, error_type=ValidationError):
    active_container_ids = set()
    stack = [("enter", value, 0)]

    while stack:
        action, current, depth = stack.pop()
        if action == "exit":
            active_container_ids.remove(id(current))
            continue
        if isinstance(current, str):
            if any(0xD800 <= ord(character) <= 0xDFFF for character in current):
                raise error_type(f"{label} must not contain lone Unicode surrogates")
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


def require_bounded_string(value, label, maximum, error_type=ValidationError):
    if not isinstance(value, str):
        raise error_type(f"{label} must be a string")
    if not value.strip():
        raise error_type(f"{label} must be non-empty")
    if len(value) > maximum:
        raise error_type(f"{label} must contain at most {maximum} characters")


def require_string_array(
    value,
    label,
    error_type,
    *,
    maximum_items=MAX_HOOK_ITEMS,
    allow_empty=False,
):
    if not isinstance(value, list):
        raise error_type(f"{label} must be a JSON array")
    if not allow_empty and not value:
        raise error_type(f"{label} must contain at least one item")
    if len(value) > maximum_items:
        raise error_type(f"{label} must contain at most {maximum_items} items")
    canonical = []
    seen = set()
    for index, item in enumerate(value):
        item_label = f"{label}[{index}]"
        require_bounded_string(
            item,
            item_label,
            MAX_HOOK_ITEM_CHARACTERS,
            error_type,
        )
        if item in seen:
            raise error_type(f"{label} items must be unique: {item}")
        seen.add(item)
        canonical.append(item)
    return canonical


def validate_request(request):
    validate_structure(request, "request")
    validate_exact_fields(request, REQUEST_FIELDS, "request")
    if request["schema"] != REQUEST_SCHEMA:
        raise ValidationError(
            f"unsupported request schema: {request['schema']}"
        )
    require_bounded_string(
        request["rfp_id"],
        "request.rfp_id",
        MAX_RFP_ID_CHARACTERS,
    )
    domain = request["domain"]
    if not isinstance(domain, str):
        raise ValidationError("request.domain must be a string")
    if domain not in SUPPORTED_DOMAINS:
        raise ValidationError(f"unknown domain: {domain}")

    requirements = request["requirements"]
    if not isinstance(requirements, list):
        raise ValidationError("request.requirements must be a JSON array")
    if not requirements:
        raise ValidationError(
            "request.requirements must contain at least one requirement"
        )
    if len(requirements) > MAX_REQUIREMENTS:
        raise ValidationError(
            f"request.requirements must contain at most {MAX_REQUIREMENTS} requirements"
        )

    canonical_requirements = []
    seen_ids = set()
    for requirement in requirements:
        validate_exact_fields(requirement, REQUIREMENT_FIELDS, "request requirement")
        require_bounded_string(
            requirement["id"],
            "request requirement.id",
            MAX_REQUIREMENT_ID_CHARACTERS,
        )
        require_bounded_string(
            requirement["text"],
            "request requirement.text",
            MAX_REQUIREMENT_TEXT_CHARACTERS,
        )
        if not isinstance(requirement["mandatory"], bool):
            raise ValidationError("request requirement.mandatory must be a boolean")
        requirement_id = requirement["id"]
        if requirement_id in seen_ids:
            raise ValidationError(
                f"request.requirements ids must be unique: {requirement_id}"
            )
        seen_ids.add(requirement_id)
        canonical_requirements.append(
            {
                "id": requirement_id,
                "text": requirement["text"],
                "mandatory": requirement["mandatory"],
            }
        )

    return {
        "schema": request["schema"],
        "rfp_id": request["rfp_id"],
        "domain": domain,
        "requirements": canonical_requirements,
    }


def build_hook_request(request, requirement_ids=None, gaps=None):
    canonical = validate_request(request)
    if requirement_ids is None:
        requirement_ids = [item["id"] for item in canonical["requirements"]]
    if gaps is None:
        gaps = [
            item["id"]
            for item in canonical["requirements"]
            if item["mandatory"] and "[gap]" in item["text"]
        ]
    return {
        "rfp_id": canonical["rfp_id"],
        "domain": canonical["domain"],
        "requirements": deepcopy(canonical["requirements"]),
        "gaps": deepcopy(gaps),
    }


def validate_hook_request(hook_request, expected_domain):
    validate_structure(hook_request, "domain hook request", HookContractError)
    validate_exact_fields(
        hook_request,
        HOOK_REQUEST_FIELDS,
        "domain hook request",
        HookContractError,
    )
    require_bounded_string(
        hook_request["rfp_id"],
        "domain hook request.rfp_id",
        MAX_RFP_ID_CHARACTERS,
        HookContractError,
    )
    if hook_request["domain"] != expected_domain:
        raise HookContractError(
            "domain hook request domain mismatch: "
            f"expected '{expected_domain}', found '{hook_request['domain']}'"
        )
    requirements = hook_request["requirements"]
    if not isinstance(requirements, list):
        raise HookContractError("domain hook request.requirements must be a JSON array")
    if not requirements:
        raise HookContractError(
            "domain hook request.requirements must contain at least one requirement"
        )
    if len(requirements) > MAX_REQUIREMENTS:
        raise HookContractError(
            "domain hook request.requirements must contain at most "
            f"{MAX_REQUIREMENTS} requirements"
        )
    canonical_requirements = []
    requirement_ids = set()
    for requirement in requirements:
        validate_exact_fields(
            requirement,
            REQUIREMENT_FIELDS,
            "domain hook request requirement",
            HookContractError,
        )
        require_bounded_string(
            requirement["id"],
            "domain hook request requirement.id",
            MAX_REQUIREMENT_ID_CHARACTERS,
            HookContractError,
        )
        require_bounded_string(
            requirement["text"],
            "domain hook request requirement.text",
            MAX_REQUIREMENT_TEXT_CHARACTERS,
            HookContractError,
        )
        if not isinstance(requirement["mandatory"], bool):
            raise HookContractError(
                "domain hook request requirement.mandatory must be a boolean"
            )
        if requirement["id"] in requirement_ids:
            raise HookContractError(
                "domain hook request requirement ids must be unique: "
                f"{requirement['id']}"
            )
        requirement_ids.add(requirement["id"])
        canonical_requirements.append(
            {field: deepcopy(requirement[field]) for field in REQUIREMENT_FIELDS}
        )
    gaps = require_string_array(
        hook_request["gaps"],
        "domain hook request.gaps",
        HookContractError,
        maximum_items=MAX_REQUIREMENTS,
        allow_empty=True,
    )
    if any(gap not in requirement_ids for gap in gaps):
        raise HookContractError(
            "domain hook request.gaps must reference requirement ids"
        )
    return {
        "rfp_id": hook_request["rfp_id"],
        "domain": hook_request["domain"],
        "requirements": canonical_requirements,
        "gaps": gaps,
    }


def validate_hook_result(result, expected_domain):
    validate_structure(result, "domain hook result", HookContractError)
    validate_exact_fields(
        result,
        HOOK_RESULT_FIELDS,
        "domain hook result",
        HookContractError,
    )
    if result["domain"] != expected_domain:
        raise HookContractError(
            "domain hook result domain mismatch: "
            f"expected '{expected_domain}', found '{result['domain']}'"
        )
    return {
        "domain": result["domain"],
        "focus_areas": require_string_array(
            result["focus_areas"],
            "domain hook result.focus_areas",
            HookContractError,
        ),
        "required_evidence": require_string_array(
            result["required_evidence"],
            "domain hook result.required_evidence",
            HookContractError,
        ),
    }


def healthcare_domain_hook(hook_request):
    validate_hook_request(hook_request, "healthcare")
    return {
        "domain": "healthcare",
        "focus_areas": [
            "patient-data-protection",
            "clinical-workflow-continuity",
        ],
        "required_evidence": [
            "security-control-mapping",
            "clinical-adoption-plan",
        ],
    }


def finance_domain_hook(hook_request):
    validate_hook_request(hook_request, "finance")
    return {
        "domain": "finance",
        "focus_areas": [
            "transaction-integrity",
            "regulatory-auditability",
        ],
        "required_evidence": [
            "control-testing-report",
            "audit-trail-sample",
        ],
    }


class RfpResponseTemplate(ABC):
    """AbstractClass that owns the complete, invariant RFP algorithm."""

    domain = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        forbidden = sorted(set(cls.__dict__) & set(FORBIDDEN_OVERRIDES))
        if forbidden:
            raise TypeError(
                "ConcreteClass may override only apply_domain_hook; "
                f"forbidden override: {forbidden[0]}"
            )

    def __init__(self, request):
        self._request = validate_request(request)
        if self._request["domain"] != self.domain:
            raise ValidationError(
                "ConcreteClass domain mismatch: "
                f"expected '{self.domain}', found '{self._request['domain']}'"
            )

    def run(self):
        stages = []

        requirement_ids = self._extract_requirements()
        stages.append("extract-requirements")

        gaps = self._analyze_gaps()
        stages.append("analyze-gaps")

        hook_request = build_hook_request(self._request, requirement_ids, gaps)
        domain_result = self.apply_domain_hook(deepcopy(hook_request))
        domain_result = validate_hook_result(domain_result, self.domain)
        stages.append("apply-domain-hook")

        draft = self._draft_response(requirement_ids, gaps, domain_result)
        stages.append("draft-response")

        quality = self._quality_check(draft)
        stages.append("quality-check")

        result = {
            "rfp_id": self._request["rfp_id"],
            "domain": self.domain,
            "requirement_ids": requirement_ids,
            "gaps": gaps,
            "domain_result": domain_result,
            "draft": draft,
            "quality": quality,
            "stages": stages,
        }
        return validate_result(result, self._request)

    def _extract_requirements(self):
        return [item["id"] for item in self._request["requirements"]]

    def _analyze_gaps(self):
        return [
            item["id"]
            for item in self._request["requirements"]
            if item["mandatory"] and "[gap]" in item["text"]
        ]

    @abstractmethod
    def apply_domain_hook(self, hook_request):
        """Implement the sole bounded primitive operation."""

    def _draft_response(self, requirement_ids, gaps, domain_result):
        return {
            "summary": f"Drafted response for {self._request['rfp_id']}.",
            "requirement_ids": deepcopy(requirement_ids),
            "domain_focus": deepcopy(domain_result["focus_areas"]),
        }

    def _quality_check(self, draft):
        return {
            "passed": True,
            "checks": [
                "all-requirements-covered",
                "domain-hook-validated",
                "mandatory-order-preserved",
            ],
        }


class HealthcareRfpResponse(RfpResponseTemplate):
    """ConcreteClass for the healthcare domain hook."""

    domain = "healthcare"

    def apply_domain_hook(self, hook_request):
        return healthcare_domain_hook(hook_request)


class FinanceRfpResponse(RfpResponseTemplate):
    """ConcreteClass for the financial-services domain hook."""

    domain = "finance"

    def apply_domain_hook(self, hook_request):
        return finance_domain_hook(hook_request)


CONCRETE_CLASSES = {
    "healthcare": HealthcareRfpResponse,
    "finance": FinanceRfpResponse,
}


def validate_result(result, request):
    error_type = ResultContractError
    canonical_request = validate_request(request)
    validate_structure(result, "result", error_type)
    validate_exact_fields(result, RESULT_FIELDS, "result", error_type)

    expected_rfp_id = canonical_request["rfp_id"]
    if result["rfp_id"] != expected_rfp_id:
        raise error_type(
            f"result.rfp_id mismatch: expected '{expected_rfp_id}', "
            f"found '{result['rfp_id']}'"
        )
    expected_domain = canonical_request["domain"]
    if result["domain"] != expected_domain:
        raise error_type(
            f"result.domain mismatch: expected '{expected_domain}', "
            f"found '{result['domain']}'"
        )

    expected_requirement_ids = [
        item["id"] for item in canonical_request["requirements"]
    ]
    requirement_ids = require_string_array(
        result["requirement_ids"],
        "result.requirement_ids",
        error_type,
        maximum_items=MAX_REQUIREMENTS,
    )
    if requirement_ids != expected_requirement_ids:
        raise error_type("result.requirement_ids must preserve request order")
    gaps = require_string_array(
        result["gaps"],
        "result.gaps",
        error_type,
        maximum_items=MAX_REQUIREMENTS,
        allow_empty=True,
    )
    if any(gap not in requirement_ids for gap in gaps):
        raise error_type("result.gaps must reference request requirement ids")

    try:
        domain_result = validate_hook_result(result["domain_result"], expected_domain)
    except HookContractError as exc:
        raise error_type(f"result.domain_result invalid: {exc}") from exc

    draft = result["draft"]
    validate_exact_fields(draft, DRAFT_FIELDS, "result.draft", error_type)
    require_bounded_string(
        draft["summary"],
        "result.draft.summary",
        MAX_REQUIREMENT_TEXT_CHARACTERS,
        error_type,
    )
    draft_requirement_ids = require_string_array(
        draft["requirement_ids"],
        "result.draft.requirement_ids",
        error_type,
        maximum_items=MAX_REQUIREMENTS,
    )
    if draft_requirement_ids != requirement_ids:
        raise error_type("result.draft.requirement_ids must match extracted requirements")
    draft_focus = require_string_array(
        draft["domain_focus"],
        "result.draft.domain_focus",
        error_type,
    )
    if draft_focus != domain_result["focus_areas"]:
        raise error_type("result.draft.domain_focus must match domain hook result")

    quality = result["quality"]
    validate_exact_fields(quality, QUALITY_FIELDS, "result.quality", error_type)
    if not isinstance(quality["passed"], bool):
        raise error_type("result.quality.passed must be a boolean")
    quality_checks = require_string_array(
        quality["checks"],
        "result.quality.checks",
        error_type,
    )
    if result["stages"] != list(REQUIRED_STAGES):
        raise error_type("result.stages must equal the invariant Template Method order")

    return {
        "rfp_id": result["rfp_id"],
        "domain": result["domain"],
        "requirement_ids": requirement_ids,
        "gaps": gaps,
        "domain_result": domain_result,
        "draft": {
            "summary": draft["summary"],
            "requirement_ids": draft_requirement_ids,
            "domain_focus": draft_focus,
        },
        "quality": {"passed": quality["passed"], "checks": quality_checks},
        "stages": list(REQUIRED_STAGES),
    }


def default_request(domain):
    if domain == "healthcare":
        return {
            "schema": REQUEST_SCHEMA,
            "rfp_id": "rfp-healthcare-001",
            "domain": "healthcare",
            "requirements": [
                {
                    "id": "security",
                    "text": "Protect patient data and provide control evidence.",
                    "mandatory": True,
                },
                {
                    "id": "continuity",
                    "text": "Maintain clinical workflow continuity during rollout.",
                    "mandatory": True,
                },
            ],
        }
    if domain == "finance":
        return {
            "schema": REQUEST_SCHEMA,
            "rfp_id": "rfp-finance-001",
            "domain": "finance",
            "requirements": [
                {
                    "id": "integrity",
                    "text": "Preserve transaction integrity across integrations.",
                    "mandatory": True,
                },
                {
                    "id": "auditability",
                    "text": "Provide an exportable control audit trail.",
                    "mandatory": True,
                },
            ],
        }
    if not isinstance(domain, str):
        raise ValidationError("domain must be a string")
    raise ValidationError(f"unknown domain: {domain}")


def run_template(concrete_class, request):
    if not isinstance(concrete_class, type) or not issubclass(
        concrete_class, RfpResponseTemplate
    ):
        raise ValidationError(
            "concrete_class must be an RfpResponseTemplate ConcreteClass"
        )
    return concrete_class(request).run()


def run_rfp(domain, request=None):
    if request is None:
        request = default_request(domain)
    canonical = validate_request(request)
    if canonical["domain"] != domain:
        raise ValidationError(
            f"request domain mismatch: expected '{domain}', "
            f"found '{canonical['domain']}'"
        )
    try:
        concrete_class = CONCRETE_CLASSES[domain]
    except (KeyError, TypeError):
        if not isinstance(domain, str):
            raise ValidationError("domain must be a string") from None
        raise ValidationError(f"unknown domain: {domain}") from None
    return run_template(concrete_class, canonical)


def run_rfp_request(request):
    canonical = validate_request(request)
    return run_rfp(canonical["domain"], canonical)


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


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Run Enterprise RFP Template Method")
    parser.add_argument("request", nargs="?", type=Path, default=DEFAULT_REQUEST)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        result = run_rfp_request(load_request(args.request))
    except (ValidationError, HookContractError, ResultContractError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
