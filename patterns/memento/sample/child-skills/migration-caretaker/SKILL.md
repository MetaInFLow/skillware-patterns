---
name: migration-caretaker
description: Manage one opaque configuration checkpoint. Use when migration success discards it and failure must request exact restoration.
intent: Own capture, restore, commit, and lifecycle policy without inspecting or modifying Originator state.
type: component
---

# Migration Caretaker

## Contract

Implement the **Caretaker** lifecycle from
[`configuration-memento-v1`](../../references/configuration-memento-contract.md).

## Behavior

Capture exactly one Memento before mutation and retain it opaquely. Retain only
the opaque one-use preparation token returned by the Originator; never receive
or inspect its private immutable payload. If capability-checked preparation or
conflict validation fails before a write attempt, checksum-validate and expire
the Memento and outstanding token without restoration so newer content
survives. On successful post-write validation, also checksum-validate, expire,
and discard without restoration.
After any write attempt or post-write failure, ask the Originator to restore
conservatively, then expire only after verified recovery. Reject second-live,
stale, foreign-owner, checksum-invalid, and cross-target checkpoints.

For rollback orchestration, include owner, lifecycle, identity, target, and
checksum admission inside the restoration-error boundary. If admission or
restoration fails, preserve both the triggering migration error and the
restore error. The complete migrated file may remain because recovery was
impossible. Preserve the checkpoint for a trusted retry when integrity permits;
never report rollback unless the Originator verified exact bytes and permissions.
