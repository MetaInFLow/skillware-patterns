# Tracker request contracts

This reference records the official contracts used by the deterministic demo.
The sources were reviewed on 2026-07-22. The demo builds offline descriptors;
it does not authenticate, send requests, inspect tenant metadata, or establish
that any live service would accept a fixture.

## Canonical request

The outer request has exactly `target`, `issue`, and `target_context`.
`issue` has exactly the non-empty strings `id`, `title`, `description`, and
`severity`; severity is `low`, `medium`, `high`, or `critical`.

Target context is exact and target-specific:

| Target | Required context | Meaning |
| --- | --- | --- |
| GitHub | `owner`, `repo` | Repository owner and repository name used in the REST path. |
| Jira | `project_key`, `issue_type` | Jira project key and issue type ID used in `fields`. |
| Linear | `team_id` | Linear team ID used as `variables.input.teamId`. |

## GitHub REST Target

Official source: [GitHub REST create-an-issue endpoint, API version 2022-11-28](https://docs.github.com/en/rest/issues/issues?apiVersion=2022-11-28#create-an-issue).

The descriptor uses `POST /repos/{owner}/{repo}/issues`, `Accept:
application/vnd.github+json`, and `X-GitHub-Api-Version: 2022-11-28`. The
documented request body supports `title`, `body`, and `labels`.

| Canonical meaning | Documented representation |
| --- | --- |
| title | `request.body.title` |
| description | leading Markdown in `request.body.body` |
| source identity | deterministic HTML comment in `request.body.body` |
| severity | deterministic HTML comment plus `skillware-severity-{value}` label |

The descriptor intentionally omits authorization. A caller would need to add
credentials and ensure labels and repository issue settings are valid before a
live request.

## Jira Cloud REST v3 Target

Official sources: [Jira Cloud REST v3 Create issue](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-post) and [Atlassian Document Format structure](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/).

The descriptor uses `POST /rest/api/3/issue` with JSON headers. Its body has a
`fields` object containing `project.key`, `summary`, `issuetype.id`, an ADF
`description`, and `labels`.

| Canonical meaning | Documented representation |
| --- | --- |
| title | `request.body.fields.summary` |
| description | first ADF paragraph |
| source identity | ADF paragraph plus deterministic source label |
| severity | ADF paragraph plus deterministic severity label |

Jira permits only fields available in the selected project's create metadata.
The offline descriptor cannot verify field screens, permissions, label policy,
tenant base URL, or whether the supplied issue type ID belongs to the project.

## Linear GraphQL Target

Official source: [Linear GraphQL creating and editing issues](https://linear.app/developers/graphql#creating-and-editing-issues).

The descriptor targets `https://api.linear.app/graphql` and carries a
parameterized `issueCreate` mutation. `variables.input` contains `teamId`,
`title`, and Markdown `description`, matching the documented create example.

| Canonical meaning | Documented representation |
| --- | --- |
| target team | `request.body.variables.input.teamId` |
| title | `request.body.variables.input.title` |
| description | leading Markdown in `request.body.variables.input.description` |
| source identity | deterministic Markdown metadata line in `description` |
| severity | deterministic Markdown metadata line in `description` |

The Adapter does not emit `labelIds`, because no resolved Linear label IDs are
part of the canonical request or target context.

## Severity is not priority

Canonical severity describes impact. Tracker priority is a scheduling decision
that can depend on team policy, business context, and target configuration.
The Adapter preserves the severity value as metadata and never injects a
priority. Converting severity into priority would add domain policy rather than
translate an interface.

## Compatibility boundary

Field renaming is not enough. An Adapter must retain the meaning of every
required canonical field through documented target fields and must reject
unsupported schema. These descriptors establish structural correspondence to
the cited contracts only. Authentication, tenant configuration, live API
acceptance, side effects, and runtime parity remain unverified.
