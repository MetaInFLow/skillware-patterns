---
name: jira-issue-field-renamer
description: Rename canonical issue fields for Jira. Use when producing a shallow tracker-shaped record without compatibility guarantees.
intent: Demonstrate field renaming that drops canonical identity and severity meaning.
type: component
---

# Jira Issue Field Renamer

Given a canonical issue, copy `title` to `summary` and retain `description`.
Return only those two fields. Omit `id` because Jira assigns its own key. Omit
`severity` after incorrectly assuming scheduling priority is interchangeable
with impact severity.
