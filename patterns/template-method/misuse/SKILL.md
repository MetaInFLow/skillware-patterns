---
name: domain-owned-rfp-checklists
description: Let each domain choose and order its own RFP stages. Use only to demonstrate a workflow with no invariant Template Method skeleton.
intent: Show the Template Method near miss where domain profiles replace mandatory workflow order instead of one bounded operation.
type: workflow
---

# Domain-Owned RFP Checklists

Select a checklist by domain and follow whatever order it declares.

- Healthcare: `draft-response`, `extract-requirements`,
  `apply-domain-policy`, `quality-check`.
- Finance: `extract-requirements`, `draft-response`,
  `apply-domain-policy`; omit quality review when time is short.

Permit new domains to insert, delete, duplicate, or reorder any stage. Each
domain owns its whole response algorithm and output shape. There is no root
workflow that fixes mandatory order and no shared bounded hook contract.
