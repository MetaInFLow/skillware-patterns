---
name: enterprise-rfp-response
description: Run a fixed enterprise RFP response sequence with one bounded domain hook. Use when sector expertise may vary but mandatory response stages must not.
intent: Preserve extraction, gap analysis, drafting, and quality-check order while allowing one validated healthcare or finance domain operation.
type: workflow
---

# Enterprise RFP Response / 企业 RFP 响应

## Trigger

Use this root Skill when an enterprise RFP response must always extract
requirements, analyze gaps, draft, and pass quality review in one fixed order,
while a bounded sector profile adds domain focus and evidence requirements.
Input and domain output follow
[`rfp-domain-hook-v1`](references/rfp-domain-hook-contract.md).

## Participants

This root workflow is the **AbstractClass**: it owns the complete Template
Method and all mandatory operations. Healthcare and Finance child Skill
Artifacts are **ConcreteClass** implementations of the sole overridable
`apply-domain-hook` operation. That operation is not an additional GoF
participant.

Agent Host and Agent Runtime are execution context, not Template Method
participants.

## Agent mode

1. Validate the complete `enterprise-rfp-v1` request before beginning. Reject
   malformed JSON, duplicate members at any depth, invalid UTF-8, lone Unicode
   surrogates, non-string mapping keys, cycles, excessive depth, unknown fields,
   unsupported domains, duplicate requirement ids, wrong types, and exceeded
   bounds through controlled errors.
2. Execute exactly these operations in this order:
   `extract-requirements`, `analyze-gaps`, `apply-domain-hook`,
   `draft-response`, `quality-check`.
3. Select one ConcreteClass from the validated domain. Give its hook an
   copied `rfp-domain-hook-v1` request. Invoke its single-argument static
   hook callable exactly once, and validate and copy its result before drafting.
4. Permit the ConcreteClass to supply only domain `focus_areas` and
   `required_evidence`. It must not skip, insert, repeat, or reorder any
   mandatory stage, and must not own the final response or quality decision.
5. If the hook fails, propagate that failure unchanged and stop before drafting
   or quality checking. Never fabricate a partial success result.
6. Validate the final result, including the exact stage sequence, domain and
   RFP identity, requirement order, hook result, draft coverage, and quality
   fields. Return validated copies in deterministic field and stage order.

The executable public boundary dispatches the AbstractClass template
implementation explicitly. It creates no ConcreteClass instance, stores no
request or trace on `self`, and never resolves mandatory operations through a
ConcreteClass or mixin. Request identity, domain, requirements, and trace remain
local snapshots; inherited `run` or mandatory-stage names are irrelevant to
`run_template` and `run_rfp`. For cooperative hooks that use only the declared
argument/result contract, the copied request and local snapshots prevent
ordinary argument mutation or returned stage claims from rewriting captured
values or order. This is a contract boundary, not a security boundary.

## 中文执行约定

本根 Skill 是 AbstractClass，拥有完整且不可重排的模板方法：
先提取需求，再分析缺口，仅调用一次领域钩子，然后起草并质检。
医疗与金融子 Skill 是 ConcreteClass，只能实现
`apply-domain-hook` 静态可调用项，不得更改必经阶段。公开执行边界
显式调用 AbstractClass 实现，不创建领域实例，请求身份、领域与轨迹都保留为
局部快照。对于只使用声明参数与结果契约的协作式钩子，参数副本可防止
通过该参数进行的普通修改改写已捕获数据。钩子失败时原样传播异常，
且不得继续起草或质检。

## Demo mode and root harness

The standard-library Python oracle models the AbstractClass/ConcreteClass
collaboration; it does not interpret these Skill files. From `sample/`, run:

```bash
python3 scripts/run_demo.py
python3 -m unittest discover tests -v
```

The repository root harness automatically copies this record to an isolated
directory, runs the focused tests, and runs the default demo without network
access or imports from another pattern.

## Ontology boundary

Behavioral Source -> Skill Artifact -> Skillware Unit -> Agent Host -> Agent Runtime -> Execution Trace -> Task Outcome

The Template Method roles belong to the pattern mapping. Agent Host and Agent
Runtime remain execution context and are not reclassified as Template Method
participants.

## Limits

The domain content is illustrative and is not a legal, compliance, clinical,
security, procurement, or financial assurance. Selecting a runtime-swappable
whole RFP algorithm would be Strategy. Letting a domain profile reorder the
checklist removes the Template Method invariant. This in-process oracle does
not sandbox hooks. They are cooperative, trusted extension code. Deep copies
and local snapshots cover ordinary mutation through the supplied hook argument;
they do not protect against closure-captured references, module-global access,
monkeypatching, introspection, or other arbitrary in-process Python behavior.
