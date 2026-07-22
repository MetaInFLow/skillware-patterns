---
name: unrelated-review-branches
description: Route to unrelated code tools with incompatible outputs. Use only to demonstrate alternatives that are not interchangeable Strategies.
intent: Show a Strategy near miss whose branches perform different tasks and expose different request and result interfaces.
type: workflow
---

# Unrelated Review Branches

Read a `mode` field and branch as follows:

- For `dependency-links`, accept `{query}` and return `{links}` from a dependency
  link finder.
- For `deployment-approval`, accept `{proposal}` and return
  `{recommendation, approved}` from a release approver.

The branches perform unrelated discovery and approval tasks. They share no
review request, no finding schema, and no summary. Let each branch validate and
format its own incompatible object. There is no common operation against which
the alternatives can be substituted or tested.
