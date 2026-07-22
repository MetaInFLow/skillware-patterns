# Pipes and Filters

**Canonical source.** Pipes and Filters is an architectural pattern in the
Pattern-Oriented Software Architecture tradition described by Buschmann et al.
It is not a Gang of Four pattern. This record preserves the canonical roles
Data Source, Filter, Pipe, and Data Sink.

## Intent

Process a stream of data through independently replaceable transformation
stages connected by explicit channels with a shared data contract.

## Forces

- Triage stages need separate ownership and substitution boundaries.
- Stage order and exactly-once invocation must have one external owner.
- Every boundary must reject invalid records without relying on conversation state.
- Caller input and adjacent stages must not share mutable record aliases.
- Failures must stop processing and identify the responsible stage.

## Participants

- **Data Source:** admits ticket text and creates `support-ticket.v1`.
- **Filter:** normalize, redact, classify, prioritize, or draft; each accepts and
  returns the same record envelope.
- **Pipe:** validates and deep-copies the envelope between stages.
- **Data Sink:** emits the completed record and canonical trace.
- Agent Host and Agent Runtime are execution context, not POSA participants.

## Collaboration

The runner validates the complete Filter set, owns canonical order, and asks
the Data Source for an initial record. A Pipe validates and copies the record
before and after every Filter. The first exception or invalid output stops the
run with stage attribution. The Data Sink validates and detaches final output.

## Consequences

Filters become addressable, testable, and replaceable; intermediate contracts
and failure locations become explicit. Costs include repeated validation and
copying, fixed topology, and the need for separate operational flow policies.

## Skillware Mapping

The root Skill declares topology, five child Skill Artifacts carry Filter
behavior, and the record reference carries the Pipe contract. Fixtures model
Data Source and Data Sink artifacts. The Python oracle demonstrates the local
contract but does not interpret natural-language Skills.

### Final ontology

The source roles remain exactly **Data Source**, **Filter**, **Pipe**, and
**Data Sink**. Behavioral Source is persisted in Skill Artifacts within one
Skillware Unit. Agent Host and Agent Runtime remain contextual; neither is
renamed into a POSA participant.

## Applicability

Use this pattern when processing has stable ordered stages, a common explicit
record can cross each boundary, and stages need independent testing or
replacement. Content processing, compilation, ETL, and triage are common fits.

## Non-Applicability

Do not use it when stages require rich cyclic collaboration, one transaction
must span all steps, or transformations cannot share a practical contract. A
single indivisible operation gains nothing from artificial stage names.

## Positive Evidence

The constructive sample proves the literal `run_pipeline` scenario, five
independent injectable Filters, runner-owned exactly-once order, before/after
Pipe validation, deep-copy transfers, email redaction, high priority,
replaceability, deterministic output, strict admission, and fail-stop errors.

## Counter-Evidence

The oracle is sequential trusted code in one process. It does not prove Agent
Runtime interpretation, Host activation, security isolation, production
throughput, distributed cancellation, or durable delivery.

## False Positives

A monolithic function falsely called a pipeline is not Pipes and Filters: its
steps cannot be independently addressed or replaced and no explicit Pipe
enforces their contract. A prose checklist using hidden conversation state is
the same false positive. See [`misuse/SKILL.md`](misuse/SKILL.md).

## Open-Source Correspondence

OpenMontage is a **candidate correspondence** at pinned revision
`db91727598d08d40919d7d68a47864a5467bd448`. Its manifest, loader, and stage
Skill paths show declared ordered stages and artifact flow. A common envelope,
isolation, and runtime behavior remain unverified. See
[`correspondence.md`](correspondence.md) and the
[frozen evidence](evidence/openmontage-frozen-case.md).

## Verification

Run `python3 -m unittest discover patterns/pipes-and-filters/sample/tests -v`
from the repository root. The root harness also copies the record to an
isolated directory, runs its focused tests, and executes the default CLI.

## Limitations

The local oracle deliberately excludes buffering, backpressure, concurrency, and network transport.
It also excludes retries, parallel branches, durable
queues, timeouts, authentication, and resource accounting. Those policies must
be explicit in a production pipeline rather than inferred from this sample.
