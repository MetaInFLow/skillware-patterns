---
name: investment-memo-builder
description: Assemble a validated investment memo tree. Use when market, financial, competition, and risk sections must share one recursive contract.
intent: Build one investment memo by invoking independently inspectable analysis Skills and preserving a uniform section result at every tree level.
type: workflow
---

# Investment Memo Builder

## Trigger

Use this Skill when a task caller needs one investment memo composed from the
market, financial, competition, and risk analysis Skills through the same
section contract.

## Component contract

Invoke any node with its declared input, whether the node is a Leaf or
Composite. Every node returns exactly `id`, `title`, `content`, `evidence`, and
`children` under `memo-section-v1`. A Leaf returns `children: []`; this root
returns the same shape with complete child section records. The exact contract
is in `references/section-contract.md`.

## Agent mode

1. Load the JSON workflow without changing it and validate the complete node
   registry as one rooted tree.
2. For each Leaf reference in declared order, call the associated child Skill
   with its `input` object.
3. Require the child Skill to return a valid `memo-section-v1` record with its
   declared identity, title, and empty `children`.
4. Assemble validated child records into the root Component record and return
   only that record.

The associated child Skills are:

- `child-skills/market-analysis/SKILL.md`
- `child-skills/financial-analysis/SKILL.md`
- `child-skills/competition-analysis/SKILL.md`
- `child-skills/risk-analysis/SKILL.md`

## Demo mode

`scripts/run_demo.py` supplies four deterministic Leaf executors keyed by those
child Skill paths. Each executor accepts the same `id`, `title`, `skill`, and
`input` request, computes one section, and returns `memo-section-v1`. The
builder supports injected executor mappings so tests can observe calls without
changing workflow data. Python models the collaboration contract; it does not
load or interpret the child `SKILL.md` files.

## Tree rules

Before invoking a Leaf, reject a missing root or child, invalid node schema or
kind, duplicate node ID, repeated child, root with a parent, non-root node with
zero or multiple parents, unreachable node, or cycle anywhere in the registry.
A cycle error reports its complete cycle path. These rules reject shared-child
DAGs and disconnected components rather than assembling them as trees.

## Output contract

Return the root section record only. Do not add wrapper fields, flatten child
records, omit a Leaf's empty `children`, reorder children, or accept an
executor result before validating its exact keys and types.

## Example

The default workflow builds `investment-memo` for Northstar Analytics. It calls
market, financial, competition, and risk Leaves exactly once in that order.
The exact assembled tree is in `expected/investment-memo.json`.

## Ontology boundary

Behavioral Source -> Skill Artifact -> Skillware Unit -> Agent Host -> Agent Runtime -> Execution Trace -> Task Outcome

The Composite roles belong to the pattern mapping. Agent Host and Agent Runtime
remain execution context and are not reclassified as Composite participants.

## Anti-pattern

Do not classify a folder, dependency graph, shared-child DAG, or workflow with
different Leaf and Composite result shapes as Composite. See
`../misuse/SKILL.md`.
