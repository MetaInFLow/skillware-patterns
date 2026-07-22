# State

**Canonical source.** State is the behavioral pattern described in the Gang of
Four tradition by Gamma, Helm, Johnson, and Vlissides in *Design Patterns:
Elements of Reusable Object-Oriented Software* (1994). This record transfers
that established pattern; it does not claim invention or historical priority.

## Intent

Allow a Context to change its behavior when its internal State changes by
delegating state-dependent requests to the current State object.

## Forces

- Vendor verification, approval, and activation permit different actions and
  produce different results, but callers need one stable workflow interface.
- Legal-transition rules need one owner; duplicating them in callers or a
  Context conditional makes lifecycle changes hard to audit.
- The workflow must survive process restart without reconstructing state from
  conversation or activity labels.
- Persistence must not advance when an action is illegal or a successor write
  fails.
- Corrupted state must remain visible instead of being silently reset to a
  plausible phase.
- Explicit state objects add artifacts and migration duties to a small acyclic
  lifecycle that could otherwise be represented more compactly.

## Participants

- **Context:** the root Vendor Onboarding Workflow Skill and deterministic
  `VendorWorkflow`. It exposes one transition operation, reloads persisted
  state, delegates behavior, and atomically commits a legal successor.
- **State:** the `vendor-onboarding-state-v1` `handle-action` contract used by
  every state implementation.
- **ConcreteState:** the draft, verified, approved, and activated child Skills
  and corresponding Python classes. Each owns its permitted action, successor,
  and state-specific result.
- **Agent Host and Agent Runtime:** execution context, not GoF State
  participants. Their activation and interpretation behavior is not observable
  in this constructive sample.

## Collaboration

The Context reloads and validates the versioned record before each action, then
invokes `handle` on the recovered ConcreteState. Draft alone accepts `verify`,
verified alone accepts `approve`, approved alone accepts `activate`, and
activated accepts nothing. The ConcreteState either rejects before any write or
asks the Context to atomically persist its nominated successor. The Context
updates its in-memory State only after replacement succeeds. A fresh Context
recovers the same persisted State after restart. Initial Context construction
is the explicit bootstrap boundary and may create `draft` if the record is
absent; disappearance during a later reload is corruption and never silently
creates a replacement workflow.

## Consequences

State-dependent behavior and legal transitions are localized, callers use one
stable interface, and durable recovery is explicit. Illegal paths become
deterministic and testable. Costs include one artifact per state, state-schema
migration, terminal-state policy, persistence failure handling, and concurrency
control when more than one writer is introduced.

## Skillware Mapping

Natural-language Behavioral Source defines the Context protocol, common State
operation, and four ConcreteState responsibilities. The root and child Skill
Artifacts form one coherent Skillware Unit. JSON fixtures supply state and
actions; standard-library Python is a deterministic oracle for delegation and
persistence. It does not activate or interpret the Skill files.

### Final ontology

The canonical roles remain exactly **Context**, **State**, and
**ConcreteState**. `Agent Host` activates a Skillware Unit and `Agent Runtime`
interprets activated Behavioral Source, but neither contextual object becomes
a source-pattern participant. An Execution Trace records situated performance
and Task Outcome is the evaluated effect; this static sample fabricates neither.

## Applicability

Use State when one long-lived workflow has an explicit lifecycle, the current
state changes which actions and results are possible, and later work must
recover that state. It fits approval, provisioning, publication, fulfillment,
and incident lifecycles when transitions have distinct owned behavior.

## Non-Applicability

Do not use State for interchangeable stateless algorithms; that is Strategy.
Do not introduce state objects for passive labels that never alter behavior,
or for a short fixed pipeline with no persisted lifecycle. A database status
column alone is insufficient when callers still own all transition branches.

## Positive Evidence

The repository sample is **constructive** evidence. It materializes all three
GoF roles, four distinct ConcreteState handlers, three owned transitions,
versioned persisted state, atomic replacement, reload before action, restart
recovery, missing-record and corruption validation, and rejection before write.
Focused tests also prove exact outputs, deterministic reruns, input
immutability, non-UTF-8 rejection, and failed-write memory/disk consistency.

## Counter-Evidence

The Python oracle cannot prove that an Agent Runtime interprets the Behavioral
Source identically or that a compatible Agent Host activates it. The sample is
single-writer and local; it has no locking, compare-and-swap, distributed
transaction, external evidence verification, authorization, rollback, or state
schema migration implementation.

## False Positives

Phase words in conditional prose are not State when no record is persisted,
the current phase does not own behavior, and restart recovery is undefined. A
lookup table can validate transitions but does not by itself materialize claimed
ConcreteState responsibilities. The [`misuse/SKILL.md`](misuse/SKILL.md)
artifact deliberately demonstrates the conditional-text near miss.

## Open-Source Correspondence

OpenMontage is a **candidate correspondence** at commit
`db91727598d08d40919d7d68a47864a5467bd448`. Its checkpoint library persists
stage and status, derives the next stage from completed checkpoints, and the
checkpoint protocol changes resume behavior for `in_progress` and
`awaiting_human`. The reviewed paths do not define separate State and
ConcreteState participants or Context-to-State delegation, so this is not a
confirmed GoF mapping. See [`correspondence.md`](correspondence.md) and the
[frozen evidence](evidence/openmontage-frozen-case.md).

## Verification

From `sample/`, run `python3 scripts/run_demo.py` and `python3 -m unittest
discover tests -v`. Verification covers the full action sequence, persisted
reload after every step, approved-state restart recovery, per-state handler
ownership, illegal-transition no-write, atomic replacement failure, missing and
corrupted state, invalid UTF-8, non-string state values, vendor identity
mismatch, exact fixture outputs and errors, deterministic reruns, and standalone
standard-library execution without network access.

## Limitations

One constructive scenario does not establish prevalence, comparative benefit,
production durability, or cross-Host behavioral equivalence. The acyclic
revision rule is scenario-specific. Adding correction, suspension, offboarding,
or retries requires explicit new states, transitions, persistence semantics,
and tests rather than conversational inference.
