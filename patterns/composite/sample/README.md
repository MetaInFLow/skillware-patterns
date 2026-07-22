# Investment Memo Builder

This standalone Composite sample assembles an investment memo from market,
financial, competition, and risk analysis Skills. Atomic sections and the root
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
no network, and imports no shared pattern code. It validates serialized node
references recursively, preserves declared child order, and does not mutate
the parsed workflow. Invalid schemas, kinds, result contracts, duplicate IDs,
missing nodes, Leaf children, and cycles fail with deterministic messages.

The JSON workflow is a node registry plus child references; the directory
layout itself is not the Composite relation. The relation comes from uniform
Component results and validated part-whole traversal.
