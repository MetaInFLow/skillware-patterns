---
name: incident-response-facade
description: Coordinate incident diagnosis, impact assessment, and communication. Use when a production service reports a signal requiring one response.
intent: Provide one stable incident-response contract over three specialist Skills.
type: workflow
---

# Production Incident Response

## Trigger

Use this Skill when an operator supplies a production `service` and observed
`signal` and needs one coordinated incident response.

## Input contract

Require a non-empty string `service` and a non-empty string `signal`. Reject the
request clearly if either field is absent, empty, or not a string.

## Public operation

Return exactly these fields in this order:

1. `summary`
2. `impact`
3. `actions`
4. `communication`

Do not expose child Skill names, internal route names, or intermediate records.
The detailed field contract is in `references/response-contract.md`.

## Orchestration

For `5xx spike`:

1. Use `child-skills/diagnose/SKILL.md` to summarize the observed failure and
   propose immediate diagnostic actions.
2. Pass the service, signal, and diagnosis to
   `child-skills/assess-impact/SKILL.md` to classify likely customer impact.
3. Pass the service, signal, and returned impact assessment to
   `child-skills/draft-communication/SKILL.md`; derive the status update from
   that assessment.
4. Assemble the public result without exposing orchestration details.

## Fallback

For any unknown signal, do not guess a diagnosis. Preserve the public result
contract and set `actions` to exactly `["request-human-triage"]`.

## Example

Input: `{"service": "checkout-api", "signal": "5xx spike"}`

The response summarizes elevated 5xx failures, identifies degraded checkout
availability, gives immediate actions, and provides one investigation update.
The executable expected result is in `expected/incident-result.json`.

## Ontology boundary

Behavioral Source -> Skill Artifact -> Skillware Unit -> Agent Host -> Agent Runtime -> Execution Trace -> Task Outcome

The Facade roles belong to the pattern mapping. Agent Host and Agent Runtime
remain execution context and are not reclassified as Facade participants.

## Anti-pattern

Do not merely list the three child Skills and ask the caller to choose. Without
one public operation, orchestration rules, and a fallback, the artifact is a
catalog rather than a Facade. See `../misuse/SKILL.md`.
