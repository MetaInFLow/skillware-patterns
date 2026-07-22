---
name: expense-approval-policy
description: Evaluate reusable composable expense rules. Use when receipt, budget, authority, and department decisions need exact explainable policy.
intent: Apply immutable DDD Specifications to one bounded Candidate with deterministic AND, OR, NOT, and structured explanations.
type: workflow
---

# Expense Approval Policy / 费用审批规则

## Trigger

Use this root Skill to evaluate one expense Candidate under
[`expense-approval-policy-v1`](references/expense-candidate-contract.md).

## 中文触发约定

当费用决策需要精确输入、可复用命名规则、AND/OR/NOT 组合和可检查解释时，
使用本根 Skill。

## DDD participants

This is Eric Evans's Domain-Driven Design Specification pattern, not a Gang of
Four pattern. The canonical roles are Specification, Candidate, and Composite
Specifications (And/Or/Not). Agent Host and Agent Runtime are execution
context, not pattern participants.

## Agent mode

1. Admit exactly the fields required by the composed policy. For the default
   policy these are `receipt`, `budget`, `amount`, and `department`; reject all
   missing or extra fields before evaluating any Specification.
2. Require `receipt` to be a boolean. Require budget and amount to be integers
   from 0 through 1,000,000,000; reject booleans, floats, NaN, and infinity.
   Treat the integer currency unit as integration-defined and prefer cents.
3. Apply Unicode NFC to a non-blank department of at most 128 UTF-8 bytes and
   compare it case-sensitively.
4. Compose only immutable named Specification objects. AND and OR evaluate
   left-to-right with short-circuit boolean semantics; NOT evaluates its one
   child. Do not mutate the Candidate or use hidden state.
5. `is_satisfied_by` returns only `bool`. For diagnostics, use `explain` in
   short-circuit mode or evaluate all leaves. All-evaluation is valid only
   because every admitted Specification is pure and side-effect free.

The concrete reusable default policy is:

```python
HasReceipt() & WithinBudget() & AuthorizedAmount(1000) & ~Department("restricted")
```

## Demo mode and root harness

The standard-library oracle models local deterministic policy evaluation; it
does not interpret these Skill files. From `sample/`, run:

```bash
python3 scripts/run_demo.py
python3 -m unittest discover tests -v
```

The literal API `HasReceipt() & WithinBudget() & AuthorizedAmount(1000)` is
true for `receipt=True,budget=500,amount=400` and false when `receipt=False`.
The literal `~Department('restricted')` is true for department `sales`.

## Ontology and limits

Behavioral Source persists in these Skill Artifacts within one Skillware Unit.
An Agent Host may activate the unit and an Agent Runtime may interpret it to
produce an Execution Trace and Task Outcome; neither runtime relationship is
observed by this local oracle. Python code is trusted and is not a security
sandbox. Persistence-query translation, currency conversion, authorization
identity, and policy version migration are outside this sample.

## Anti-pattern

One opaque monolithic eligibility function whose rules cannot be named,
combined, explained, or reused is not Specification. See `../misuse/SKILL.md`.
