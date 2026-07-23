# Strategy / 策略模式

This record transfers the canonical Gang of Four Strategy pattern to Skillware
through Risk-Aware Code Review / 风险感知代码审查. The root review Skill is the
Context, `risk-aware-code-review-v1` is the Strategy contract, and Fast Scan and
Deep Review child Skills are ConcreteStrategies.

The Context selects Deep Review for security-sensitive requests or at least
four files and Fast Scan otherwise. Both procedures accept the same request and
return the same result fields, can be injected or directly addressed, and are
validated at the delegation boundary.

The demo module separately preserves the compact plan-level
`review({"files": int, "security_sensitive": bool})` API, whose Deep Review
threshold is strictly greater than five files and whose exact result fields are
`strategy`, `findings`, and `confidence`. It is not interchangeable with the
richer file-content CLI contract. Its Context delegates exactly once to the
selected compact `fast_scan` or `deep_review` callable.

- [English definition](definition.md)
- [中文定义](definition.zh-CN.md)
- [Participant map](participant-map.yaml)
- [Correspondence assessment](correspondence.md)
- [Runnable sample](sample/)
- [Misuse discriminator](misuse/explanation.md)

## Case Skill: upstream implementation

**Case Skill:** `ui-ux-pro-max` at
`.claude/skills/ui-ux-pro-max/SKILL.md`.

The high-star comparison is [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill):
`.claude/skills/ui-ux-pro-max/SKILL.md` routes requests through
`scripts/search.py`, `scripts/core.py`, and `scripts/design_system.py` for
domain, stack, and design-system procedures. It remains candidate-only because
the cited paths do not prove one common substitution contract; see the [pinned
evidence record](../../docs/upstream-skill-evidence.md#strategy--策略模式).
The local demo makes Fast Scan and Deep Review interchangeable under one schema.

## Mock sample Skill: this repository

**Mock Skill:** [`sample/SKILL.md`](sample/SKILL.md), named
`risk-aware-code-review`. Its Context chooses either the `fast-scan` or
`deep-review` child Skill while preserving one request/result contract.

The Strategy idea is implemented by one selection policy plus interchangeable
procedures, not unrelated branches with different outputs. Run
`python3 sample/scripts/run_demo.py`; the mapping is in
[`participant-map.yaml`](participant-map.yaml).

The local sample is **constructive** evidence. UI/UX Pro Max is a **candidate
correspondence** at one fixed public revision: its tool routes among distinct
procedures, but the inspected paths do not establish one common interface or
substitution relation. Neither claim establishes ecosystem frequency,
production security quality, cross-Host equivalence, or comparative benefit.
