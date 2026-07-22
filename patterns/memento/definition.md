# Memento

**Canonical source.** Memento is the behavioral pattern described in the Gang
of Four tradition by Gamma, Helm, Johnson, and Vlissides in *Design Patterns:
Elements of Reusable Object-Oriented Software* (1994). This record transfers
that established pattern and makes no claim of invention or priority.

## Intent

Without violating encapsulation, capture and externalize an object's internal
state so the object can later be restored to that state.

## Forces

- A configuration migration must be reversible after an attempted write or a
  post-write validation failure, including preservation of byte layout rather
  than only JSON meaning.
- The migration coordinator needs to decide when to capture, restore, or
  discard a checkpoint, but must not inspect or edit Originator state.
- Checkpoints must be tied to one target and one lifecycle so stale or foreign
  state cannot silently overwrite another configuration.
- Atomic replacement prevents partial target content, while permission mode,
  checksum, deterministic serialization, and bounded input make recovery
  auditable.
- If restoration itself fails, the system must expose both the migration and
  restore failures rather than claiming rollback succeeded.
- Exact snapshots increase memory use and do not supply concurrency control,
  authorization, encryption, or durable history by themselves.

## Participants

- **Originator:** the Configuration Originator child Skill and
  `ConfigurationOriginator`. It encapsulates the validated configuration,
  creates Mementos, performs and validates migration, and interprets its own
  opaque checkpoint when restoring.
- **Memento:** `configuration-memento-v1` and `ConfigurationMemento`. It holds
  exact prior bytes plus target, permission, integrity, ownership, and
  lifecycle metadata. It exposes none of that state through its public surface.
- **Caretaker:** the root Configuration Migration Skill, its Caretaker child
  contract, and `MigrationCaretaker`. It owns capture, failure restoration,
  successful disposal, and one-live-checkpoint policy without reading state.
- **Agent Host and Agent Runtime:** execution context, not GoF Memento
  participants. Their activation and interpretation behavior is not observable
  in this constructive sample.

## Collaboration

The Caretaker asks the Originator to create one Memento before any mutation.
The Originator checks that the file is a bounded, regular, non-symlink UTF-8
JSON configuration, retains validated state privately, and creates an opaque
checkpoint containing exact bytes and metadata. Preparation capability-checks
active ownership, target, and checksum, then verifies the target still equals
the capture and renders version `n + 1` without writing. The Originator keeps
that immutable prepared payload in private storage bound to the target, owner
capability, active Memento, token identity, and integrity seal; the Caretaker
receives only an opaque one-use `PreparedMigration` token. A preparation or
conflict failure makes the Caretaker integrity-check, expire, and discard the
checkpoint and outstanding token without restoring, so it cannot overwrite
newer external content. Once mutation is attempted, the Originator revalidates
all bindings, consumes the token before I/O, and applies mode to the open same-directory temporary
file, fsyncs it, atomically replaces the target, fsyncs the directory, and
rereads the file. Any error from that write attempt or post-write validation is
handled conservatively as potentially mutated and invokes exact restore. On
success the Caretaker checksum-validates and expires the checkpoint without
restoration. It expires a failure checkpoint only after restoration succeeds;
restore failure leaves it active for a trusted retry and reports both errors.
Rollback orchestration also treats owner, lifecycle, identity, target, or
checksum admission failure as a restoration failure, preserving it alongside
the original migration error. In that case the complete migrated file may
remain because the checkpoint cannot safely be applied.

## Consequences

The migration has an explicit recovery owner, byte-exact rollback, controlled
lifecycle, stable errors, and deterministic successful output. The costs are a
full in-memory copy, two writes on failure, filesystem-specific durability
limits, a deliberately single-writer model, and coupling between checkpoint
format and Originator implementation.

## Skillware Mapping

Behavioral Source defines the root Caretaker and child Originator Skill
Artifacts. Those artifacts, their reference contract, fixtures, and oracle
form one coherent constructive Skillware Unit. The exact-byte Memento is a
runtime state object described by that source, not a new Skillware ontology
category. Standard-library Python is a deterministic oracle; it does not
interpret the natural-language Skills.

### Final ontology

The source-pattern roles remain exactly **Originator**, **Memento**, and
**Caretaker**. A Behavioral Source is persisted in a Skill Artifact carried by
a Skillware Unit. An Agent Host activates that unit and an Agent Runtime
interprets activated Behavioral Source in context, but neither becomes a GoF
participant. An Execution Trace records situated performance and Task Outcome
is the evaluated effect; this static sample fabricates neither.

## Applicability

Use Memento when a state-owning object must support later exact restoration
while another component owns checkpoint timing and lifecycle without inspecting
the state. Configuration migration, transactional editing, staged upgrades,
and bounded undo histories are common fits.

## Non-Applicability

Do not use Memento when semantic reconstruction is sufficient, no restore
operation exists, or ordinary database transactions already own the complete
rollback contract. A log, backup, Git commit, or copied file alone is not
Memento unless a Caretaker has an operational restore path into the Originator.

## Positive Evidence

The repository sample is **constructive** evidence. It materializes all three
roles, the literal `migrate(path, fail=True)` restoration API, exact prior-byte
and permission capture, checksum, active lifecycle, owner capability, and
target binding, conflict-safe pre-write discard, atomic migration and restore,
post-write validation, conservative partial-write handling, mode-before-fsync
ordering, Originator-private immutable prepared payloads, opaque one-use token
consumption, forged/tampered/reused token rejection, checksum-validated commit
and discard, successful disposal without restoration, direct stale/foreign and
integrity rejection, retryable restore failure, bounded strict JSON input,
stable CLI errors, deterministic output, and no partial target content at
atomic replacement boundaries.

## Counter-Evidence

The Python oracle does not prove Agent Runtime interpretation, Agent Host
activation, crash durability on every filesystem, multi-process isolation, or
security against hostile in-process code. A restore failure can leave the
complete migrated file in place. This includes restore-admission or integrity
failure after commit; `MigrationRollbackError` preserves both failures and
reports that recovery did not occur. Permission tests cover portable mode bits, not ownership, ACLs, extended
attributes, labels, or platform-specific metadata.

## False Positives

A workflow that logs old and new values but cannot restore exact prior state is
not Memento. Neither is a backup directory whose adoption code has no owned
recovery operation. The [`misuse/SKILL.md`](misuse/SKILL.md) sample records a
change log after overwriting the target, so it cannot reconstruct the original
whitespace, key order, encoding bytes, or permissions.

## Open-Source Correspondence

Microsoft SkillOpt is a **candidate correspondence** at commit
`b860a5cf88ce75e2bd02ca981ac21fb28cffba83`. Its exact
`skillopt_sleep/staging.py` path backs up live files before copying staged
proposals into place. The inspected source exposes no owned restore path, exact
checkpoint contract, lifecycle, or restoration verification, so full Memento
is unverified. See [`correspondence.md`](correspondence.md) and the
[frozen evidence](evidence/skillopt-frozen-case.md).

## Verification

From `sample/`, run `python3 scripts/run_demo.py` and `python3 -m unittest
discover tests -v`. Tests cover the literal rollback API, successful migration,
no restore after commit, byte and permission restoration, write and validation
failure, pre-write external-change preservation, conservative post-rename
failure, mode/fsync ordering, restore failure reporting and retry, direct stale,
foreign-owner, cross-target, and integrity-corrupted mementos, opaque prepared
tokens, immutable private payloads, tuple/forged/tampered/reused token rejection,
and corrupted commit/discard rejection,
post-write checkpoint corruption, rollback admission wrapping, preservation of
both failures, and the complete migrated-file outcome when restore is forbidden,
missing/corrupt/non-UTF-8 input, duplicate fields, strict types, non-finite
numbers, lone surrogates, symlinks, version and size bounds, deterministic
fixtures, stable CLI errors, and root/child contract files. The repository root
harness copies and executes the materialized record automatically.

## Limitations

The sample assumes one cooperative writer and trusted in-process code. Private
attributes, owner tokens, and checksums are contract boundaries, not security
boundaries: reflection, monkeypatching, arbitrary memory access, or direct file
mutation can bypass them. Same-directory atomic replacement does not guarantee
identical crash semantics on every filesystem. Production use needs explicit
locking, authorization, confidential-state handling, backup retention, storage
budgets, platform metadata policy, observability, and recovery drills.
