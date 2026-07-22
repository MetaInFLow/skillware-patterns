---
name: contract-citation-check
description: Add a missing-citation finding around a contract review. Use as a ConcreteDecorator while preserving contract-review-v1.
intent: Invoke one wrapped contract-review Component and append one bounded citation finding without changing its interface or owned data.
type: component
---

# Contract Citation Check

## Contract

Implement the same
[`contract-review-v1`](../../references/contract-review-component.md)
Component interface as the wrapped Skill. Accept exactly `{text}` and return
exactly `{summary, findings}`.

## Wrapper procedure

Validate and copy the request. Invoke the wrapped Component exactly once with a
separate copy. Propagate its failure unchanged. Validate and copy its complete
result. If the original validated text contains the literal marker
`[missing]`, append
`{"type": "citation", "message": "Missing citation marker detected."}`.
unless that exact `(type, message)` identity is already present. Otherwise
append nothing. Repeated Citation Check wrappers are therefore idempotent.

Preserve the wrapped summary and existing finding order. Do not copy the base
review procedure, add output fields, or mutate data owned by the caller or
wrapped Component.

## Demo mode

`with_citation_check` deterministically models this ConcreteDecorator without
external I/O and does not interpret this Skill file.
