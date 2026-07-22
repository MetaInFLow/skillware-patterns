# Specification

**Canonical source.** Specification is the domain pattern described by Eric
Evans in *Domain-Driven Design*. It is not a Gang of Four pattern. This record
preserves the canonical roles Specification, Candidate, and Composite
Specifications (And/Or/Not).

## Intent

Express a domain rule as a named, reusable object that can decide whether a
Candidate satisfies it, then compose rules without hiding their meaning.

## Forces

- Expense rules need independent names, tests, and reuse across policies.
- A Candidate must have one exact, bounded input contract before any rule runs.
- Composition must preserve deterministic boolean semantics and clear precedence.
- Decisions need inspectable explanations without changing the boolean API.
- Policy evaluation must not mutate the Candidate or depend on hidden state.

## Participants

- **Specification:** a named rule with `is_satisfied_by(candidate) -> bool`.
- **Candidate:** the expense mapping evaluated against a Specification.
- **Composite Specifications:** And, Or, and Not objects that combine other
  Specifications while retaining the same interface.
- Agent Host and Agent Runtime are execution context, not DDD participants.

## Collaboration

The caller composes immutable leaf Specifications into a reusable policy. The
policy first validates exactly the union of Candidate fields required by its
leaves. Boolean evaluation then proceeds left-to-right with short-circuit
semantics. `explain` can either retain that trace or evaluate every pure leaf
for a complete diagnostic; both modes return the same policy result.

## Consequences

Domain rules become named, independently testable, reusable, and explainable.
Composition avoids duplicating policy logic. Costs include more small objects,
explicit schema governance, and the need to define evaluation and explanation
semantics instead of relying on incidental language behavior.

## Skillware Mapping

The root Skill Artifact carries the reusable approval policy. Four child Skill
Artifacts carry the leaf Specification behaviors, and the reference document
carries the exact Candidate and composition contract. Together they form one
Skillware Unit. The Python oracle demonstrates the local contract but does not
interpret natural-language Skills.

### Final ontology

The complete context is **Behavioral Source -> Skill Artifact -> Skillware Unit
-> Agent Host -> Agent Runtime -> Execution Trace -> Task Outcome**. The DDD
roles remain exactly **Specification**, **Candidate**, and **Composite
Specifications**; Agent Host and Agent Runtime are contextual and are not
renamed into pattern participants.

## Applicability

Use Specification when domain decisions must be independently named, combined,
reused, tested, or explained over bounded Candidate data.

## Non-Applicability

Do not use it for inherently state-changing commands, an unbounded judgment
that cannot be expressed as a stable rule, or a single trivial check with no
reuse or composition need. Persistence-query translation is a separate design
boundary.

## Positive Evidence

The constructive sample proves the literal receipt, budget, authority, and
department examples; immutable leaf and composite objects; AND/OR/NOT truth
behavior; exact Candidate validation; bounded integer amounts; deterministic
pure evaluation; short-circuit and all-evaluation explanations; and stable CLI
errors for malformed inputs.

## Counter-Evidence

No frozen external implementation is assessed, so an ecosystem Specification
relationship is **not observable**. The local sample is constructive only. It
does not prove Agent Host activation, Agent Runtime interpretation, production
policy fitness, persistence translation, or cross-Host equivalence.

## False Positives

One opaque `eligible(expense)` function containing every rule is not this
pattern when its criteria cannot be independently named, combined, explained,
or reused. A prose instruction such as "ensure expenses are valid" is also not
a Specification. See [`misuse/SKILL.md`](misuse/SKILL.md).

## Open-Source Correspondence

**Status: not observable.** This record does not invent or assess an ecosystem
project. The repository sample demonstrates construction, not external
correspondence. See [`correspondence.md`](correspondence.md).

## Verification

Run `python3 -m unittest discover patterns/specification/sample/tests -v` from
the repository root. The root harness also asserts materialization, copies the
record into isolation, runs its focused tests, and executes the default CLI.

## Limitations

Amounts are non-negative integers from 0 through 1,000,000,000; integrations
must choose and document their currency unit, normally cents. Floats, NaN,
infinity, and booleans-as-integers are rejected. Department equality is
case-sensitive after NFC normalization. Rule objects and the evaluator are
pure by contract, but Python modules and callables are trusted code, not a
security sandbox; reflection can bypass ordinary immutability boundaries.
