---
name: investment-financial-analysis
description: Produce one financial memo section. Use when an investment workflow needs a contract-compatible atomic financial analysis.
intent: Return growth, burn, and financing evidence as one memo-section-v1 Leaf record.
type: component
---

# Financial Analysis

## Trigger

Use this child Skill only when the Investment Memo Builder addresses the
`financial-analysis` Leaf. It is a Leaf component, not a second memo builder.

## Input contract

Accept the root invocation envelope with exactly `id`, `title`, `skill`, and
`input`. Require `skill` to be
`child-skills/financial-analysis/SKILL.md`, `id` to be
`financial-analysis`, and `input` to be an object with exactly these fields:

```json
{
  "growth_signal": "Revenue growth is promising",
  "burn_profile": "the current burn profile",
  "financing_condition": "milestone-based financing",
  "sources": ["management-accounts", "cash-plan"]
}
```

The three analysis fields and every source identifier are non-empty strings;
source order is meaningful.

## Output contract

Return exactly `id`, `title`, `content`, `evidence`, and `children` under
`memo-section-v1`. Preserve the request `id` and `title`, render the bounded
financial conclusion in `content`, map sources in order to
`fixture:<source>` evidence identifiers, and return `children: []`.

## Procedure

1. Validate the envelope and payload before analysis.
2. State the growth signal, contrast it with the burn profile, and attach the
   financing condition as the diligence implication.
3. Emit one deterministic section record without adding a second level.

## Failure behavior

Reject missing, extra, or wrong-type fields, blank analysis values, invalid
source lists, an unexpected Skill path, or a non-empty child list. Do not emit
a partial record or silently coerce values.

## References

The shared result and invocation rules are in
[`section-contract.md`](../../references/section-contract.md). The executable
oracle is `scripts/run_demo.py`; its financial executor models this boundary
without interpreting this file.

## Host/runtime boundary

The Agent Host loads and routes this Skill as the `financial-analysis` Leaf.
The Agent Runtime interprets its behavioral source and returns the contract
record. The Composite relationship belongs to the surrounding Skillware unit;
Host and Runtime are execution context, not Composite participants.

## Verification and limits

Run `python3 scripts/run_demo.py` from the sample directory and execute the
focused tests to check the expected section and evidence order. This fixture
is a deterministic memo-section example, not financial advice or investment
underwriting.
