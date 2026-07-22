---
name: diagnose-incident-signal
description: Summarize a recognized production signal and immediate checks. Use when the incident Facade requests diagnosis for a service signal.
intent: Produce bounded diagnostic facts and actions without owning impact or communication.
type: component
---

# Diagnose Incident Signal

## Contract

Accept `service` and the recognized signal `5xx spike`. Return a factual
summary plus these immediate actions in order:

1. `page-on-call`
2. `inspect-recent-deployments`
3. `check-upstream-dependencies`

## Example

For `checkout-api` and `5xx spike`, report that the service is experiencing
elevated 5xx responses.

## Anti-pattern

Do not infer customer impact or publish a status message; those responsibilities
belong to other specialist Skills coordinated by the root Skill.
