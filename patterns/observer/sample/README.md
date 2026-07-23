# Software Release Notification

## Scenario

After version `1.2.0` is published, audit, changelog, and team-notification
consumers must receive the same release facts. Consumers may be registered or
unregistered without changing the publisher's core workflow.

## Why this is Observer

The release publisher is the Subject. It owns registration, freezes delivery
order, sends one typed event to each independent consumer, and records isolated
receipts. The consumer Skills never call one another.

| GoF role | Skillware carrier in this example |
| --- | --- |
| Subject / ConcreteSubject | Root `sample/SKILL.md` and `ReleaseSubject` oracle |
| Observer | `release-observer-v1` in `references/release-event-contract.md` |
| ConcreteObserver | `audit`, `changelog`, and `team-notification` child Skills |

## Contract

Input: a successful `release.published.v1` event plus explicit registration
operations. Output: the event, ordered delivery receipts, and summary counts.
Duplicate registration, unknown unregistration, nested publication, and silent
retry are rejected.

## Where to look

- [Root Skill](SKILL.md) defines registration and delivery policy.
- [Event contract](references/release-event-contract.md) defines the shared Observer interface.
- `scripts/run_demo.py` demonstrates order, failure isolation, and re-entry protection.

This standalone Observer sample publishes one typed software release event to
explicitly registered audit, changelog, and team-notification consumer Skills.

Run the default valid workflow from this directory:

```bash
python3 scripts/run_demo.py
```

Run the fixture that unregisters changelog before publication:

```bash
python3 scripts/run_demo.py fixtures/valid/release-after-unregistration.json
```

Run the focused tests:

```bash
python3 -m unittest discover tests -v
```

The demo requires Python 3.10 or newer, uses only the standard library, needs
no network or external accounts, and imports no shared pattern code. Three
deterministic update functions model separately inspectable child Skills;
Python does not load or interpret `SKILL.md`.

The Subject applies explicit registration operations, freezes insertion order
for delivery, gives each Observer an isolated event copy, records every attempt,
continues after failure, and rejects publication re-entry. Notification is not
transaction completion and this sample performs no implicit retry.
