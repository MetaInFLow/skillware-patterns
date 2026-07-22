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

Capture exactly one Memento before mutation. Retain it opaquely. On successful
post-write validation, expire and discard it without restoration. On failure,
ask the Originator to restore it, then expire it only after verified recovery.
Reject second-live, stale, foreign-owner, and cross-target checkpoints.

If restoration fails, preserve the checkpoint for a trusted retry and report
both the triggering migration failure and restoration failure. Never report a
rollback unless the Originator verified exact bytes and permissions.
