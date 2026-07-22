---
name: configuration-originator
description: Own configuration capture, migration, validation, and restoration. Use only behind the configuration-memento-v1 contract.
intent: Encapsulate service configuration state and create or restore opaque exact-byte Mementos for one validated target.
type: component
---

# Configuration Originator

## Contract

Implement the **Originator** operations from
[`configuration-memento-v1`](../../references/configuration-memento-contract.md).

## Behavior

Validate and retain configuration state privately. On capture, create an opaque
Memento containing the precise pre-migration bytes, canonical target identity,
portable permission mode, SHA-256 integrity value, Caretaker identity, and
lifecycle state. Never expose those contents to the Caretaker.

For preparation and restore, require the Caretaker owner capability and reject
inactive, foreign, checksum-invalid, or cross-target checkpoints even on a
direct Originator call. Before mutation, verify that the target still matches
the captured bytes and render only `version + 1` with the same endpoint. A
preparation conflict must not write or restore. For the later write attempt,
apply mode to the open temporary file before its final fsync, atomically
replace, fsync the directory, and reread the exact result. Restore exact bytes
and permissions through the same durable ordering.

## Limits

The Python private surface and checksum enforce a cooperative contract, not a
security boundary against arbitrary trusted in-process code.
