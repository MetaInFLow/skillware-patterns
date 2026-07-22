# Release Event and Observer Contract

Event type: `release.published.v1`

Observer contract: `release-observer-v1`

## Event

The ConcreteSubject emits one event only after its release transition succeeds.
The event has exactly these fields in this order:

| Field | Type | Rule |
| --- | --- | --- |
| `type` | string | Exactly `release.published.v1`. |
| `release_id` | string | Stable non-empty release identifier. |
| `version` | string | Semantic version. |
| `commit` | string | Seven to forty lowercase hexadecimal characters. |
| `channel` | string | `stable`, `beta`, or `canary`. |
| `published_at` | string | RFC 3339 UTC timestamp supplied by the request. |
| `notes` | list of strings | One or more non-empty release notes in declared order. |

Each Observer receives a deep copy. One consumer therefore cannot alter the
canonical event or the event delivered to another consumer.

## Subscription

The Subject exposes explicit `register(observer_id, skill, update)` and
`unregister(observer_id)` operations. Observer IDs are unique while active.
Registrations retain insertion order; an observer removed and later registered
again moves to the end. Registration, unregistration, and publication re-entry
are rejected while a publication is in progress.

The fixture applies `subscription_operations` sequentially before publication.
Only active observers receive the event. Unknown unregistration and duplicate
registration are validation errors rather than silent no-ops.

## Update and accounting

`update(event) -> receipt` is the Observer operation. A delivered update returns
a non-empty receipt. An exception or invalid receipt becomes a `failed`
delivery with its error text. The Subject continues with later observers and
returns one delivery record per attempted observer in registration order:

```text
observer_id, skill, status, receipt, error
```

The summary counts attempted, delivered, and failed updates. This sample does
not retry, roll back, or claim transactional completion. Those policies require
separate idempotency, persistence, and recovery contracts.

## Agent and demo modes

In Agent mode, the root Skill invokes each registered consumer Skill through
this contract. In deterministic demo mode, `ReleaseSubject` calls explicit
Python functions keyed by child Skill path. The Python oracle models
registration and notification; it does not load or interpret `SKILL.md`.
