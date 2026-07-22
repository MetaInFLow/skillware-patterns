---
name: draft-incident-communication
description: Draft a bounded incident update from service and impact context. Use when the incident Facade requests external communication.
intent: Produce one concise update without exposing internal orchestration.
type: component
---

# Draft Incident Communication

## Contract

Accept `service`, `signal`, and the assessed impact. For a recognized `5xx
spike`, return: `Investigating elevated 5xx responses for <service>; customer
impact is being assessed.`

## Example

For `checkout-api`, replace `<service>` with that exact service identifier.

## Anti-pattern

Do not mention child Skill names, routing, or unverified root cause. The Facade
owns assembly of the complete response.
