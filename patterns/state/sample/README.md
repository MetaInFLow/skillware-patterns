# Vendor Onboarding Workflow

This standalone State sample advances a vendor through persisted draft,
verified, approved, and activated states. Each ConcreteState owns its accepted
action and successor; the Context reloads and validates state before delegation.

Run the default full workflow from this directory:

```bash
python3 scripts/run_demo.py
```

Run the restart-recovery fixture:

```bash
python3 scripts/run_demo.py fixtures/valid/recover-approved.json
```

Run the focused tests:

```bash
python3 -m unittest discover tests -v
```

The demo requires Python 3.10 or newer, uses only the standard library, needs
no network or external accounts, and imports no shared pattern code. The four
Python classes model separately inspectable ConcreteState Skills; Python does
not load or interpret `SKILL.md`.

Writes use an atomic same-directory replacement, and memory advances only after
that replacement succeeds. The sample is single-writer: atomic replacement is
not a substitute for cross-process concurrency control.
