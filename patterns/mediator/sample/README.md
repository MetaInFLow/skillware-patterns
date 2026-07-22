# Deployment Coordinator

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
