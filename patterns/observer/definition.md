# Observer

**Canonical source.** Observer is the behavioral pattern described in the Gang
of Four tradition by Gamma, Helm, Johnson, and Vlissides in *Design Patterns:
Elements of Reusable Object-Oriented Software* (1994). This record transfers
that established pattern; it does not claim a new pattern or historical
priority for Skillware.

## Intent

Define a one-to-many dependency so that when one Subject changes state, all of
its registered Observers are notified and updated through a common operation.

## Forces

- Release publication has several independent reactions, but the release
  workflow should not branch on audit, changelog, or notification internals.
- Consumers need independent lifecycle ownership, including explicit
  registration and unregistration.
- Predictable order aids verification, while ordered synchronous delivery can
  increase latency and expose ordering dependencies.
- One consumer can fail without making later consumers invisible, yet partial
  delivery then requires explicit accounting and recovery policy.
- Event schemas need versioning so Subject and Observers can evolve without
  accidental payload coupling.
- A consumer can trigger nested work; publication needs a re-entry rule to
  prevent recursion and duplicated side effects.

## Participants

- **Subject:** the release event source and ordered subscription owner. It
  exposes `register`, `unregister`, and `publish` behavior.
- **Observer:** the `release-observer-v1` contract. Its `update(event)` operation
  accepts one exact `release.published.v1` event and returns a receipt or fails.
- **ConcreteSubject:** the root Software Release Notification Skill together
  with the deterministic `ReleaseSubject` oracle. It publishes after a
  successful release transition and accounts for every attempted Observer.
- **ConcreteObserver:** the audit, changelog, and team-notification consumer
  Skills. Each implements the same update contract and remains separately
  inspectable.
- **Agent Host and Agent Runtime:** execution context, not GoF Observer
  participants. Their activation and interpretation behavior is not observable
  in this constructive sample.

## Collaboration

Before publication, the ConcreteSubject applies explicit registration and
unregistration operations in declared order. It validates release facts,
constructs one typed event, freezes the active insertion-order snapshot, and
calls each Observer once with an isolated copy. A successful Observer returns a
non-empty receipt. An exception or invalid receipt creates a failed delivery
record, after which the ConcreteSubject continues. Nested publication and
subscription mutation during delivery are rejected.

## Consequences

The release workflow and its consumers can evolve independently under a stable
event contract, and consumers can join or leave without consumer-specific
branches in the Subject. Deterministic order and per-observer records make
partial delivery visible. Costs include subscription ownership, schema
evolution, fan-out latency, partial-failure recovery, possible ordering
dependencies, duplicate-delivery risks in durable systems, and the need for
idempotency when retries are later introduced.

## Skillware Mapping

Natural-language Behavioral Sources define the root publication policy and the
three consumer update behaviors. The root and child Skill Artifacts form the
constructive Skillware Unit's coherent Skill suite. The JSON fixture declares
release state and subscription operations; support code supplies a deterministic
oracle for the collaboration. Python does not activate or interpret the Skill
behavioral source.

### Final ontology

The canonical roles remain exactly **Subject**, **Observer**,
**ConcreteSubject**, and **ConcreteObserver**. `Agent Host` activates a
Skillware Unit and `Agent Runtime` interprets activated Behavioral Source, but
those contextual objects do not become source-pattern participants. An
Execution Trace or Task Outcome can provide runtime evidence later; neither is
fabricated by the static sample.

## Applicability

Use Observer when one published lifecycle change must notify a variable set of
independent consumer Skills through one typed contract, and when the Subject
must not know each consumer's internal work. It fits audit, indexing,
notification, cache invalidation, and derived-artifact reactions when explicit
subscription and partial-delivery policies are acceptable.

## Non-Applicability

Do not use Observer for a fixed mandatory transaction in which every action
must commit atomically, for request/response work that needs one result, or for
a simple linear workflow whose steps intentionally depend on previous outputs.
Use a transactional coordinator, direct call, or pipeline respectively. A
filesystem scan or undirected broadcast is also not Observer.

## Positive Evidence

The repository sample is **constructive** evidence. It materializes all four
GoF roles, the exact versioned event, three registered consumer Skills,
registration-order delivery, explicit unregistration, per-observer receipts,
failure isolation, event-copy isolation, and re-entry rejection. Focused tests
also prove deterministic reruns, input immutability, strict validation, and
exact CLI outputs and errors.

## Counter-Evidence

The deterministic functions do not prove that an Agent Runtime will interpret
the natural-language Skills identically or that a compatible Agent Host will
activate them. Delivery is synchronous and in-memory; the sample has no durable
queue, retry, deduplication, timeout, backpressure, crash recovery, or
transactional outbox. A delivered receipt only means the update function
returned successfully in this oracle.

## False Positives

Polling a release file is not Subject-driven notification. Broadcasting to all
discovered endpoints without managed registration is not the GoF one-to-many
dependency either. Hook names, event labels, or arrays of commands remain
navigational evidence until the common update operation and participant
collaboration are established. The [`misuse/SKILL.md`](misuse/SKILL.md)
artifact intentionally combines polling and unregistered broadcast as a near
miss.

## Open-Source Correspondence

ECC is evaluated at commit `2bc924faf2f8e893bfe0af86b1931283693c30ae`.
Its hook manifest, runner, tests, and continuous-learning-v2 artifacts provide
partial source evidence for event-triggered independent behavior. The claim is
only **candidate correspondence**: the pinned paths do not establish a common
Observer update contract, explicit observer-level registration and
unregistration, deterministic delivery of all matches, or per-observer failure
accounting. See [`correspondence.md`](correspondence.md) and the local frozen
evidence audit.

## Verification

From `sample/`, run `python3 scripts/run_demo.py` and `python3 -m unittest
discover tests -v`. Verification checks exact output, all three registered
Observers in insertion order, unregistration, isolated failure with continued
delivery, nested-publication rejection, event-copy isolation, deterministic
reruns, input immutability, exact fixture errors, pinned evidence paths, and
standalone standard-library execution without network access.

## Limitations

One constructive scenario and one candidate ecosystem correspondence do not
establish prevalence, comparative benefit, production robustness, or
cross-Host behavioral equivalence. The mapping preserves the canonical GoF
intent and roles without claiming Skillware invented Observer, that every hook
system implements Observer, or that notification guarantees consumer-side
transaction completion.
