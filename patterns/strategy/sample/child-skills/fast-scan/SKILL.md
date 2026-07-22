---
name: code-review-fast-scan
description: Apply high-signal code-review checks. Use when the Context selects Fast Scan or directly addresses it through the shared review contract.
intent: Review every supplied added line with the bounded high-signal rule set and return the exact common result contract.
type: component
---

# Code Review Fast Scan

## Contract

Implement `review` from `../../references/review-strategy-contract.md`. Accept
the exact request schema and return the exact common result schema with
`strategy` set to `fast-scan`.

## Procedure

Traverse requested files and added lines in input order. Apply, in declared
order, checks for dynamic evaluation, hard-coded credential-like values, and
disabled TLS certificate verification. Emit one finding per matching rule and
derive summary counts from the emitted findings.

Do not add contextual SQL, authorization-bypass, or wildcard-permission checks.
Those belong to Deep Review. Do not omit required result fields when no finding
exists.

## Demo mode

`FastScanStrategy.review` deterministically models this procedure without
external I/O and does not interpret this Skill file.
