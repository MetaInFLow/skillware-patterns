---
name: finance-rfp-domain
description: Add finance focus and evidence to the bounded RFP domain hook. Use only inside the fixed Enterprise RFP Response template.
intent: Implement rfp-domain-hook-v1 for finance without changing, skipping, or reordering mandatory RFP stages.
type: component
---

# Finance RFP Domain

## Contract

This Skill Artifact is a **ConcreteClass** supplier of the sole static
`apply-domain-hook` callable in
[`rfp-domain-hook-v1`](../../references/rfp-domain-hook-contract.md). Accept and
return exactly that hook contract.

## Procedure

Validate the isolated hook request and confirm `domain` is `finance`. Return
the focus areas `transaction-integrity` and `regulatory-auditability`, plus the
required evidence `control-testing-report` and `audit-trail-sample`.

Accept only the copied hook request; no instance or mutable root workflow state
is available. Do not extract requirements, analyze gaps, draft the response, perform the
quality check, call another stage, or change stage order. The AbstractClass
owns those operations and invokes this bounded operation exactly once.

## Demo mode

The static `FinanceRfpResponse.apply_domain_hook` deterministically models this
ConcreteClass without external I/O and does not interpret this Skill file.
