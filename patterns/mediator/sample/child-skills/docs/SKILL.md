---
name: deployment-docs-check
description: Report documentation readiness to the Deployment Coordinator. Use only for the docs participant in deployment-readiness-v1.
intent: Perform bounded documentation verification and return one pass or fail report through the Mediator boundary.
type: component
---

# Docs Colleague / 文档参与者

## Trigger

Use this child Skill only when the Deployment Coordinator addresses the `docs`
Colleague. It performs documentation-readiness verification and returns one
report.

## Input contract

Act only as the `docs` **Colleague** under
[`deployment-readiness-v1`](../../references/deployment-readiness-contract.md).
Receive exactly one status value, literal `pass` or `fail`, for `docs`; do not
accept peer state or a release decision.

## Output contract

Perform documentation-specific verification. Report exactly one literal
`pass` or `fail` status to the Deployment Coordinator. Never invoke another participant,
store peer references, decide release readiness, or perform build, security, or
approval work.

## Procedure

1. Validate the `docs` address and the literal status.
2. Perform only documentation-specific verification represented by the status.
3. Send one report through the Mediator boundary and return control.

## Failure behavior

Reject missing, extra, or invalid status input. A raised specialist error or
invalid status is converted by the Mediator to `fail`; the child does not
contact peers, retry, or infer release readiness.

## References

The shared Colleague and report contract is in
[`deployment-readiness-contract.md`](../../references/deployment-readiness-contract.md).
The deterministic sample oracle is `sample/scripts/run_demo.py`; it models the
boundary and does not load this Skill file.

## Host/runtime boundary

The Agent Host selects this `docs` participant. The Agent Runtime interprets
the behavioral source and reports only through the Mediator. The surrounding
Coordinator owns aggregation; Host and Runtime are not GoF roles.

## Verification and limits

Run the sample demo and focused tests to verify exactly one ordered report and
failure isolation. The fixture checks a status contract; it does not perform a
full documentation audit.

文档参与者只执行文档检查，并仅向部署协调者报告一次；不得调用其他参与者或决定发布。
