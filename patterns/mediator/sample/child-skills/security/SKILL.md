---
name: deployment-security-check
description: Report security readiness to the Deployment Coordinator. Use only for the security participant in deployment-readiness-v1.
intent: Perform bounded security verification and return one pass or fail report through the Mediator boundary.
type: component
---

# Security Colleague / 安全参与者

## Trigger

Use this child Skill only when the Deployment Coordinator addresses the
`security` Colleague. It owns one bounded security-readiness report.

## Input contract

Act only as the `security` **Colleague** under
[`deployment-readiness-v1`](../../references/deployment-readiness-contract.md).
Receive exactly one status value, literal `pass` or `fail`, for `security`.
The Skill has no peer list and no authority to alter the release policy.

## Output contract

Perform security-specific verification. Report exactly one literal `pass` or
`fail` status to the Deployment Coordinator. Never invoke another participant,
store peer references, decide release readiness, or perform build, docs, or
approval work.

## Procedure

1. Validate the participant address and the one allowed status value.
2. Perform only the security verification represented by that status.
3. Report exactly once to the Mediator with no additional fields.

## Failure behavior

Reject malformed or non-literal status input without reporting. A specialist
exception or malformed report is isolated by the Mediator as `fail`, and later
participants remain eligible for addressing. This Skill never retries or
publishes a release decision.

## References

See [`deployment-readiness-contract.md`](../../references/deployment-readiness-contract.md)
for the Colleague operation and report boundary. The standard-library oracle
in `sample/scripts/run_demo.py` models this call without interpreting
`SKILL.md`.

## Host/runtime boundary

The Agent Host routes the security address to this Skill. The Agent Runtime
interprets its behavioral source and returns one report through the Mediator.
Host and Runtime are context, not Mediator participants.

## Verification and limits

Run the sample demo and focused tests to verify single delivery, isolation, and
the exact `pass`/`fail` contract. This deterministic fixture is not a
penetration test or security certification.

安全参与者只执行安全检查，并仅向部署协调者报告一次；不得调用其他参与者或决定发布。
