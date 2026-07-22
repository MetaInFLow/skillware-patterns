---
name: assess-incident-impact
description: Assess customer impact from a recognized incident. Use when the incident Facade supplies a service and confirmed 5xx spike.
intent: Produce one bounded impact statement for the incident response contract.
type: component
---

# Assess Incident Impact

## Contract

Accept the service and confirmed `5xx spike` context. Return: `Customer
requests may fail; treat checkout availability as degraded.`

## Example

The statement distinguishes likely customer failure from a claim that every
request has failed.

## Anti-pattern

Do not diagnose the underlying cause or choose operational actions. This Skill
only assesses impact from the supplied incident context.
