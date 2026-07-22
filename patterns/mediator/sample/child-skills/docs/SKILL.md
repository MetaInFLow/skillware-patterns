---
name: deployment-docs-check
description: Report documentation readiness to the Deployment Coordinator. Use only for the docs participant in deployment-readiness-v1.
intent: Perform bounded documentation verification and return one pass or fail report through the Mediator boundary.
type: component
---

# Docs Colleague / 文档参与者

## Contract

Act only as the `docs` **Colleague** under
[`deployment-readiness-v1`](../../references/deployment-readiness-contract.md).

## Behavior

Perform documentation-specific verification. Report exactly one literal
`pass` or `fail` status to the Deployment Coordinator. Never invoke another participant,
store peer references, decide release readiness, or perform build, security, or
approval work.

文档参与者只执行文档检查，并仅向部署协调者报告一次；不得调用其他参与者或决定发布。
