---
name: contract-review-enhancers
description: Compose privacy and citation checks around one contract review interface. Use when review responsibilities must vary without changing the base Skill.
intent: Validate one contract-review request, invoke a wrapped Component exactly once, and add ordered findings without changing the Component contract.
type: workflow
---

# Contract Review Enhancers / 合同审查增强

## Trigger

Use this root Skill when contract text must pass through a stable base review
and optional privacy or citation responsibilities. Input and output must satisfy
[`contract-review-v1`](references/contract-review-component.md).

## Participants

The shared `contract-review-v1` interface is the Component. Base Contract
Review is the ConcreteComponent. A contract-preserving wrapper is the
Decorator role. Privacy Check, Citation Check, and optional Compliance Check
are ConcreteDecorator child Skill Artifacts.

Agent Host and Agent Runtime are execution context, not Decorator
participants.

## Agent mode

1. Validate exactly one `text` request field before invoking any Component.
   Reject duplicate JSON members at every depth, invalid UTF-8, lone Unicode
   surrogates, unknown fields, wrong types, blank text, and text over the
   declared bound. Reject non-string programmatic mapping keys, cyclic values,
   structures deeper than 64 levels, and parser recursion failures through
   controlled validation errors.
2. Begin with Base Contract Review. For each requested decorator in
   inside-to-outside order, wrap the current Component rather than copying or
   replacing its review procedure.
3. Invoke the resulting Component once. At every wrapper boundary, pass an
   isolated request copy, validate and copy the wrapped result, then add only
   that wrapper's bounded finding when its condition matches and its exact
   `(type, message)` identity is not already present.
4. Preserve exactly the `summary` and `findings` top-level fields. Preserve the
   wrapped summary and existing finding order. Append an inner wrapper's
   finding before an outer wrapper's finding. Reject duplicate finding
   identities returned by a Component; repeated identical decorators are
   idempotent and do not append duplicates. The contract places no finite cap
   on the number of otherwise valid findings.
5. Propagate wrapped Component failures unchanged. Do not synthesize a partial
   result or expose references owned by the caller or wrapped Component.

The manifest's canonical executable identifiers are `privacy-check`,
`citation-check`, and optional `compliance-check`. The exact plan default is
Base Contract Review, then Privacy Check, then Citation Check; Compliance Check
is not enabled by default. In Python notation the default is
`with_citation_check(with_privacy_check(base_review))`.

## 中文执行约定

当合同文本需要在不改变基础审查接口的前提下叠加隐私或引用检查时，
使用本根 Skill。输入必须仅包含 `text`，输出必须仅包含
`summary` 和 `findings`。每个装饰器只调用被包装组件一次，不复制
基础审查逻辑；先追加内层结果，再追加外层结果。相同 `(type, message)`
是发现身份，重复包装不得重复追加。每个边界都要复制并
校验请求与结果，被包装组件失败时原样传播异常。

## Demo mode and root harness

The deterministic Python oracle models contract preservation and wrapper
composition; it does not interpret these Skill files. From `sample/`, run:

```bash
python3 scripts/run_demo.py
python3 -m unittest discover tests -v
```

The repository root harness automatically copies this record to an isolated
directory, runs the focused tests, and runs the default demo without network or
imports from another pattern.

## Limits

The three lexical checks are bounded demonstrations, not legal, privacy,
citation, or compliance assurance. A hook is not automatically a Decorator. It must wrap a
Component, preserve the same interface, delegate, and add a responsibility
without replacing the base behavior.
