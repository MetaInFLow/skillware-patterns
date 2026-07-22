---
name: investment-memo-builder
description: Assemble a validated investment memo tree. Use when market, financial, competition, and risk sections must share one recursive contract.
intent: Build one investment memo from independently inspectable analysis Skills while preserving a uniform section result at every tree level.
type: workflow
---

# Investment Memo Builder

## Trigger

Use this Skill when a task caller needs one investment memo composed from the
market, financial, competition, and risk analysis Skills through the same
section contract.

## Component contract

Invoke any node through `build_component(workflow, node_id)`, whether its kind
is Leaf or Composite. Every node returns exactly `id`, `title`, `content`,
`evidence`, and `children` as defined in
`references/section-contract.md`. Strings remain strings,
`evidence` remains a list of strings, and `children` remains a list of section
records. A Leaf always returns `children: []`. This root Composite returns the
same keys and places complete child section records in `children`.

## Workflow

1. Load `fixtures/valid/investment-memo.json` or the caller-selected JSON
   workflow without mutating it.
2. Validate the workflow and every node before creating the registry. Reject a
   duplicate ID before it can overwrite an earlier node.
3. Resolve `root`, then recursively resolve each Composite child reference in
   declared order.
4. Run the independently inspectable Leaf behavior associated with each leaf
   node and produce a `memo-section-v1` record with an empty `children` list.
5. Assemble each Composite as a `memo-section-v1` record containing its child
   records, then validate the final tree before returning it.

Reject a missing root or child, invalid kind or schema, Leaf with children,
contract violation, or reference cycle. Report the full cycle path.

## Child Skills

- `child-skills/market-analysis/SKILL.md`
- `child-skills/financial-analysis/SKILL.md`
- `child-skills/competition-analysis/SKILL.md`
- `child-skills/risk-analysis/SKILL.md`

The default root contains these four Leaves in exactly this order. Each child
remains addressable and inspectable independently of the root.

## Output contract

Return the root section record only. Do not add wrapper fields, flatten child
records, omit a Leaf's empty `children`, or reorder children.

## Example

The default workflow builds `investment-memo` for Northstar Analytics. Its
four child IDs are `market-analysis`, `financial-analysis`,
`competition-analysis`, and `risk-analysis`. The exact tree is committed at
`expected/investment-memo.json`.

## Anti-pattern

Do not classify a folder of unrelated Skills as Composite. A workflow whose
atomic and grouped results use different shapes also fails uniform Component
treatment. See `../misuse/SKILL.md`.
