# Risk-Aware Code Review Strategy Contract

Contract: `risk-aware-code-review-v1`

Operation: `review`

## Request

Every ConcreteStrategy accepts one UTF-8 JSON object with fields in this order:

| Field | Type | Rule |
| --- | --- | --- |
| `schema` | string | Exactly `risk-aware-code-review-request-v1`. |
| `review_id` | string | Non-empty, at most 64 characters. |
| `security_sensitive` | boolean | `true` or `false`; strings and integers are invalid. |
| `files` | array | Between 1 and 50 unique changed-file records. |

Each file record contains exactly `path` and `additions`, in that order. `path`
is a non-empty relative POSIX path of at most 240 characters, without `.` or
`..` segments or backslashes. `additions` contains at most 200 strings; each
line contains at most 500 characters. Unknown fields, duplicate paths, invalid
UTF-8, and malformed JSON are rejected before selection or review.

## Selection

The Context selects `deep-review` when `security_sensitive` is `true`. If not,
it selects `deep-review` when the request contains at least four files. Every
other valid request selects `fast-scan`. Security sensitivity has precedence
when both rules match.

A caller may directly address `fast-scan` or `deep-review` for audit, replay,
or conformance testing. Direct addressing changes only the procedure, never the
request or result interface. Unknown strategy identifiers are rejected.

## Result

Every ConcreteStrategy returns one JSON object with fields in this order:

1. `schema`: exactly `risk-aware-code-review-result-v1`.
2. `review_id`: exactly the request identity.
3. `strategy`: `fast-scan` or `deep-review`.
4. `reviewed_files`: every requested path, exactly once and in request order.
5. `findings`: ordered finding records.
6. `summary`: counts derived from the requested files and findings.

Each finding contains exactly `rule_id`, `severity`, `path`, `line`, and
`message`, in that order. Severity is `high`, `medium`, or `low`; path and line
must identify an added request line. Summary contains exactly `files_reviewed`,
`findings`, `high`, `medium`, and `low`, in that order. The Context validates
the complete result after every delegated call, including injected strategies.

## Procedures

Fast Scan applies the three high-signal rules `dynamic-execution`,
`hardcoded-secret`, and `insecure-tls`. Deep Review applies those same rules
plus `sql-concatenation`, `authorization-bypass`, and `wildcard-permission`.
Both traverse files, lines, and rules in declared order, so output is stable.

The rule set is a deterministic demonstration, not a production security
scanner. No network, repository checkout, model, Agent Host, or Agent Runtime
is required. Python models contract conformance and delegation; it does not
interpret the Skill files.
