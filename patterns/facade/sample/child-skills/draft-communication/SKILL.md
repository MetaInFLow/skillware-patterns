---
name: draft-incident-communication
description: Draft a bounded incident update from service and impact context. Use when the incident Facade requests external communication.
intent: Produce one concise update without exposing internal orchestration.
type: component
---

# Draft Incident Communication

## Contract

Accept `service`, `signal`, and the returned impact assessment. For a
recognized `5xx spike`, combine the service with the assessment's
communication clause. Do not substitute a hard-coded impact claim.

## Example

If the assessment clause is `customer impact is being assessed`, return:
`Investigating elevated 5xx responses for <service>; customer impact is being
assessed.`

## Anti-pattern

Do not mention child Skill names, routing, or unverified root cause. The Facade
owns assembly of the complete response.
