---
name: risk-aware-code-review
description: Select an interchangeable code-review procedure by risk. Use for bounded changed-file requests that require one stable review result contract.
intent: Validate one code-review request, select Fast Scan or Deep Review deterministically, and enforce the same result contract after delegation.
type: workflow
---

# Risk-Aware Code Review

## Trigger

Use this root Skill when changed files must be reviewed through one stable
interface while review depth varies by security sensitivity or change size.
Input must satisfy `references/review-strategy-contract.md`.

## Participants

This Skill is the Context. `risk-aware-code-review-v1` is the Strategy contract.
Fast Scan and Deep Review are ConcreteStrategy child Skills.

Agent Host and Agent Runtime are execution context, not Strategy participants.

## Agent mode

1. Validate the exact request schema, types, bounds, path safety, and unique
   file identities before selecting a procedure.
2. Select Deep Review when `security_sensitive` is true. Otherwise select Deep
   Review for four or more files and Fast Scan for one to three files.
3. Invoke exactly one selected child Skill through the common `review`
   operation. Do not merge procedures or change the request shape.
4. Permit explicit `fast-scan` or `deep-review` addressing only when a caller
   intentionally requests audit, replay, or contract testing.
5. Validate the returned schema, identity, addressed strategy, reviewed-file
   order, finding records, and derived summary before returning it.

## ConcreteStrategy Skills

- `child-skills/fast-scan/SKILL.md`
- `child-skills/deep-review/SKILL.md`

Both accept the same request and return the same result fields. Fast Scan uses
only high-signal checks; Deep Review adds contextual checks. They vary the
procedure, not the Context or public interface.

## Demo mode

`scripts/run_demo.py` implements an injectable `RiskAwareCodeReview` Context
and two separately addressable strategy objects using only the Python standard
library. The deterministic rules demonstrate delegation and conformance; they
are not a production security scanner and do not interpret these Skill files.

## Output contract

Return exactly `schema`, `review_id`, `strategy`, `reviewed_files`, `findings`,
and `summary` as specified by the contract reference. Reject a strategy result
that exposes any other interface.

## Example

The default two-file, non-security-sensitive fixture selects Fast Scan. The
security-sensitive fixture and four-file fixture both select Deep Review.

## Anti-pattern

Branches that perform unrelated work and return incompatible objects are not
interchangeable Strategies. See `../misuse/SKILL.md`.
