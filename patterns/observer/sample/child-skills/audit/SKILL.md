---
name: release-audit-consumer
description: Record a typed release audit entry. Use when registered as the audit consumer for a published software release.
intent: Consume one release.published.v1 event through release-observer-v1 and return a stable audit receipt.
type: component
---

# Release Audit Consumer

## Contract

Accept exactly one `release.published.v1` event defined in
`../../references/release-event-contract.md`. Validate it before recording.

## Behavior

Append one audit entry keyed by `release_id`, preserving version, commit,
channel, published timestamp, and notes. Return `audit:<release_id>` only after
the entry succeeds. On failure, raise an error; do not publish another release
or call the other consumers.

## Demo mode

`update_audit` deterministically returns the receipt without external I/O. It
models this consumer boundary and does not interpret this Skill file.
