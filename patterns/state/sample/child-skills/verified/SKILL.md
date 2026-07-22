---
name: vendor-verified-state
description: Handle verified vendor approval. Use only when the recovered onboarding state is verified.
intent: Own the verified state's approve action, reject every other action, and nominate approved only after approval is recorded.
type: component
---

# Vendor Verified State

## Contract

Implement `handle-action` from `../../references/vendor-state-contract.md` for
the `verified` state. Accept only `approve`.

## Behavior

Record the authorized approval against the verified evidence. On success,
return the approval result and nominate `approved` as the successor. If
approval cannot be recorded, remain `verified` and do not ask the Context to
write. Reject every other action before persistence.

## Demo mode

`VerifiedState.handle` deterministically models this ownership without
external I/O and does not interpret this Skill file.
