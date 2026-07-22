---
name: assess-incident-impact
description: Assess customer impact from a recognized incident. Use when the incident Facade supplies a service and confirmed 5xx spike.
intent: Produce one bounded impact statement for the incident response contract.
type: component
---

# Assess Incident Impact

## Contract

Accept the service, confirmed `5xx spike` signal, and diagnosis result. Return
an internal assessment with a public statement and communication clause. The
public statement is: `Customer requests may fail; treat <service scope>
availability as degraded.` The communication clause states that customer
impact is being assessed.

## Example

For `checkout-api`, the service scope is `checkout`. The statement
distinguishes likely customer failure from a claim that every request has
failed.

## Anti-pattern

Do not diagnose the underlying cause or choose operational actions. This Skill
only assesses impact from the supplied incident context.
