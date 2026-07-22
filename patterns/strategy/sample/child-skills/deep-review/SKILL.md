---
name: code-review-deep-review
description: Apply extended contextual code-review checks. Use when security sensitivity, file count, or direct addressing selects Deep Review.
intent: Review every supplied added line with high-signal and contextual rules while returning the exact common result contract.
type: component
---

# Code Review Deep Review

## Contract

Implement `review` from `../../references/review-strategy-contract.md`. Accept
the exact request schema and return the exact common result schema with
`strategy` set to `deep-review`.

## Procedure

Traverse requested files and added lines in input order. Apply the Fast Scan
high-signal checks, then contextual checks for SQL concatenation, explicit
authorization bypass, and wildcard permission grants. Emit one finding per
matching rule and derive summary counts from the emitted findings.

Do not change request fields, finding fields, or summary fields to describe the
additional depth. Interchangeability depends on the shared interface.

## Demo mode

`DeepReviewStrategy.review` deterministically models this procedure without
external I/O and does not interpret this Skill file.
