---
name: vendor-approved-state
description: Handle approved vendor activation. Use only when the recovered onboarding state is approved.
intent: Own the approved state's activate action, reject every other action, and nominate activated only after activation succeeds.
type: component
---

# Vendor Approved State

## Contract

Implement `handle-action` from `../../references/vendor-state-contract.md` for
the `approved` state. Accept only `activate`.

## Behavior

Enable the approved vendor for operational use. On success, return the
activation result and nominate `activated` as the successor. If activation
fails, remain `approved` and do not ask the Context to write. Reject every
other action before persistence.

## Demo mode

`ApprovedState.handle` deterministically models this ownership without
external I/O and does not interpret this Skill file.
