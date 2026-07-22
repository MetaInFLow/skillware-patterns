---
name: deployment-security-check
description: Report security readiness to the Deployment Coordinator. Use only for the security participant in deployment-readiness-v1.
intent: Perform bounded security verification and return one pass or fail report through the Mediator boundary.
type: component
---

# Security Colleague / 安全参与者

## Contract

Act only as the `security` **Colleague** under
[`deployment-readiness-v1`](../../references/deployment-readiness-contract.md).

## Behavior

Perform security-specific verification. Report exactly one literal `pass` or
`fail` status to the Deployment Coordinator. Never invoke another participant,
store peer references, decide release readiness, or perform build, docs, or
approval work.

安全参与者只执行安全检查，并仅向部署协调者报告一次；不得调用其他参与者或决定发布。
