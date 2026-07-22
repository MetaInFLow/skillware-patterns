---
name: multi-tracker-issue-publisher
description: Build an offline GitHub, Jira, or Linear issue request. Use when adapting one canonical issue to documented tracker request contracts.
intent: Preserve issue identity and severity while producing a versioned vendor request descriptor without network access.
type: workflow
---

# Multi-Tracker Issue Publisher

## Trigger

Use this Skill when a task caller provides one canonical issue and target
location details, and needs a documented offline request descriptor for
GitHub, Jira, or Linear.

## Input contract

The request has exactly `target`, `issue`, and `target_context`.

The canonical `issue` has exactly four non-empty string fields: `id`, `title`,
`description`, and `severity`. Severity is exactly `low`, `medium`, `high`, or
`critical`.

The exact `target_context` depends on `target`:

- `github`: `owner` and `repo`;
- `jira`: `project_key` and `issue_type`, where `issue_type` is the Jira issue
  type ID;
- `linear`: `team_id`.

Reject unknown targets, missing or additional fields, non-object records,
wrong types, blank values, invalid JSON, and unsupported severity. Never mutate
the request, nested issue, or target context.

## Canonical semantics

Treat the four issue fields as the Adaptee contract. Preserve source identity
and severity in documented body, description, or label fields instead of
inventing vendor fields. Severity describes impact; tracker priority represents
scheduling policy. Do not convert one into the other.

## Target bindings

1. **GitHub REST API 2022-11-28:** build `POST
   /repos/{owner}/{repo}/issues` with the version and media headers, canonical
   title, a Markdown body containing deterministic source/severity markers, and
   a deterministic severity label.
2. **Jira Cloud REST API v3:** build `POST /rest/api/3/issue` with project key,
   issue type ID, summary, an Atlassian Document Format description containing
   the description/source/severity, and deterministic source/severity labels.
3. **Linear GraphQL:** build the documented `issueCreate` mutation with
   `variables.input.teamId`, `title`, and Markdown `description`. Keep source
   identity and severity in the description because label IDs are not supplied.

The exact contracts and official documentation links are in
`references/tracker-contracts.md`.

## Output contract

Return exactly `target` and `request`. `request` is a deterministic offline
descriptor with the selected REST or GraphQL operation. It contains no
credentials, performs no network call, and does not claim that a live vendor
service accepted it.

## Example

The valid GitHub fixture supplies `owner: acme` and `repo: payments`. Its
descriptor uses `POST /repos/acme/payments/issues`, GitHub API version
`2022-11-28`, the canonical title, and body markers for `ISSUE-104` and
`critical`. The exact result is in `expected/github-result.json`.

## Ontology boundary

Behavioral Source -> Skill Artifact -> Skillware Unit -> Agent Host -> Agent Runtime -> Execution Trace -> Task Outcome

The Adapter roles belong to the pattern mapping. Agent Host and Agent Runtime
remain execution context and are not reclassified as Adapter participants.

## Anti-pattern

Do not copy this Skill per tracker, rename a few fields, or treat impact
severity as scheduling priority. Dropping identity or severity meaning fails
the Adapter requirement of semantic translation. See `../misuse/SKILL.md`.
