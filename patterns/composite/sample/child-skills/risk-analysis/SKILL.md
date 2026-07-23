---
name: investment-risk-analysis
description: Produce one risk memo section. Use when an investment workflow needs a contract-compatible atomic risk analysis.
intent: Return material risks and diligence gates as one memo-section-v1 Leaf record.
type: component
---

# Risk Analysis

## Trigger

Use this child Skill only when the Investment Memo Builder addresses the
`risk-analysis` Leaf. It turns a supplied risk register into one section and
does not coordinate diligence work itself.

## Input contract

Accept exactly `id`, `title`, `skill`, and `input` in the invocation envelope.
Require `skill` to be `child-skills/risk-analysis/SKILL.md`, `id` to be
`risk-analysis`, and `input` to match:

```json
{
  "risks": ["sales-cycle length", "platform dependency", "valuation"],
  "gate_policy": "diligence gates are defined for each",
  "sources": ["risk-register"]
}
```

`risks` must contain at least two non-empty strings. `gate_policy` and every
source identifier must also be non-empty strings; source order is preserved.

## Output contract

Return exactly `id`, `title`, `content`, `evidence`, and `children` under
`memo-section-v1`. Preserve identity and title, list all risks in order in
`content`, map sources to `fixture:<source>`, and return `children: []`.

## Procedure

1. Validate the envelope, risk list, policy, and sources.
2. Render the ordered risk list and attach the supplied gate policy without
   inventing severity or mitigation.
3. Emit one Leaf record with the shared contract and no nested sections.

## Failure behavior

Reject fewer than two risks, blank or wrong-type values, missing or extra
fields, an unexpected identity/path, invalid evidence sources, and non-empty
children. Never downgrade invalid input into a generic risk statement.

## References

See [`section-contract.md`](../../references/section-contract.md) for the
uniform Leaf/Composite result shape. `scripts/run_demo.py` supplies the
deterministic risk executor and does not interpret this Skill file.

## Host/runtime boundary

The Agent Host loads this Leaf through the parent workflow. The Agent Runtime
interprets its behavioral source. The parent Composite retains ownership of
tree topology, node reachability, and final assembly.

## Verification and limits

From `sample/`, run `python3 scripts/run_demo.py` and the focused tests. This
demo records supplied diligence risks; it is not a risk score, legal opinion,
or investment recommendation.
