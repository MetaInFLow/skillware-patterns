---
name: investment-market-analysis
description: Produce one market memo section. Use when an investment workflow needs a contract-compatible atomic market analysis.
intent: Return market demand and sizing evidence as one memo-section-v1 Leaf record.
type: component
---

# Market Analysis

## Trigger

Use this child Skill only when the Investment Memo Builder addresses the
`market-analysis` Leaf. It supplies one market section and never assembles
siblings or a parent memo.

## Input contract

Accept the invocation envelope with exactly `id`, `title`, `skill`, and `input`.
Require `skill` to be `child-skills/market-analysis/SKILL.md`, `id` to be
`market-analysis`, and `input` to contain exactly four non-empty fields:

```json
{
  "customer_segment": "Mid-market finance teams",
  "workflow_problem": "fragmented forecasting workflows",
  "market_wedge": "a focused analytics wedge",
  "sources": ["market-interviews", "market-sizing"]
}
```

`sources` is an ordered list of non-empty strings and is preserved as evidence
order.

## Output contract

Return exactly `id`, `title`, `content`, `evidence`, and `children` under
`memo-section-v1`. Preserve `id` and `title`, describe the segment, problem,
and wedge in `content`, map sources to `fixture:<source>`, and return an empty
`children` list.

## Procedure

1. Validate the complete envelope and payload.
2. Connect the segment to the workflow problem and state the wedge as a
   bounded demand claim.
3. Emit one Leaf record in the shared field order.

## Failure behavior

Reject missing or extra fields, blank strings, malformed sources, a wrong
Skill path or identity, and any child record. Never infer market facts not
present in the payload and never return a partial section.

## References

Use [`section-contract.md`](../../references/section-contract.md) for the
`memo-section-v1` boundary. `scripts/run_demo.py` is the deterministic oracle;
it models the child call and does not load this Skill file.

## Host/runtime boundary

The Agent Host selects this Leaf from the validated workflow. The Agent
Runtime interprets the behavioral source and produces the section record. The
parent Composite owns tree validation and sibling ordering.

## Verification and limits

From `sample/`, run `python3 scripts/run_demo.py` and the focused unit tests.
The example expresses a memo input transformation; it does not establish
market size, demand, or investment suitability.
