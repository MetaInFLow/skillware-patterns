# Contract Review Component Contract

Contract: `contract-review-v1`

Operation: `review`

## Request

Every Component accepts one JSON object with exactly one field:

| Field | Type | Rule |
| --- | --- | --- |
| `text` | string | Non-blank and at most 10,000 Unicode code points. |

JSON member order is irrelevant. Malformed JSON, invalid UTF-8, duplicate JSON
object members at any depth, lone Unicode surrogates, missing or unknown
fields, wrong types, blank text, and text above the bound are rejected before
delegation. Every wrapper retains its own validated request copy and gives the
wrapped Component another copy. Programmatic mappings with non-string keys,
cyclic values, and values deeper than 64 container levels are rejected through
controlled validation errors. A JSON parser recursion failure is also mapped
to a stable validation error.

## Result

Every Component returns one JSON object with exactly these top-level fields,
canonically serialized in this order:

1. `summary`: a non-blank string of at most 500 Unicode code points.
2. `findings`: an array of finding objects. The shared Component contract has
   no finite finding-count cap, because any valid Component may be wrapped by
   additional valid Decorators.

Each finding has exactly `type` and `message` in that canonical member order.
Both values are non-blank strings of at most 200 Unicode code points. Finding
identity is the exact `(type, message)` pair and every Component result must
contain unique identities. Lone
surrogates are invalid anywhere in the result. Incoming member order is
irrelevant; wrappers copy and canonicalize every valid wrapped result. Finding
array order is semantic and must be preserved.

## Wrapper collaboration

A Decorator accepts any callable implementing `contract-review-v1` and itself
implements the same contract. It validates and copies the request, invokes the
wrapped Component exactly once, validates and copies the result, then appends
only its own bounded finding when applicable and when the identical finding is
not already present. Repeating the same Decorator or wrapping a Component that
already contains that finding is therefore idempotent. It never mutates caller input,
the wrapped Component's result, or nested finding objects. It propagates the
wrapped Component's exception unchanged and never synthesizes a partial result.

Composition uses the manifest's canonical executable identifiers and is
declared inside-to-outside. For `privacy-check, citation-check`, the
effective Component is
`with_citation_check(with_privacy_check(base_review))`. Base findings appear
first, followed by the privacy finding, then the citation finding. Reversing
the declared order reverses the two enhancement findings without changing the
request or result shape. Optional `compliance-check` recognizes the literal
`[noncompliant]` marker and adds one `compliance` finding through the same
contract; it is not part of the exact default plan composition.

## Scope

The base summary and the email/`[missing]` checks are deterministic test
oracles. They do not perform legal analysis, prove personal-data handling
compliance, or verify real citations. Python models the participant
collaboration and does not interpret the natural-language Skills.
