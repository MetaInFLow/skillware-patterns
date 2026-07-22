---
name: healthcare-rfp-domain
description: Add healthcare focus and evidence to the bounded RFP domain hook. Use only inside the fixed Enterprise RFP Response template.
intent: Implement rfp-domain-hook-v1 for healthcare without changing, skipping, or reordering mandatory RFP stages.
type: component
---

# Healthcare RFP Domain

## Contract

This Skill Artifact is a **ConcreteClass** supplier of the sole static
`apply-domain-hook` callable in
[`rfp-domain-hook-v1`](../../references/rfp-domain-hook-contract.md). Accept and
return exactly that hook contract.

## Procedure

Validate the isolated hook request and confirm `domain` is `healthcare`.
Return the focus areas `patient-data-protection` and
`clinical-workflow-continuity`, plus the required evidence
`security-control-mapping` and `clinical-adoption-plan`.

Accept only the copied hook request; no instance or mutable root workflow state
is available. Do not extract requirements, analyze gaps, draft the response, perform the
quality check, call another stage, or change stage order. The AbstractClass
owns those operations and invokes this bounded operation exactly once.

## Demo mode

The static `HealthcareRfpResponse.apply_domain_hook` deterministically models this
ConcreteClass without external I/O and does not interpret this Skill file.
