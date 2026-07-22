# Expense Approval Policy

This standalone sample implements Eric Evans's Domain-Driven Design
Specification pattern for expense approval. It is explicitly not a GoF
pattern.

The default reusable policy requires a receipt, an amount within budget, an
amount no greater than 1,000 authorized units, and a department other than
`restricted`. Root behavior is in [`SKILL.md`](SKILL.md), leaf behaviors are in
[`child-skills/`](child-skills/), and exact Candidate semantics are in
[`references/expense-candidate-contract.md`](references/expense-candidate-contract.md).

Run from this directory:

```bash
python3 scripts/run_demo.py
python3 -m unittest discover tests -v
```

Pass another Candidate path and select a trace mode when needed:

```bash
python3 scripts/run_demo.py fixtures/valid/missing-receipt.json --evaluation short-circuit
```

Exit status is 0 for a satisfied policy, 1 for a valid rejected Candidate, and
2 for invalid input. Output and errors have exact fixtures in [`expected/`](expected/).
