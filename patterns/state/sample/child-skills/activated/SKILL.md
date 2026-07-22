---
name: vendor-activated-state
description: Guard the terminal activated vendor state. Use when a recovered active vendor receives another onboarding action.
intent: Reject every onboarding transition from activated so terminal state cannot advance or be silently rewritten.
type: component
---

# Vendor Activated State

## Contract

Implement `handle-action` from `../../references/vendor-state-contract.md` for
the terminal `activated` state. Accept no transition action.

## Behavior

Return the exact illegal-transition error for every requested onboarding
action. Do not nominate a successor and do not ask the Context to write. Work
such as suspension or offboarding requires a separately designed lifecycle;
it must not be inferred here.

## Demo mode

`ActivatedState.handle` deterministically models this terminal behavior and
does not interpret this Skill file.
