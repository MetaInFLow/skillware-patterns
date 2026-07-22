---
name: contract-privacy-check
description: Add an email privacy finding around a contract review. Use as a ConcreteDecorator while preserving contract-review-v1.
intent: Invoke one wrapped contract-review Component and append one bounded privacy finding without changing its interface or owned data.
type: component
---

# Contract Privacy Check

## Contract

Implement the same
[`contract-review-v1`](../../references/contract-review-component.md)
Component interface as the wrapped Skill. Accept exactly `{text}` and return
exactly `{summary, findings}`.

## Wrapper procedure

Validate and copy the request. Invoke the wrapped Component exactly once with a
separate copy. Propagate its failure unchanged. Validate and copy its complete
result. If the original validated text contains an email address, append
`{"type": "privacy", "message": "Email address detected."}`. Otherwise
append nothing.

Preserve the wrapped summary and existing finding order. Do not copy the base
review procedure, add output fields, or mutate data owned by the caller or
wrapped Component.

## Demo mode

`with_privacy_check` deterministically models this ConcreteDecorator without
external I/O and does not interpret this Skill file.
