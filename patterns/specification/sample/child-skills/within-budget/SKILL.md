---
name: expense-within-budget
description: Compare an expense amount with its budget. Use as a named leaf in a composable expense approval policy.
intent: Return true only when bounded admitted integer amount is no greater than bounded admitted integer budget.
type: component
---

# Within Budget / 预算内

Act as the immutable `WithinBudget` Specification. Require admitted `amount`
and `budget` integers under the root contract, and return `amount <= budget`.
Perform no rounding, conversion, mutation, lookup, or side effect. Explain both
observed integers and their relation.

作为不可变 `WithinBudget` 规约，仅在已校验整数 `amount <= budget` 时返回真。
不舍入、转换或修改 Candidate，解释中列出两个观测值。
