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
wrapped Component another copy.

## Result

Every Component returns one JSON object with exactly these top-level fields,
canonically serialized in this order:

1. `summary`: a non-blank string of at most 500 Unicode code points.
2. `findings`: an array of at most 100 finding objects.

Each finding has exactly `type` and `message` in that canonical member order.
Both values are non-blank strings of at most 200 Unicode code points. Lone
surrogates are invalid anywhere in the result. Incoming member order is
irrelevant; wrappers copy and canonicalize every valid wrapped result. Finding
array order is semantic and must be preserved.

## Wrapper collaboration

A Decorator accepts any callable implementing `contract-review-v1` and itself
implements the same contract. It validates and copies the request, invokes the
wrapped Component exactly once, validates and copies the result, then appends
only its own bounded finding when applicable. It never mutates caller input,
the wrapped Component's result, or nested finding objects. It propagates the
wrapped Component's exception unchanged and never synthesizes a partial result.

Composition is declared inside-to-outside. For `privacy, citation`, the
effective Component is
`with_citation_check(with_privacy_check(base_review))`. Base findings appear
first, followed by the privacy finding, then the citation finding. Reversing
the declared order reverses the two enhancement findings without changing the
request or result shape.

## Scope

The base summary and the email/`[missing]` checks are deterministic test
oracles. They do not perform legal analysis, prove personal-data handling
compliance, or verify real citations. Python models the participant
collaboration and does not interpret the natural-language Skills.
