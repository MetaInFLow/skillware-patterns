---
name: vendor-draft-state
description: Handle draft vendor verification. Use only when the recovered onboarding state is draft.
intent: Own the draft state's verify action, reject every other action, and nominate verified only after verification succeeds.
type: component
---

# Vendor Draft State

## Contract

Implement `handle-action` from `../../references/vendor-state-contract.md` for
the `draft` state. Accept only `verify`.

## Behavior

Validate that required identity, tax, banking, and compliance evidence is
present and internally consistent. On success, return the verification result
and nominate `verified` as the successor. On failure, remain `draft` and do not
ask the Context to write. Reject every other action before persistence.

## Demo mode

`DraftState.handle` deterministically models this ownership without external
I/O and does not interpret this Skill file.
