# Investment Memo Builder

## Scenario

An investment team needs one memo with market, financial, competition, and
risk sections. Each section is produced independently, but the final memo must
remain a validated tree that can be inspected or extended one section at a
time.

## Why this is Composite

Leaves and the root expose the same `memo-section-v1` record. The root can be
handled as a Component while recursively containing Leaf Components; the
relationship is the validated workflow tree, not the directory layout.

| GoF role | Skillware carrier in this example |
| --- | --- |
| Client | Caller of the investment-memo root Skill |
| Component | `references/section-contract.md` |
| Leaf | Four analysis child Skills |
| Composite | Root `sample/SKILL.md` and the investment memo node |

## Contract

Input: a node registry with one root and declared child references. Output: one
`memo-section-v1` tree where every node has `id`, `title`, `content`, `evidence`,
and `children`. Cycles, shared children, disconnected nodes, and invalid child
results fail before an invalid memo is returned.

## Where to look

- [Root Skill](SKILL.md) explains tree validation and child invocation.
- [Section contract](references/section-contract.md) is the common Component interface.
- `scripts/run_demo.py` is the oracle; `child-skills/` contains the four Leaf Skills.

This standalone Composite sample assembles an investment memo by invoking
market, financial, competition, and risk Leaves. Atomic sections and the root
memo use the same `memo-section-v1` result contract.

Run the default valid workflow from this directory:

```bash
python3 scripts/run_demo.py
```

Run an explicit workflow fixture:

```bash
python3 scripts/run_demo.py fixtures/valid/investment-memo.json
```

Run the focused tests:

```bash
python3 -m unittest discover tests -v
```

The demo requires Python 3.10 or newer, uses only the standard library, needs
no network, and imports no shared pattern code. Four deterministic executors
are keyed to the child Skill paths and compute Leaf results from fixture input;
Python does not interpret `SKILL.md`. The builder supports injected executors,
validates every returned record, preserves call order, and does not mutate the
workflow.

Whole-registry validation rejects missing references, repeated children,
shared-child DAGs, roots with parents, unreachable nodes, and cycles even in
disconnected components before any Leaf executes.

The JSON workflow is a node registry plus child references; the directory
layout itself is not the Composite relation. The relation comes from uniform
Component results and validated part-whole traversal.
