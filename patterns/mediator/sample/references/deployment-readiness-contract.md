# Deployment Readiness Contract / 部署就绪契约

## Roles / 角色

- **Mediator:** the single `deployment-readiness-v1` report interface.
- **ConcreteMediator:** Deployment Coordinator, which owns addressing,
  failure isolation, readiness policy, and the final decision.
- **Colleague:** one of build, security, docs, or approval. Each owns only its
  specialist work and reports only to the Mediator.

Mediator、ConcreteMediator、Colleague 是唯一的 GoF 参与者。Agent Host 与
Agent Runtime 仅是执行上下文。

## Input / 输入

`coordinate(statuses)` accepts a mapping with exactly these fields and literal
values:

```json
{"build":"pass","security":"pass","docs":"pass","approval":"pass"}
```

Allowed values are exactly `pass` and `fail`. The coordinator rejects a missing,
extra, duplicate, wrong-type, malformed, non-UTF-8, symbolic-link, non-regular,
or larger-than-65,536-byte workflow before dispatch. It copies status values
and never mutates the caller mapping.

## Collaboration / 协作

The ConcreteMediator validates one unique Colleague per canonical participant,
binds each to address `deployment-coordinator`, and invokes each exactly once in
build, security, docs, approval order. Each Colleague receives only its own
status, performs its bounded specialist callable, and calls `Mediator.receive`.
No Colleague receives a peer list or peer address.

ConcreteMediator catches a specialist exception or invalid callable report,
records that participant as `fail`, and continues. It alone applies
`all-participants-pass`; it does not perform the specialist checks.

ConcreteMediator 按固定顺序逐一寻址。参与者异常或无效报告会隔离为 `fail`，后续参与者仍会
执行。只有 ConcreteMediator 决定发布或阻止，参与者之间不得直接通信。

## Output / 输出

The result contains exactly `decision`, `communication_path`, and `statuses`.
`decision` is `release` only when all four final reports are `pass`; otherwise
it is `blocked`. `communication_path` is always the literal
`participants->mediator->release`. Status fields always use canonical order.

## Trusted-code limit / 可信代码限制

Python object binding and private attributes express a cooperative contract,
not isolation from hostile in-process code. Reflection, subclass replacement,
monkeypatching, memory inspection, or out-of-band shared services can create
peer coupling. Production hosts must enforce capabilities and audit actual
messages if adversarial isolation is required.
