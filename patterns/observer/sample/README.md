# Software Release Notification

> **This directory is the mock sample.** It demonstrates the Observer idea
> using release notifications; it is not the ECC hook implementation.

## Evidence at a glance

```mermaid
flowchart LR
    E[release.published.v1] --> S[Mock Subject\nSKILL.md]
    S --> A[audit]
    S --> C[changelog]
    S --> T[team-notification]
    A --> R[Receipt]
    C --> R
    T --> R
```

| Evidence layer | Open this | What proves the Observer relation |
| --- | --- | --- |
| **Upstream case** | [ECC continuous-learning-v2](https://github.com/affaan-m/ECC/blob/2bc924faf2f8e893bfe0af86b1931283693c30ae/skills/continuous-learning-v2/SKILL.md) + [hooks](https://github.com/affaan-m/ECC/blob/2bc924faf2f8e893bfe0af86b1931283693c30ae/hooks/hooks.json) | Lifecycle events are routed to an observation Skill (candidate correspondence). |
| **Mock Subject** | [`SKILL.md#agent-mode`](SKILL.md#agent-mode) | The root owns registration, order, event copies, and delivery accounting. |
| **Observer Skills** | [`child-skills/`](child-skills/) · [`references/release-event-contract.md`](references/release-event-contract.md) | Each consumer accepts the same event and returns an isolated receipt. |
| **Executable proof** | [`scripts/run_demo.py`](scripts/run_demo.py) · [`tests/test_demo.py`](tests/test_demo.py) | Tests cover registration, unregistration, failure isolation, and re-entry. |

**The pattern-bearing line is:** one Subject event → registered independent
Observers → one delivery receipt per Observer.

## Mock Skill source

```text
sample/
├── SKILL.md
├── child-skills/{audit,changelog,team-notification}/SKILL.md
├── references/release-event-contract.md
├── scripts/run_demo.py
└── tests/test_demo.py
```

```markdown
<!-- Observer: Subject owns subscriptions; consumers remain independent. -->
register observers -> freeze order -> publish release.published.v1
  -> audit receipt
  -> changelog receipt
  -> team-notification receipt
```

## Learn the pattern

| Before: the publisher hardcodes every consumer | After: the Subject publishes to registered Observers |
| --- | --- |
| `publish_release()`<br>`  call audit()`<br>`  call changelog()`<br>`  call team_notification()`<br><br>Adding a consumer changes the publisher, and one failure changes delivery behavior. | `release event -> registration snapshot -> independent Observer updates`<br><br>Consumers own their behavior and delivery receipts. |

### Use it when

| Use Observer when | Keep it simple when |
| --- | --- |
| consumers can be added or removed independently | every step is mandatory and ordered |
| one event should reach multiple Skills | a single downstream result is required |
| delivery needs receipts or failure isolation | polling is enough and no subscription state exists |

### Skill-author recipe

1. Define a typed event contract.
2. Make the Subject own registration and delivery policy.
3. Freeze the subscription snapshot per event.
4. Record each Observer attempt and specify retry behavior explicitly.

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
