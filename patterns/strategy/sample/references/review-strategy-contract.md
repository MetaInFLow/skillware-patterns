# Risk-Aware Code Review Strategy Contract

Contract: `risk-aware-code-review-v1`

Operation: `review`

## Plan compatibility API

The module-level `review({"files": int, "security_sensitive": bool})` function
preserves the exact compact implementation-plan surface. It selects
`deep-review` when `security_sensitive` is true or `files` is greater than 5;
otherwise it selects `fast-scan`. It returns exactly `strategy`, `findings`,
and `confidence`, canonically in that serialization order. After selection,
`review` invokes exactly one `fast_scan(change)` or `deep_review(change)`
callable; both implement that exact compact result contract. Optional injected
callables support isolated selection/delegation tests, and default functions are
resolved at call time so they can also be patched. `files` must be a non-negative
integer and cannot be a boolean. This compact API is separate from the richer
changed-file contract and CLI below; their request and result objects must not
be substituted for each other.

## Request

Every rich ConcreteStrategy accepts one UTF-8 JSON object with exactly these
fields. JSON object-member order is semantically irrelevant:

| Field | Type | Rule |
| --- | --- | --- |
| `schema` | string | Exactly `risk-aware-code-review-request-v1`. |
| `review_id` | string | Non-empty, at most 64 characters. |
| `security_sensitive` | boolean | `true` or `false`; strings and integers are invalid. |
| `files` | array | Between 1 and 50 unique changed-file records. |

Each file record contains exactly `path` and `additions`; their JSON member order
is semantically irrelevant. `path`
is a non-empty relative POSIX path of at most 240 characters, without `.` or
`..` segments or backslashes. `additions` contains at most 200 strings; each
line contains at most 500 characters. Unknown fields, duplicate paths, invalid
UTF-8, lone Unicode surrogates, malformed JSON, and duplicate JSON object
members at any depth are rejected before selection or review.

## Rich selection

The Context selects `deep-review` when `security_sensitive` is `true`. If not,
it selects `deep-review` when the request contains at least four files. Every
other valid request selects `fast-scan`. Security sensitivity has precedence
when both rules match.

A caller may directly address `fast-scan` or `deep-review` for audit, replay,
or conformance testing. Direct addressing changes only the procedure, never the
request or result interface. Unknown strategy identifiers are rejected.

## Result

Every rich ConcreteStrategy returns one JSON object with exactly these fields.
Incoming object-member order is semantically irrelevant; the Context emits the
fields in the canonical order shown here:

1. `schema`: exactly `risk-aware-code-review-result-v1`.
2. `review_id`: exactly the request identity.
3. `strategy`: `fast-scan` or `deep-review`.
4. `reviewed_files`: every requested path, exactly once and in request order.
5. `findings`: ordered finding records.
6. `summary`: counts derived from the requested files and findings.

Each finding contains exactly `rule_id`, `severity`, `path`, `line`, and
`message`. Their incoming member order is irrelevant and their emitted member
order follows that list. Severity is `high`, `medium`, or `low`; path and line
must identify an added request line. Finding identity is `(rule_id, path,
line)` and must be unique. The Context canonically orders findings by request
file, line, then rule identifier.

Summary contains exactly `files_reviewed`, `findings`, `high`, `medium`, and
`low`. Every count is a non-negative integer, never a boolean or float, and must
equal the counts derived from the request and findings. The selected strategy
identifier must be a string. The Context validates and canonicalizes the
complete shared result after every delegated call, including injected
strategies. It does not inspect an injected procedure or require it to use a
built-in lexical rule.

## Procedures

The built-in Fast Scan applies the three high-signal rules `dynamic-execution`,
`hardcoded-secret`, and `insecure-tls`. Deep Review applies those same rules
plus `sql-concatenation`, `authorization-bypass`, and `wildcard-permission`.
Both traverse files, lines, and rules in declared order, so output is stable.
Built-in procedure tests own these assertions separately from Context
substitution tests. A custom injected strategy can use another deterministic
review algorithm as long as it satisfies the shared result contract, unique
finding identity, and canonical ordering boundary.

The rule set is a deterministic demonstration, not a production security
scanner. No network, repository checkout, model, Agent Host, or Agent Runtime
is required. Python models contract conformance and delegation; it does not
interpret the Skill files.
