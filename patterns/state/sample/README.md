# Vendor Onboarding Workflow

## Scenario

A vendor moves through `draft`, `verified`, `approved`, and `activated`. The
same action, such as `approve`, means different things depending on the
persisted state, and the workflow must recover correctly after a restart.

## Why this is State

The Context reloads the current state before every action and delegates the
action to the corresponding ConcreteState Skill. Each state owns its legal
action and successor; the Context does not grow a centralized phase switch.

| GoF role | Skillware carrier in this example |
| --- | --- |
| Context | Root `sample/SKILL.md` and persisted workflow |
| State | `vendor-onboarding-state-v1` in `references/vendor-state-contract.md` |
| ConcreteState | `draft`, `verified`, `approved`, and `activated` child Skills |

## Contract

Input: vendor identity, persisted state record, and one requested action.
Output: ordered transition results plus final and recovered state. Illegal
actions and corrupted records fail without silently recreating `draft`.

## Where to look

- [Root Skill](SKILL.md) defines reload, delegation, and atomic persistence.
- [State contract](references/vendor-state-contract.md) defines `handle-action`.
- `scripts/run_demo.py` and `fixtures/valid/recover-approved.json` show restart recovery.

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
not a substitute for cross-process concurrency control. Initial construction is
the explicit bootstrap boundary; deletion of the known state record after that
point is a corruption error and never recreates `draft` silently.
