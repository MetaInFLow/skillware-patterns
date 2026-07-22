---
name: deployment-coordinator
description: Coordinate four isolated deployment checks and decide release readiness. Use when specialists must report centrally without peer calls.
intent: Address build, security, docs, and approval Colleagues once, isolate failures, and apply one deterministic all-pass release policy.
type: workflow
---

# Deployment Coordinator / 部署协调

## Trigger

Use this root Skill when build, security, documentation, and approval readiness
must be combined under
[`deployment-readiness-v1`](references/deployment-readiness-contract.md) without
direct communication among specialist Skills.

## 中文触发约定

当构建、安全、文档和审批专长必须彼此隔离，并由一个中心协调者汇总后决定是否发布时，
使用本根 Skill。

## Participants

This root Skill is the **ConcreteMediator** and implements the **Mediator**
report boundary. The four child Skills are **Colleague** participants. Agent
Host and Agent Runtime are execution context, not GoF Mediator participants.

## Agent mode

1. Require exactly `build`, `security`, `docs`, and `approval`, each with the
   literal status `pass` or `fail`. Reject missing, extra, duplicate, wrong-type,
   non-UTF-8, malformed, or oversized input before addressing a Colleague.
2. Inject exactly one Colleague for each participant. Reject duplicates,
   missing participants, extras, non-Colleague objects, or a Colleague already
   bound to another Mediator.
3. Address Colleagues exactly once in build, security, docs, approval order.
   Give each only its own status. A Colleague reports only through the Mediator
   boundary and never receives peer references.
4. Isolate a callable specialist exception or invalid report as `fail`, then
   continue addressing later Colleagues. Never expose exception text in the
   release result.
5. Apply readiness policy centrally: release only when all four received
   statuses are `pass`; otherwise block. Do not redo build, security, docs, or
   approval work inside the coordinator.
6. Return a fresh deterministic status copy in canonical order with
   `communication_path: participants->mediator->release`. Do not mutate input.

## Demo mode and root harness

The standard-library Python oracle models Mediator/ConcreteMediator/Colleague
collaboration; it does not interpret these Skill files. From `sample/`, run:

```bash
python3 scripts/run_demo.py
python3 -m unittest discover tests -v
```

The repository root harness copies this record to an isolated directory, runs
the focused tests, and runs the default demo.

## Limits

Colleague binding and lack of peer references are trusted in-process code
contracts, not a security sandbox. Reflection, subclass overrides,
monkeypatching, shared external services, or direct memory access can bypass
them. The deterministic oracle validates structured statuses; it does not
interpret natural-language specialist work or prove Agent Runtime behavior.

## Anti-pattern

A full peer mesh in which every specialist invokes every other specialist is
not Mediator. A central God Skill that performs every specialist check itself
is also not sound Mediator separation. See `../misuse/SKILL.md`.
