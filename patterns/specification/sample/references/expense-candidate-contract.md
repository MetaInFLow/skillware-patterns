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
exactly their ordered union, preserving each field's first left-to-right
occurrence; it does not always require all four default fields. Missing and
extra fields are errors. Complete schema, type, bound, Unicode, and depth
validation happens before the first rule, including before a branch that would
otherwise short-circuit.

Custom Predicate fields accept JSON-compatible null, booleans, finite numbers,
strings, lists, and string-keyed mappings. Custom strings are at most 4,096
UTF-8 bytes, lists and mappings at most 128 items, and numeric absolute values
at most 1,000,000,000. The complete compact admitted Candidate is at most
65,536 UTF-8 bytes and nesting depth is at most 16. Tuples, arbitrary objects,
non-finite floats, invalid Unicode, oversized values, and cycles are rejected.
Validation creates a recursive copy.

## Specifications

- `HasReceipt` requires `receipt is True`.
- `WithinBudget` requires `amount <= budget`.
- `AuthorizedAmount(maximum)` requires `amount <= maximum`.
- `Department(expected)` requires NFC-normalized exact department equality.

Leaf and composite objects are immutable after construction. Configuration is
validated immediately. The supported implementations are the four built-in
leaves, `Predicate`, And, Or, and Not. Bare `Specification`, mutable subclasses,
and every other unregistered subclass are rejected before composition or
evaluation.

## Predicate extension

`Predicate(name, required_fields, evaluator, explanation)` is the only custom
extension path. Its explicit name is a non-blank valid-Unicode string of at
most 128 UTF-8 bytes. Its ordered declaration contains 1-32 unique non-blank
field names, each at most 128 bytes, and is snapshotted into a tuple. The
evaluator must return an exact boolean. The explanation callable receives the
same Candidate shape and result and must return valid Unicode of at most 4,096
UTF-8 bytes.

Each callable receives a new deep copy, so it cannot alias the caller's
Candidate or another rule's admitted copy through ordinary references.
Callables are nevertheless trusted, deterministic, pure, and side-effect free
only by contract. Closures, globals, I/O, reflection, and hostile code are not
sandboxed. Boolean evaluation does not invoke the explanation callable.

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

The CLI performs one bounded read of 65,537 bytes and rejects the file when the
result exceeds the 65,536-byte cap; it never loads the remainder. It decodes
strict UTF-8, rejects duplicate JSON members at every depth and all non-finite
numeric constants, and enforces a maximum parsed nesting depth of 16. It prints
one deterministic ASCII-safe JSON trace, escaping non-ASCII output so stdout
does not depend on the process locale. Exit status is 0 for true, 1 for false,
and 2 for input/configuration errors.

## Trusted-code boundary

The oracle is sequential trusted Python in one process. Frozen dataclasses,
snapshotted declarations, validation copies, and per-call deep copies prevent
ordinary alias mutation but are not a security boundary against reflection,
closures, external effects, or a hostile module. The sample does not provide
authorization identity, currency conversion, persistence-query translation,
policy version migration, audit durability, Agent Host activation, or Agent
Runtime interpretation.
