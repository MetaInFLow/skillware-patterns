# Decorator / 装饰模式

This record transfers the canonical Gang of Four Decorator pattern to Skillware
through Contract Review Enhancers / 合同审查增强. `contract-review-v1` is the
Component, Base Contract Review is the ConcreteComponent, the shared wrapper
protocol is the Decorator, and Privacy Check, Citation Check, and optional
Compliance Check are ConcreteDecorators.

The default composition is
`with_citation_check(with_privacy_check(base_review))`. It accepts exactly
`text` and returns exactly `summary` and `findings`; base findings precede
privacy, which precedes citation. Compliance is available but excluded from
that exact plan default. Reversing nesting reverses only the enabled
enhancements. Every wrapper delegates once, preserves the wrapped summary and
failure, copies values at participant boundaries, and suppresses an already
present identical `(type, message)` finding.

- [English definition](definition.md)
- [中文定义](definition.zh-CN.md)
- [Participant map](participant-map.yaml)
- [Correspondence assessment](correspondence.md)
- [Runnable sample](sample/)
- [Misuse discriminator](misuse/explanation.md)

## Upstream Skill example

The high-star comparison is [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman):
`src/hooks/caveman-activate.js` adds activation/session behavior around the
`skills/caveman/SKILL.md` surface. This is candidate correspondence because
the common Component result and explicit delegate boundary are not fully
observable; see the [pinned evidence record](../../docs/upstream-skill-evidence.md#decorator--装饰模式).
The local demo gives each wrapper a complete contract-preserving Skill.

The local sample is **constructive** evidence. Caveman is a **candidate
correspondence** at one fixed public revision: its activation hook adds
behavior around session start while preserving its process/stdout Host
interaction surface, but the inspected paths do not establish complete GoF
Component contract equivalence or runtime behavior. Neither claim establishes
ecosystem frequency, legal review quality, cross-Host equivalence, Agent
Runtime interpretation, or comparative benefit.
