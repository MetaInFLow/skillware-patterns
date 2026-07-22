# Strategy / 策略模式

This record transfers the canonical Gang of Four Strategy pattern to Skillware
through Risk-Aware Code Review / 风险感知代码审查. The root review Skill is the
Context, `risk-aware-code-review-v1` is the Strategy contract, and Fast Scan and
Deep Review child Skills are ConcreteStrategies.

The Context selects Deep Review for security-sensitive requests or at least
four files and Fast Scan otherwise. Both procedures accept the same request and
return the same result fields, can be injected or directly addressed, and are
validated at the delegation boundary.

- [English definition](definition.md)
- [中文定义](definition.zh-CN.md)
- [Participant map](participant-map.yaml)
- [Correspondence assessment](correspondence.md)
- [Runnable sample](sample/)
- [Misuse discriminator](misuse/explanation.md)

The local sample is **constructive** evidence. UI/UX Pro Max is a **candidate
correspondence** at one fixed public revision: its tool routes among distinct
procedures, but the inspected paths do not establish one common interface or
substitution relation. Neither claim establishes ecosystem frequency,
production security quality, cross-Host equivalence, or comparative benefit.
