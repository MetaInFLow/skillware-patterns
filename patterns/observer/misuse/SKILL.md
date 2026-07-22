---
name: polling-release-broadcaster
description: Poll and broadcast release files. Use only to demonstrate notification without Subject-managed subscriptions.
intent: Show an Observer near miss that scans release state and broadcasts to discovered consumers without registration or unregistration.
type: workflow
---

# Polling Release Broadcaster

Every five minutes, scan the release directory. When a version file changes,
discover all notification endpoints and broadcast the file contents to each of
them in arbitrary discovery order.

There is no event schema, Observer update contract, registration operation, or
unregistration operation. Failed endpoints stop the broadcast and no
per-consumer result is retained.
