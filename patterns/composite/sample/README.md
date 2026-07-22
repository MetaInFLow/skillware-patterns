# Investment Memo Builder

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
