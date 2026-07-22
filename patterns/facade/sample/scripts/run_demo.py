#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import sys


DEFAULT_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures/valid/incident.json"


class ValidationError(ValueError):
    pass


def validate_request(request):
    if not isinstance(request, dict):
        raise ValidationError("request must be a JSON object")
    service = request.get("service")
    signal = request.get("signal")
    if (
        not isinstance(service, str)
        or not service.strip()
        or not isinstance(signal, str)
        or not signal.strip()
    ):
        raise ValidationError("service and signal are required non-empty strings")
    return service.strip(), signal.strip().lower()


def diagnose_5xx_spike(service):
    return {
        "summary": f"{service} is experiencing elevated 5xx responses.",
        "actions": [
            "page-on-call",
            "inspect-recent-deployments",
            "check-upstream-dependencies",
        ],
    }


def assess_5xx_impact():
    return "Customer requests may fail; treat checkout availability as degraded."


def draft_5xx_communication(service):
    return (
        f"Investigating elevated 5xx responses for {service}; "
        "customer impact is being assessed."
    )


def fallback_response(service, signal):
    return {
        "summary": f"{service} reported an unrecognized signal: {signal}.",
        "impact": "Impact is not yet classified.",
        "actions": ["request-human-triage"],
        "communication": (
            f"Human triage requested for {service}; "
            "impact and next update are pending."
        ),
    }


def respond_to_incident(request):
    service, signal = validate_request(request)
    if signal != "5xx spike":
        return fallback_response(service, signal)

    diagnosis = diagnose_5xx_spike(service)
    impact = assess_5xx_impact()
    communication = draft_5xx_communication(service)
    return {
        "summary": diagnosis["summary"],
        "impact": impact,
        "actions": diagnosis["actions"],
        "communication": communication,
    }


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Run the standalone Production Incident Response sample."
    )
    parser.add_argument(
        "fixture",
        nargs="?",
        type=Path,
        default=DEFAULT_FIXTURE,
        help="JSON request fixture (defaults to the known 5xx incident)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        request = json.loads(args.fixture.read_text(encoding="utf-8"))
        result = respond_to_incident(request)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
