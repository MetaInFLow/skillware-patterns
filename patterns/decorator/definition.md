# Decorator in Skillware

## Intent

Attach a bounded responsibility to a Skill dynamically while preserving the
same Component interface, so callers can use the base Skill, one wrapper, or a
composition of wrappers through the same operation.

## Forces

- A stable core behavior should not be copied or edited for every optional
  cross-cutting check.
- Callers need one request and result contract regardless of enabled checks.
- Individual responsibilities must be independently composable and removable.
- Wrapper order can be operationally significant and therefore must be
  declared and tested.
- Mutable requests and results can create hidden coupling unless ownership is
  isolated at each boundary.
- A wrapper failure policy must remain compatible with the wrapped Component.

## Participants

### Component

Declares the operation and exact request/result contract shared by wrapped and
unwrapped objects. Here it is `contract-review-v1`: `review({text})` returns
exactly `{summary, findings}`.

### ConcreteComponent

Implements the base operation that can stand alone. Base Contract Review
validates contract text and returns a stable base result without enhancement
findings.

### Decorator

Maintains a reference to another Component and implements the same Component
interface. Its common protocol validates and copies the request, delegates
once, validates and copies the result, preserves failure semantics, and exposes
no new required fields.

### ConcreteDecorator

Adds one responsibility before or after delegation while retaining the common
protocol. Privacy Check appends an email finding. Citation Check appends a
missing-marker finding. Both remain valid Components and can wrap the base or
one another.

Agent Host and Agent Runtime are execution context. They are not GoF
participants and are not evidence for the Component/Decorator relation.

## Collaboration

The caller supplies a valid Component request to the outermost decorator. Each
Decorator validates its own request snapshot and calls its wrapped Component
exactly once with a separate copy. Delegation proceeds outside-to-inside until
the ConcreteComponent returns. Results then flow inside-to-outside. Each
ConcreteDecorator validates and copies the complete inner result and appends
only its own finding.

For `with_citation_check(with_privacy_check(base_review))`, the execution path
is Citation to Privacy to Base on entry and Base to Privacy to Citation on
return. Consequently base findings appear first, followed by privacy and then
citation. Reverse nesting produces citation then privacy without changing the
Component contract.

## Consequences

Optional review behavior composes without editing the base Skill. A caller can
substitute a decorated Component through the same operation, and an additional
bounded decorator can be added independently. Focused tests can verify each
responsibility and the common boundary.

The design introduces more participant boundaries and makes nesting order part
of behavior. Repeated validation and copying consume work but prevent mutation
and alias leaks. Unbounded wrapper stacks could repeat checks or obscure
latency. Contract evolution must be versioned across the base and every
decorator.

## Skillware Mapping

| GoF role | Skillware carrier | Constructive artifact |
| --- | --- | --- |
| Component | Shared Skill request/result contract | `sample/references/contract-review-component.md` |
| ConcreteComponent | Base contract-review child Skill | `sample/child-skills/base-contract-review/SKILL.md` |
| Decorator | Contract-preserving wrapper protocol and root composition | `sample/SKILL.md` |
| ConcreteDecorator | Privacy and citation child Skills | `sample/child-skills/privacy-check/SKILL.md`, `sample/child-skills/citation-check/SKILL.md` |

The Python oracle provides callables with the same relationships. Natural-
language Skills are the behavioral source; the oracle verifies the declared
collaboration without claiming to interpret them.

## Applicability

Use Decorator when the base responsibility is stable, optional checks share
its complete interface, multiple checks should compose, and callers should not
need to know whether the Component is wrapped. It is appropriate when wrapper
order and failure policy can be stated precisely and conformance-tested.

## Non-Applicability

Do not use Decorator when the added behavior needs a different request or
result contract, replaces rather than surrounds the base task, coordinates
unrelated peers, selects one interchangeable algorithm, controls access without
adding responsibility, or requires global knowledge of a workflow. A versioned
pipeline or another pattern may fit those forces better.

## Positive Evidence

The constructive sample wraps an injected Component rather than inspecting or
copying it. Exact tests prove the plan-level call
`with_citation_check(with_privacy_check(base_review))`, verify privacy then
citation findings, reverse wrapper order, inject another conforming base,
validate the same fields at every boundary, propagate the identical exception,
and demonstrate request/result alias isolation.

## Counter-Evidence

[`misuse/SKILL.md`](misuse/SKILL.md) copies the base procedure, adds a required
`approval_token`, and returns a mandatory `privacy_approved` field. It neither
holds nor delegates to a Component and cannot substitute for
`contract-review-v1`.

## False Positives

A hook, middleware label, nested directory, or wrapper-shaped prompt is not
automatically Decorator. Logging around a task is insufficient when the logger
changes the public contract or never invokes the original task. A conditional
that chooses between implementations is not Decorator unless its branches are
the result of actual Component wrapping. A copied base prompt plus extra steps
is inheritance-by-copy, not object composition.

## Open-Source Correspondence

**Status: no assessed correspondence.** No public pinned ecosystem case is
assessed for this record. Possible carrier categories in the catalog do not by
themselves establish the complete participant relation. See
[`correspondence.md`](correspondence.md) for the bounded evidence criteria and
constructive claim.

## Verification

From `sample/`, run `python3 scripts/run_demo.py` and `python3 -m unittest
discover tests -v`. Verification covers the literal compatibility API;
Component field preservation; default and reversed decorator order; one-call
delegation; injected Components; bounded match and non-match behavior;
unchanged failure propagation; deterministic output; strict request, result,
finding, UTF-8, surrogate, duplicate-member, type and bound validation; and
input/result immutability. The repository harness copies and runs the sample
standalone.

## Limitations

The sample's email regular expression and literal `[missing]` marker do not
perform production privacy, citation, or legal review. One construction does
not establish ecosystem prevalence, cross-Host equivalence, model
interpretation, production quality, or comparative benefit. Copying values at
the Python boundary models ownership policy but does not prove an Agent Runtime
will enforce it. Findings from separately written decorators may conflict;
resolving such conflicts is outside this contract.
