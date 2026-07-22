---
name: contract-compliance-check
description: Add a compliance-marker finding around a contract review. Use as an optional ConcreteDecorator while preserving contract-review-v1.
intent: Invoke one wrapped contract-review Component and append one bounded compliance finding without changing its interface or owned data.
type: component
---

# Contract Compliance Check

## Contract

Implement the same
[`contract-review-v1`](../../references/contract-review-component.md)
Component interface as the wrapped Skill Artifact. Accept exactly `{text}` and
return exactly `{summary, findings}`.

## Wrapper procedure

Validate and copy the request. Invoke the wrapped Component exactly once with a
separate copy. Propagate its failure unchanged. Validate and copy its complete
result. If the original validated text contains the literal marker
`[noncompliant]`, append
`{"type": "compliance", "message": "Compliance exception marker detected."}`
unless an identical finding is already present. Otherwise append nothing.

Preserve the wrapped summary and existing finding order. Do not copy the base
review procedure, add output fields, or mutate data owned by the caller or
wrapped Component.

## Demo mode

`with_compliance_check` deterministically models this optional
ConcreteDecorator without external I/O and does not interpret this Skill
Artifact.
