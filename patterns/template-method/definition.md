# Template Method

**Canonical source.** Template Method is the behavioral pattern described in
the Gang of Four tradition by Gamma, Helm, Johnson, and Vlissides in *Design
Patterns: Elements of Reusable Object-Oriented Software* (1994). This record
transfers that established pattern; it does not claim invention or historical
priority.

## Intent

Define the skeleton of an algorithm in an AbstractClass operation, deferring
selected operations to ConcreteClasses without letting them change the
algorithm's structure.

## Forces

- Every enterprise RFP must extract requirements, analyze gaps, apply domain
  expertise, draft a response, and complete quality review in one auditable
  order.
- Healthcare and financial-services responses need different focus areas and
  evidence, but duplicating the whole workflow would let mandatory stages
  drift.
- A domain extension must have enough context to specialize the response while
  remaining unable to skip, repeat, or reorder mandatory work.
- Hook failure and malformed hook output must stop later work predictably;
  otherwise a draft could appear complete without validated domain input.
- Input, hook output, and final result boundaries need deterministic validation
  because model-mediated or file-supplied data can be malformed.
- A rigid skeleton reduces extension freedom and can become hard to understand
  if too many hooks are introduced.

## Participants

- **AbstractClass:** the root Enterprise RFP Response Skill and deterministic
  `RfpResponseTemplate`. It owns the `run-rfp` Template Method, implements all
  mandatory operations, and invokes the sole overridable operation once.
- **ConcreteClass:** the Healthcare and Finance child Skill Artifacts and
  corresponding Python subclasses. Each implements only
  `apply-domain-hook` through `rfp-domain-hook-v1`.
- **Agent Host and Agent Runtime:** execution context, not GoF Template Method
  participants. Their activation and interpretation behavior is not observable
  in the constructive sample.

Primitive operations and the Template Method are operations owned or
implemented by these two canonical participants; they are not extra participant
roles.

## Collaboration

The AbstractClass validates one request, extracts requirement ids, analyzes
gaps, builds an isolated hook request, and invokes the selected ConcreteClass
exactly once. It validates and copies the hook result before drafting, then
runs the quality check and validates the complete result. A ConcreteClass can
return only domain focus and required evidence. The oracle rejects a subclass
that attempts to override the template method or any mandatory operation. A
hook exception propagates unchanged and drafting and quality review do not run.

## Consequences

One root owns policy order, domain variants share mandatory behavior, and the
extension boundary is testable. Adding a domain requires only one conforming
ConcreteClass. Costs include root-to-child coupling, contract versioning, a
deliberately narrow extension surface, and coordinated changes when the
invariant skeleton itself evolves.

## Skillware Mapping

Behavioral Source defines and informs the root and child Skill Artifacts. The
root file specifies the AbstractClass algorithm and the child files specify the
two ConcreteClass operations. These artifacts and their contract form one
coherent Skillware Unit. JSON fixtures provide requests; standard-library
Python is a deterministic oracle for order and boundary behavior, not an Agent
Runtime interpreter.

### Final ontology

The canonical GoF roles remain exactly **AbstractClass** and
**ConcreteClass**. A Behavioral Source is persisted in a Skill Artifact carried
by a Skillware Unit. An Agent Host activates that unit and an Agent Runtime
interprets activated Behavioral Source in context, but neither contextual
object becomes a source-pattern participant. An Execution Trace records
situated performance and Task Outcome is the evaluated effect; this static
sample fabricates neither.

## Applicability

Use Template Method when variants share a meaningful, stable algorithm order
and differ at a small number of declared operations. It fits regulated response
workflows, review protocols, document production, onboarding, and validation
flows where one owner must preserve mandatory gates.

## Non-Applicability

Do not use Template Method when the whole algorithm must be selected at runtime
behind one interchangeable interface; that is Strategy. Do not force it onto
independent checklists with no common invariant, or onto a simple sequence with
no specialization. If extensions need to insert arbitrary stages, use an
explicit pipeline or orchestration model instead.

## Positive Evidence

The repository sample is **constructive** evidence. It materializes both
canonical roles, a five-stage skeleton, two ConcreteClasses sharing one exact
hook contract, once-only hook invocation, subclass override rejection,
stop-on-failure behavior, strict request/hook/result validation, copy isolation,
stable errors, exact fixtures, and deterministic reruns. The literal
`run_rfp("healthcare")` API returns the healthcare domain and exact required
stage list.

## Counter-Evidence

Python language enforcement and tests do not prove that an Agent Runtime will
interpret the Behavioral Source identically or that an Agent Host will activate
the intended artifacts. The domain output is lexical fixture content, not
validated sector expertise. No production RFP system, external evidence source,
authorization, concurrency, retry, redaction, or human approval integration is
present.

## False Positives

A fixed checklist with no overridable operation is only a fixed workflow. A set
of domain profiles that each owns its whole sequence is not Template Method
because no AbstractClass preserves order. A runtime selector for complete
algorithms is Strategy. The [`misuse/SKILL.md`](misuse/SKILL.md) record lets
domains reorder and omit stages to expose this discriminator.

## Open-Source Correspondence

Superpowers is a **candidate correspondence** at commit
`896224c4b1879920ab573417e68fd51d2ccc9072`. Its exact brainstorming and TDD
Skill paths prescribe invariant workflow skeletons. The inspected sources do
not establish bounded domain-hook or ConcreteClass substitution, protection
against specialization reorder, or Agent Runtime behavior, so the claim is not
confirmed. See [`correspondence.md`](correspondence.md) and the
[frozen evidence](evidence/superpowers-frozen-case.md).

## Verification

From `sample/`, run `python3 scripts/run_demo.py` and `python3 -m unittest
discover tests -v`. Verification covers the exact five-stage order, AbstractClass
ownership, once-only hook invocation, two shared-contract ConcreteClasses,
bounded substitution, hook failure, malformed results, deterministic fixtures,
input immutability, output isolation, duplicate JSON members, invalid UTF-8,
lone surrogates, cycles, parser and value depth, wrong types, and stable CLI
errors. The repository root harness exercises the isolated sample automatically.

## Limitations

One constructive RFP scenario does not establish prevalence, comparative
benefit, production safety, or cross-Host behavioral equivalence. Only one
extension operation is modeled. Adding procurement jurisdiction, evidence
retrieval, negotiated exceptions, human review, or output rendering requires
explicit contracts and tests rather than conversational inference.
