---
name: multi-tracker-issue-publisher
description: Translate one canonical issue for GitHub, Jira, or Linear. Use when publishing the same issue semantics through different tracker contracts.
intent: Preserve issue identity and meaning while adapting one canonical contract to three target payloads.
type: workflow
---

# Multi-Tracker Issue Publisher

## Trigger

Use this Skill when a task caller provides one canonical issue and needs a
payload for GitHub, Jira, or Linear without maintaining tracker-specific copies
of the issue procedure.

## Input contract

Require a request object with:

- `target`: exactly `github`, `jira`, or `linear`;
- `issue.id`: a non-empty stable canonical identity;
- `issue.title`: a non-empty title;
- `issue.description`: a non-empty description;
- `issue.severity`: exactly `low`, `medium`, `high`, or `critical`.

Reject an unknown target, missing field, empty field, wrong field type, or
unsupported severity. The request must contain exactly `target` and `issue`,
and `issue` must contain exactly the four canonical fields; reject additional
fields clearly instead of silently discarding them. Never mutate the request
or nested issue object.

## Canonical semantics

Treat `id`, `title`, `description`, and `severity` as the Adaptee contract.
Every Adapter must preserve `id` as `external_id`, retain title and description
meaning, and translate severity according to the target mapping in
`references/tracker-contracts.md`. Reject a binding rather than discarding a
required semantic value.

## Target bindings

1. For GitHub, map `title` directly, map `description` to `body`, and encode
   severity as one `severity:<canonical-value>` label.
2. For Jira, map `title` to `summary`, retain `description`, and map severity to
   the documented named `priority`.
3. For Linear, retain `title` and `description`, and map severity to the
   documented numeric `priority`.

Each binding is an Adapter. The selected tracker payload contract is its
Target. The task caller is the Client.

## Output contract

Return exactly `target` and `payload`. The payload must contain `external_id`
and only the selected Target's documented fields. Do not expose internal route
names or add tracker-independent policy.

## Example

Input: `{"target":"github","issue":{"id":"ISSUE-104","title":"Checkout retries exhaust","description":"Payment requests fail after retry budget is exhausted.","severity":"critical"}}`

The GitHub Adapter emits `external_id`, the canonical title, the description as
`body`, and the label `severity:critical`. The exact executable result is in
`expected/github-result.json`.

## Anti-pattern

Do not copy this Skill per tracker and merely rename fields while dropping
canonical `id` or severity meaning. That creates divergent behavior and fails
the Adapter requirement of semantic translation. See `../misuse/SKILL.md`.
