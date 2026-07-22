# Decorator / 装饰模式

This record transfers the canonical Gang of Four Decorator pattern to Skillware
through Contract Review Enhancers / 合同审查增强. `contract-review-v1` is the
Component, Base Contract Review is the ConcreteComponent, the shared wrapper
protocol is the Decorator, and Privacy Check and Citation Check are
ConcreteDecorators.

The default composition is
`with_citation_check(with_privacy_check(base_review))`. It accepts exactly
`text` and returns exactly `summary` and `findings`; base findings precede
privacy, which precedes citation. Reversing nesting reverses only the two
enhancement findings. Every wrapper delegates once, preserves the wrapped
summary and failure, and copies input and results at participant boundaries.

- [English definition](definition.md)
- [中文定义](definition.zh-CN.md)
- [Participant map](participant-map.yaml)
- [Correspondence assessment](correspondence.md)
- [Runnable sample](sample/)
- [Misuse discriminator](misuse/explanation.md)

The local sample is **constructive** evidence. No public pinned ecosystem case
is assessed for this record, so it makes no candidate or confirmed
correspondence claim. The construction does not establish ecosystem frequency,
legal review quality, cross-Host equivalence, Agent Runtime interpretation, or
comparative benefit.
