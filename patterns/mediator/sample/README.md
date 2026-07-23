# Deployment Coordinator

## Scenario

A release is ready only when build, security, documentation, and approval checks
all report `pass`. The checks must remain isolated and must not call each other
or decide the release independently.

## Why this is Mediator

The Deployment Coordinator is the ConcreteMediator. It owns the single report
boundary, addresses each Colleague once in canonical order, isolates failures,
and applies the all-pass policy. Colleagues know the Mediator, not one another.

| GoF role | Skillware carrier in this example |
| --- | --- |
| Mediator | `deployment-readiness-v1` report contract |
| ConcreteMediator | Root `deployment-coordinator` Skill |
| Colleague | `build`, `security`, `docs`, and `approval` child Skills |

## Contract

Input: exactly four statuses: `build`, `security`, `docs`, and `approval`.
Output: ordered reports and a release or blocked decision. Invalid status sets
fail before any Colleague is addressed; a specialist failure is isolated and
cannot be mistaken for readiness.

## Where to look

- [Root Skill](SKILL.md) defines binding, ordering, isolation, and policy.
- [Readiness contract](references/deployment-readiness-contract.md) defines the report boundary.
- `scripts/run_demo.py` and the security-failure fixture show centralized coordination.

This standalone Mediator sample coordinates build, security, documentation,
and approval Colleagues through one Deployment Coordinator. Every participant
is addressed once in canonical order and reports only to the Mediator. The
ConcreteMediator isolates callable failures, applies the all-pass policy, and
returns a deterministic release or blocked decision without doing specialist
work.

Run the deterministic default release-ready demo:

```bash
python3 scripts/run_demo.py
```

Run another bounded JSON workflow and the focused tests:

```bash
python3 scripts/run_demo.py fixtures/valid/security-failure.json
python3 -m unittest discover tests -v
```

The sample requires Python 3.10 or later, uses only the standard library, needs
no network or account, imports no shared pattern code, and does not modify its
fixtures. Binding and peer isolation are trusted-code contract boundaries, not
a security sandbox.
