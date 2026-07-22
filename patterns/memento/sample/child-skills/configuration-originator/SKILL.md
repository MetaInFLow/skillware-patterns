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

For migration, verify that the target still matches the captured bytes, render
only `version + 1` with the same endpoint, atomically replace, and reread the
exact result. For restore, accept only a checksum-valid checkpoint for this
target, atomically replace exact bytes and permissions, and verify them.

## Limits

The Python private surface and checksum enforce a cooperative contract, not a
security boundary against arbitrary trusted in-process code.
