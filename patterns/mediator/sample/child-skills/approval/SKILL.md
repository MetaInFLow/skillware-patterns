---
name: deployment-approval-check
description: Report approval readiness to the Deployment Coordinator. Use only for the approval participant in deployment-readiness-v1.
intent: Perform bounded approval verification and return one pass or fail report through the Mediator boundary.
type: component
---

# Approval Colleague / 审批参与者

## Contract

Act only as the `approval` **Colleague** under
[`deployment-readiness-v1`](../../references/deployment-readiness-contract.md).

## Behavior

Perform approval-specific verification. Report exactly one literal `pass` or
`fail` status to the Deployment Coordinator. Never invoke another participant,
store peer references, decide release readiness, or perform build, security, or
docs work.

审批参与者只执行审批检查，并仅向部署协调者报告一次；不得调用其他参与者或决定发布。
