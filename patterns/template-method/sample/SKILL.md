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
   isolated `rfp-domain-hook-v1` request, invoke the hook exactly once, and
   validate and copy its result before drafting.
4. Permit the ConcreteClass to supply only domain `focus_areas` and
   `required_evidence`. It must not skip, insert, repeat, or reorder any
   mandatory stage, and must not own the final response or quality decision.
5. If the hook fails, propagate that failure unchanged and stop before drafting
   or quality checking. Never fabricate a partial success result.
6. Validate the final result, including the exact stage sequence, domain and
   RFP identity, requirement order, hook result, draft coverage, and quality
   fields. Return isolated deterministic data.

## 中文执行约定

本根 Skill 是 AbstractClass，拥有完整且不可重排的模板方法：
先提取需求，再分析缺口，仅调用一次领域钩子，然后起草并质检。
医疗与金融子 Skill 是 ConcreteClass，只能实现
`apply-domain-hook`，不得更改必经阶段。钩子失败时原样传播异常，
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

## Limits

The domain content is illustrative and is not a legal, compliance, clinical,
security, procurement, or financial assurance. Selecting a runtime-swappable
whole RFP algorithm would be Strategy. Letting a domain profile reorder the
checklist removes the Template Method invariant.
