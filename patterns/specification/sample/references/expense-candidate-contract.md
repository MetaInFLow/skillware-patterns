# Expense Candidate Contract

`expense-approval-policy-v1` binds named DDD Specifications to one exact
Candidate mapping. It is the contract for both direct API and CLI evaluation.

## Candidate

The default policy accepts exactly:

```json
{
  "receipt": true,
  "budget": 500,
  "amount": 400,
  "department": "sales"
}
```

`receipt` is a JSON/Python boolean. `budget` and `amount` are non-negative
integers no greater than 1,000,000,000. Python `bool` is rejected as an integer;
floats, NaN, and infinity are rejected. An integration must declare the integer
currency unit and should use cents. No conversion or rounding occurs.

`department` is a non-blank Unicode string of at most 128 UTF-8 bytes. It is
normalized to NFC and compared case-sensitively. Candidate values are copied
into a fresh admitted mapping; the caller's mapping is never mutated.

Every Specification exposes its required fields. A composed policy admits
exactly the ordered union of those fields, not always all four default fields.
Missing and extra fields are errors. Complete schema, type, bound, Unicode, and
depth validation happens before the first rule, including before a branch that
would otherwise short-circuit.

## Specifications

- `HasReceipt` requires `receipt is True`.
- `WithinBudget` requires `amount <= budget`.
- `AuthorizedAmount(maximum)` requires `amount <= maximum`.
- `Department(expected)` requires NFC-normalized exact department equality.

Leaf and composite objects are immutable after construction. Configuration is
validated immediately. Only Specification instances can be combined.

## Composite Specifications

`A & B` creates And, `A | B` creates Or, and `~A` creates Not. AND and OR use
left-to-right short-circuit evaluation; NOT evaluates its one child. Operator
precedence follows Python: `~` before `&` before `|`. Parenthesize mixed
expressions when policy intent could be unclear.

`is_satisfied_by(candidate)` validates once and returns only `bool`.
`explain(candidate)` uses the same short-circuit behavior and lists skipped
branches. `explain(candidate, evaluate_all=True)` evaluates every leaf and
lists none as skipped. All-evaluation does not redefine the boolean result and
is permitted only because every rule is deterministic, pure, and side-effect
free. No mode mutates the Candidate or a Specification.

## CLI input

The CLI reads at most 65,536 bytes, decodes strict UTF-8, rejects duplicate JSON
members at every depth and all non-finite numeric constants, and enforces a
maximum parsed nesting depth of 16. It prints one deterministic JSON trace.
Exit status is 0 for true, 1 for false, and 2 for input/configuration errors.

## Trusted-code boundary

The oracle is sequential trusted Python in one process. Frozen dataclasses
prevent ordinary mutation but are not a security boundary against reflection
or a hostile module. The sample does not provide authorization identity,
currency conversion, persistence-query translation, policy version migration,
audit durability, Agent Host activation, or Agent Runtime interpretation.
