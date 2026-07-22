# configuration-memento-v1

## Scope

This contract governs one bounded JSON configuration migration under the three
canonical GoF roles: Originator, Memento, and Caretaker.

## Configuration

The input is a regular non-symlink UTF-8 file no larger than 65,536 bytes. Its
JSON root has exactly `version` and `endpoint`, with no duplicate members.
`version` is a non-boolean integer from 0 through 2,147,483,646. `endpoint` is a
nonblank string of at most 4,096 Unicode scalar values. Non-finite values and
lone surrogates are invalid. Invalid input is never rewritten.

## Originator

The Originator owns validation and its private configuration state. It alone:

- creates a Memento from exact bytes plus target, mode, checksum, owner, and
  lifecycle metadata;
- requires the Caretaker owner capability and an active Memento for preparation
  and restore, including direct Originator calls;
- verifies the target still matches the capture during no-write preparation;
- renders deterministic UTF-8 JSON with sorted keys, two-space indentation,
  and one final newline;
- atomically replaces and rereads the migrated target; and
- interprets a target-bound, integrity-valid Memento for exact restore.

## Memento

The Memento is opaque to Caretaker code. It has no public content, payload,
state, byte, or checksum accessor. Its representation reveals no configuration.
The target binding and SHA-256 value detect accidental cross-target use or
corruption inside the trusted process; they do not provide confidentiality or
hostile-code security.

## Caretaker

One Caretaker owns at most one live Memento. It captures before mutation,
retains the checkpoint opaquely, and discards it without restoration when
preparation or conflict validation fails before any write attempt. After a
write attempt it requests Originator restore on failure and expires only after
verified restore. A successful migration expires it without a restore call.
Foreign, stale, checksum-corrupted, and second-live Mementos are controlled
errors at both Caretaker and Originator access paths.

## Atomicity and failure

Migration and restoration each write a same-directory temporary file, apply the
captured portable mode on its open descriptor, `fsync` that file, atomically
replace the target, then `fsync` the directory. Where descriptor-mode changes
are unavailable, the portable fallback changes mode by temporary path while the
file remains open and before its `fsync` and rename. Temporary files are removed
after failure. A post-write reread must match the validated configuration and
exact deterministic bytes.

Any error once the atomic write is attempted is treated conservatively as a
possible target mutation, including an error after rename during directory
`fsync`. If migration fails and restore succeeds, re-raise the original
migration error. If restore fails, raise `MigrationRollbackError` carrying both
`migration_error` and `restore_error`; the file remains one complete atomic
version but recovery is not claimed. Direct Caretaker restore failure raises
`RestorationError` and keeps the checkpoint live for a trusted retry.

## Trust and concurrency

The contract assumes one cooperative writer and trusted in-process extension
code. It is not a lock, transaction manager, sandbox, capability system, or
secret store. Reflection, monkeypatching, direct filesystem access, races, and
arbitrary memory access require controls outside this sample. Portable mode
preservation excludes ownership, ACLs, extended attributes, and security
labels.
