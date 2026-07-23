# 外观模式（Facade）

This record transfers the Gang of Four Facade pattern to Skillware. It maps a
stable entry Skill to the Facade, independently addressable specialist Skills
to the subsystem, and the operator or task-level agent execution to the
Client.

The standalone sample is **Production Incident Response / 生产事故响应**. Its
root Skill accepts `service` and `signal`, coordinates three specialist Skills,
and always returns `summary`, `impact`, `actions`, and `communication`.

- [English definition](definition.md)
- [中文定义](definition.zh-CN.md)
- [Participant map](participant-map.yaml)
- [Open-source correspondence](correspondence.md)
- [Runnable sample](sample/)
- [Misuse discriminator](misuse/explanation.md)

## Upstream Skill example

The high-star comparison is [obra/superpowers](https://github.com/obra/superpowers):
`skills/using-superpowers/SKILL.md` is the stable entry policy, while
`hooks/session-start` and `hooks/hooks.json` activate it over specialist Skills.
The observation is pinned and qualified in the
[upstream evidence record](../../docs/upstream-skill-evidence.md#facade--外观模式).
The complete offline local analogue is [`sample/SKILL.md`](sample/SKILL.md).

The constructive sample and the confirmed Superpowers correspondence are
separate evidence claims. Neither establishes ecosystem frequency,
cross-Host equivalence, or an improvement in quality.
