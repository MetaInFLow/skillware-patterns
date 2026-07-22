---
name: release-team-notification-consumer
description: Draft a team release notice from a typed event. Use when registered as the notification consumer for a published software release.
intent: Consume one release.published.v1 event through release-observer-v1 and return a stable team-notification receipt.
type: component
---

# Release Team Notification Consumer

## Contract

Accept exactly one `release.published.v1` event defined in
`../../references/release-event-contract.md`. Validate it before drafting.

## Behavior

Draft one notice for the release channel using version and notes, then return
`team-notification:<channel>:<version>` only after success. On failure, raise an
error; do not publish another release or call the other consumers.

## Demo mode

`update_team_notification` deterministically returns the receipt without
external I/O. It models this consumer boundary and does not interpret this
Skill file.
