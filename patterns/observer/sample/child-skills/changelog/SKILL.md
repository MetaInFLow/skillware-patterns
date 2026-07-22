---
name: release-changelog-consumer
description: Update a changelog from a typed release event. Use when registered as the changelog consumer for a published software release.
intent: Consume one release.published.v1 event through release-observer-v1 and return a stable changelog receipt.
type: component
---

# Release Changelog Consumer

## Contract

Accept exactly one `release.published.v1` event defined in
`../../references/release-event-contract.md`. Validate it before updating.

## Behavior

Create the changelog section for `version` from the event's declared notes and
return `changelog:<version>` only after the update succeeds. On failure, raise
an error; do not publish another release or call the other consumers.

## Demo mode

`update_changelog` deterministically returns the receipt without external I/O.
It models this consumer boundary and does not interpret this Skill file.
