---
name: investment-competition-analysis
description: Produce one competition memo section. Use when an investment workflow needs a contract-compatible atomic competition analysis.
intent: Return differentiation and competitor evidence as one memo-section-v1 Leaf record.
type: component
---

# Competition Analysis

## Trigger

Use this child Skill only for the `competition-analysis` Leaf selected by the
Investment Memo Builder. It produces a single competitor section with no
child invocation.

## Input contract

Accept exactly the invocation envelope `id`, `title`, `skill`, and `input`.
Require `skill` to be `child-skills/competition-analysis/SKILL.md`, `id` to be
`competition-analysis`, and `input` to match:

```json
{
  "differentiator": "workflow integration",
  "alternatives": "suites and point solutions",
  "sources": ["competitor-matrix"]
}
```

All text values and every ordered source identifier must be non-empty strings.

## Output contract

Return exactly `id`, `title`, `content`, `evidence`, and `children` under
`memo-section-v1`. Keep the declared identity and title, state the
differentiator alongside the alternatives in `content`, map sources to
`fixture:<source>` in order, and return `children: []`.

## Procedure

1. Validate the envelope and all payload fields.
2. Compare the supplied differentiator with the named alternatives without
   adding competitors or unsupported claims.
3. Emit one deterministic Leaf record in canonical field order.

## Failure behavior

Reject wrong identity or Skill path, missing or extra fields, blank text,
invalid source arrays, and any attempt to return nested children. Do not
silently broaden the comparison or emit partial output.

## References

The uniform Leaf boundary is defined in
[`section-contract.md`](../../references/section-contract.md). The default
oracle is `scripts/run_demo.py`; it models the child call and does not
interpret this behavioral source.

## Host/runtime boundary

The Agent Host routes the declared Leaf to this Skill. The Agent Runtime
interprets it and returns one `memo-section-v1` record. Composite tree
validation, evidence assembly, and sibling order remain owned by the parent.

## Verification and limits

Run `python3 scripts/run_demo.py` and the focused tests from `sample/` to
verify identity, evidence order, and `children: []`. This is a bounded
comparison memo, not a competitive intelligence or market-validation claim.
