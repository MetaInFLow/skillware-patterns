# Vendor Onboarding State Contract

Contract: `vendor-onboarding-state-v1`

Operation: `handle-action`

## Persisted record

The Context owns one UTF-8 JSON record with exactly these fields:

| Field | Type | Rule |
| --- | --- | --- |
| `schema` | string | Exactly `vendor-onboarding-state-v1`. |
| `vendor_id` | string | Stable, non-empty identity for this workflow. |
| `state` | string | `draft`, `verified`, `approved`, or `activated`. |
| `revision` | integer | `0`, `1`, `2`, or `3`, matching the acyclic state progression. |

The Context reloads and validates this record before handling an action. A
missing record creates a new `draft` workflow. Invalid JSON, fields, schema,
vendor identity, state, or revision is corrupted state and must not be
overwritten implicitly.

## State operation

The Context calls `current_state.handle(context, action)`. Each ConcreteState
owns one state-dependent policy:

| ConcreteState | Accepted action | Successor | State-specific result |
| --- | --- | --- | --- |
| `draft` | `verify` | `verified` | Verification evidence is ready for approval. |
| `verified` | `approve` | `approved` | Approval is recorded and activation is available. |
| `approved` | `activate` | `activated` | Activation completes and the vendor is active. |
| `activated` | none | none | Every transition is rejected. |

An unsupported action raises `illegal transition: <state> -> <action>; allowed
actions: <list-or-none>` before the Context writes. This is deterministic and
does not infer a transition from conversational history.

## Commit and recovery

For a legal transition, the Context writes the complete successor record to a
temporary file in the state directory, flushes it, and atomically replaces the
previous record. Only then does it update the in-memory State and revision. A
fresh Context recovers the persisted State and delegates the next action to
that ConcreteState.

The sample has no cross-process lock or compare-and-swap transaction, so one
workflow must have a single writer. Atomic replacement protects record
integrity; it does not provide distributed concurrency control.

## Agent and demo modes

In Agent mode, the root Skill follows the same contract and invokes the current
ConcreteState Skill. In demo mode, `VendorWorkflow` and four Python State
classes provide a deterministic oracle. Python models the collaboration but
does not load or interpret the Skill files.
