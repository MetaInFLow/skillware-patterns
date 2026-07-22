# RFP Domain Hook Contract

Contract: `rfp-domain-hook-v1`

Template Method: `run-rfp`

Overridable operation: `apply-domain-hook`

## Invariant skeleton

The AbstractClass alone owns this exact order:

1. `extract-requirements`
2. `analyze-gaps`
3. `apply-domain-hook`
4. `draft-response`
5. `quality-check`

A ConcreteClass supplies only operation 3 as a single-argument `staticmethod`.
The public helpers call `RfpResponseTemplate.run(concrete_class, request)`
explicitly and create no ConcreteClass instance. A ConcreteClass that directly
defines `run`, `_extract_requirements`, `_analyze_gaps`, `_draft_response`, or
`_quality_check` is rejected. The same names inherited through an earlier
multiple-inheritance mixin are never dispatched by the public helpers, so they
are irrelevant to the current execution rather than trusted extension points.

## Root request

The root request is a JSON object with exactly these fields:

| Field | Type | Rule |
| --- | --- | --- |
| `schema` | string | Exactly `enterprise-rfp-v1`. |
| `rfp_id` | string | Non-blank; at most 120 Unicode code points. |
| `domain` | string | Exactly `healthcare` or `finance`. |
| `requirements` | array | 1-200 unique requirement objects. |

Each requirement has exactly `id`, `text`, and `mandatory`. `id` is a
non-blank string of at most 80 characters, `text` is a non-blank string of at
most 2,000 characters, and `mandatory` is a JSON boolean. Requirement id and
array order are semantic.

Malformed JSON, invalid UTF-8, duplicate object members at any depth, lone
Unicode surrogates, unknown or missing fields, wrong types, and exceeded bounds
are rejected before the skeleton begins. Programmatic requests with non-string
mapping keys, cyclic values, or more than 64 container levels are also rejected
through controlled validation errors. Parser recursion failure becomes a
stable validation error.

## Hook request

Every ConcreteClass accepts one copied JSON object with exactly `rfp_id`,
`domain`, `requirements`, and `gaps`. The requirements are the validated root
requirements in original order. `gaps` is an ordered array of unique
requirement ids. The hook may inspect or mutate its private copy, but mutation
cannot affect the caller or AbstractClass state. The implementation keeps RFP
identity, domain, requirements, and the accumulated trace in local immutable
snapshots. Mandatory operations are inline and are not methods or capabilities
available to the hook.

## Hook result

Every ConcreteClass returns a JSON object with exactly these fields in
canonical order:

1. `domain`: the same supported domain as the hook request.
2. `focus_areas`: a non-empty array of at most 100 unique, non-blank strings;
   each string is at most 200 characters.
3. `required_evidence`: the same array contract as `focus_areas`.

The AbstractClass invokes this operation exactly once, validates and copies its
result, then drafts. A malformed result stops the workflow before drafting. A
raised exception propagates unchanged and also stops drafting and quality
checking. No partial result is emitted. Unknown result fields are rejected, so
the hook cannot claim a skip, repeat, insertion, or replacement stage.

## Final result

The result contains exactly `rfp_id`, `domain`, `requirement_ids`, `gaps`,
`domain_result`, `draft`, `quality`, and `stages`. Result validation proves RFP
and domain identity, request-order coverage, bounded domain output, draft
alignment, typed quality data, and the exact invariant stage order. All returned
containers are isolated from caller and ConcreteClass-owned values.

## Scope

The deterministic hook values expose the participant collaboration for tests.
They are not sector assurance, and Python execution is not evidence that an
Agent Runtime interpreted the natural-language Behavioral Source. This
in-process oracle is not a sandbox for arbitrary trusted Python: a hook with
module access could create unrelated process side effects or start an
independent nested workflow. The enforced guarantee is that its only supplied
capability for the current execution is the copied hook request, so it cannot
change that execution's local identity, domain, requirements, trace, or
mandatory dispatch.
