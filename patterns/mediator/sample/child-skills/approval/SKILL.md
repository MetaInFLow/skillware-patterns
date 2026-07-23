---
name: deployment-approval-check
description: Report approval readiness to the Deployment Coordinator. Use only for the approval participant in deployment-readiness-v1.
intent: Perform bounded approval verification and return one pass or fail report through the Mediator boundary.
type: component
---

# Approval Colleague / 审批参与者

## Trigger

Use this child Skill only when the Deployment Coordinator addresses the
`approval` Colleague. It performs one approval-readiness check and reports to
the central Mediator.

## Input contract

Act only as the `approval` **Colleague** under
[`deployment-readiness-v1`](../../references/deployment-readiness-contract.md).
Receive exactly one literal `pass` or `fail` status for `approval`. No peer
reference, combined status map, or release policy is accepted.

## Output contract

Perform approval-specific verification. Report exactly one literal `pass` or
`fail` status to the Deployment Coordinator. Never invoke another participant,
store peer references, decide release readiness, or perform build, security, or
docs work.

## Procedure

1. Validate the participant address and the one allowed status value.
2. Apply only the approval verification represented by that value.
3. Report once through the Mediator boundary; leave the all-pass decision to
   the Coordinator.

## Failure behavior

Reject malformed input before reporting. If the specialist callable fails or
returns anything other than literal `pass`/`fail`, the Mediator records this
participant as `fail` and continues its fixed addressing order. Never retry or
make a release decision locally.

## References

Consult [`deployment-readiness-contract.md`](../../references/deployment-readiness-contract.md)
for the shared roles and report semantics. `sample/scripts/run_demo.py` is a
deterministic oracle for this boundary and does not interpret `SKILL.md`.

## Host/runtime boundary

The Agent Host routes the `approval` address to this Skill. The Agent Runtime
interprets the behavioral source and sends one report to the Mediator. Host and
Runtime are execution context, not Mediator participants.

## Verification and limits

Run `python3 scripts/run_demo.py` and focused tests from `sample/` to verify
single reporting and failure isolation. This sample models an approval signal;
it is not an authorization system or evidence of real approval.

审批参与者只执行审批检查，并仅向部署协调者报告一次；不得调用其他参与者或决定发布。
