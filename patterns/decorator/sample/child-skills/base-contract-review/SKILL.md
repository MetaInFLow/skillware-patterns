---
name: base-contract-review
description: Produce the base contract-review result. Use as the ConcreteComponent before optional contract-preserving review decorators.
intent: Validate contract text and return the exact contract-review-v1 result without privacy or citation enhancements.
type: component
---

# Base Contract Review

## Contract

Implement the Component operation in
[`contract-review-v1`](../../references/contract-review-component.md). Accept
exactly `{text}` and return exactly `{summary, findings}`.

## Procedure

Validate the request, complete the bounded base review, and return the base
summary plus base findings. This constructive sample returns the stable summary
`Base contract review completed.` and no base findings so decorator behavior is
isolated and observable.

Do not run privacy or citation checks. Do not expose a mutable request or
result owned by another participant.

## Demo mode

`base_review` deterministically models this ConcreteComponent without external
I/O and does not interpret this Skill file.
