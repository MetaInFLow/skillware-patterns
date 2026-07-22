---
name: software-release-notification
description: Publish one typed software release event to registered consumers. Use when audit, changelog, and team updates must remain independently managed.
intent: Notify explicitly registered release consumers in deterministic order with per-observer receipts, isolated failures, unsubscription, and re-entry protection.
type: workflow
---

# Software Release Notification

## Trigger

Use this root Skill after a software release has successfully transitioned to
published and its immutable release facts are available. Do not publish for a
failed or provisional release.

## Participants

This Skill is the ConcreteSubject and owns the Subject operations. Audit,
changelog, and team-notification are separately inspectable ConcreteObserver
Skills. Every consumer implements the `release-observer-v1` Observer contract
in `references/release-event-contract.md`.

Agent Host and Agent Runtime are execution context, not Observer participants.

## Agent mode

1. Validate the exact `release.published.v1` event fields before notification.
2. Apply each explicit `register` or `unregister` operation in declared order.
   Reject duplicate registration, unknown unregistration, and unknown Skills.
3. Freeze the active registration order when publication begins.
4. Invoke every active consumer Skill once in registration order with an
   isolated copy of the same event.
5. Record `observer_id`, Skill, `status`, `receipt`, and `error` for every
   attempt. A consumer failure must not prevent a later attempt.
6. Return the canonical event, ordered delivery records, and exact summary
   counts.

Reject a nested publication or a subscription change while delivery is active.
Do not retry silently and do not report notification as transaction completion.

## Registered consumer Skills

- `child-skills/audit/SKILL.md`
- `child-skills/changelog/SKILL.md`
- `child-skills/team-notification/SKILL.md`

The ConcreteSubject depends only on the shared update contract. Do not add a
consumer-specific branch to this root when a new Observer is registered.

## Demo mode

`scripts/run_demo.py` provides a standard-library `ReleaseSubject` and three
deterministic update functions keyed by the child Skill paths. Tests inject
other update functions to prove ordering, failure isolation, event-copy
isolation, and re-entry rejection. Python models the collaboration; it does not
interpret the behavioral source in the Skill files.

For the minimal plan API, `publish_release(version, observers)` accepts one
optional lowercase `v` prefix and emits the canonical version without it.
Callbacks that return `None` are adapted to internal receipts and count as
delivered unless they raise. The full workflow continues to require explicit
non-empty receipts from registered updates.

## Output contract

Return exactly `event`, `deliveries`, and `summary`. Deliveries remain in
registration order even when one fails. A successful attempt has a non-empty
receipt and `error: null`; a failed attempt has `receipt: null` and error text.

## Example

The default fixture publishes version `1.2.0` to audit, changelog, and
team-notification in that order. The unregistration fixture removes changelog
before publication, so only audit and team-notification are attempted.

## Ontology boundary

Behavioral Source -> Skill Artifact -> Skillware Unit -> Agent Host -> Agent Runtime -> Execution Trace -> Task Outcome

The Observer roles belong to the pattern mapping. Agent Host and Agent Runtime
remain execution context and are not reclassified as Observer participants.

## Anti-pattern

Polling release files or broadcasting to every discovered consumer is not
Observer because there is no Subject-managed registration relation. See
`../misuse/SKILL.md`.
