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
   missing or extra fields before evaluating any Specification. Preserve each
   field's first left-to-right occurrence when combining declarations.
2. Require `receipt` to be a boolean. Require budget and amount to be integers
   from 0 through 1,000,000,000; reject booleans, floats, NaN, and infinity.
   Treat the integer currency unit as integration-defined and prefer cents.
3. Apply Unicode NFC to a non-blank department of at most 128 UTF-8 bytes and
   compare it case-sensitively.
4. Compose only registered immutable built-ins, composites, and `Predicate`
   wrappers. Reject bare `Specification` and arbitrary subclasses before
   composition or evaluation. A custom Predicate declares an explicit name,
   1-32 ordered required fields, an evaluator, and an explanation callable.
5. Validate custom fields as bounded JSON-compatible data and deep-copy them
   for each Predicate callable. Strings are at most 4,096 UTF-8 bytes,
   collections at most 128 items, numeric absolute values at most
   1,000,000,000, and the admitted Candidate at most 65,536 UTF-8 bytes.
6. AND and OR evaluate left-to-right with short-circuit boolean semantics; NOT
   evaluates its one child. `is_satisfied_by` returns only `bool`. For
   diagnostics, use `explain` in short-circuit mode or evaluate all leaves.
   All-evaluation is valid only because every Specification is pure.
7. For CLI input, read no more than 65,537 bytes to enforce the 65,536-byte cap.
   Emit ASCII-safe JSON so Unicode Candidates work under restrictive locales.

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
Predicate evaluator and explanation callables receive deep copies, but are
trusted deterministic and pure code only by contract; closures, reflection,
and external side effects are not sandboxed.

## Anti-pattern

One opaque monolithic eligibility function whose rules cannot be named,
combined, explained, or reused is not Specification. See `../misuse/SKILL.md`.
