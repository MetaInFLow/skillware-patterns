---
name: deployment-build-check
description: Report build readiness to the Deployment Coordinator. Use only for the build participant in deployment-readiness-v1.
intent: Perform bounded build verification and return one pass or fail report through the Mediator boundary.
type: component
---

# Build Colleague / 构建参与者

## Trigger

Use this child Skill only when the Deployment Coordinator addresses the
`build` Colleague. It performs one bounded build-readiness check and reports
through the Mediator boundary.

## Input contract

Act only as the `build` **Colleague** under
[`deployment-readiness-v1`](../../references/deployment-readiness-contract.md).
Receive exactly one status value, either `pass` or `fail`, for this participant;
do not accept a peer map, release policy, or another participant's input.

## Output contract

Perform build-specific verification. Report exactly one literal `pass` or
`fail` status to the Deployment Coordinator. Never invoke another participant,
store peer references, decide release readiness, or perform security, docs, or
approval work.

## Procedure

1. Validate the addressed participant is `build` and the status is literal
   `pass` or `fail`.
2. Apply the bounded build check represented by the supplied status.
3. Call the Mediator's report boundary exactly once with that status.

## Failure behavior

Reject a missing, extra, or invalid status before reporting. If the specialist
check raises or cannot produce a literal status, the Mediator records this
participant as `fail`; this Skill does not retry or decide the final release.

## References

The report, binding, and failure-isolation rules are defined in
[`deployment-readiness-contract.md`](../../references/deployment-readiness-contract.md).
The deterministic oracle is `sample/scripts/run_demo.py`; it models this
Colleague boundary and does not interpret the Skill file.

## Host/runtime boundary

The Agent Host addresses this Skill as the `build` participant. The Agent
Runtime interprets its behavioral source and sends the report to the Mediator.
Mediator, ConcreteMediator, and Colleague are the pattern roles; Host and
Runtime remain execution context.

## Verification and limits

Run `python3 scripts/run_demo.py` and the focused tests from `sample/` to
verify one report, canonical ordering, and failure isolation. The demo status
does not compile a repository or provide a production build guarantee.

构建参与者只执行构建检查，并仅向部署协调者报告一次；不得调用其他参与者或决定发布。
