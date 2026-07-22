---
name: opaque-expense-eligibility-misuse
description: Put all expense checks in one opaque eligibility function. Use only to study why a monolith is not the Specification pattern.
intent: Demonstrate absent named rules, composition, reuse, exact Candidate admission, and structured explanations.
type: component
---

# Opaque Eligibility Misuse / 不透明资格函数误用

Implement receipt, budget, authority, and department checks inside one
`eligible(expense)` function. Give callers only one boolean and let missing
fields, numeric coercion, and evaluation order follow incidental language
behavior. Expose no independently named rules and no AND/OR/NOT composition.

This opaque monolithic eligibility function is not the DDD Specification
pattern.

这种单体资格函数没有可独立命名、组合与复用的规约，不属于 DDD
Specification 模式。
