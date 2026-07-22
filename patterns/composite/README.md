# 组合模式（Composite）

This record transfers the canonical Gang of Four Composite pattern to
Skillware. It maps the task caller to Client, `memo-section-v1` to Component,
four independently inspectable analysis Skills to Leaves, and the root
investment-memo Skill plus serialized containment workflow to Composite.

The standalone sample is **Investment Memo Builder / 投资备忘录生成**. Every
node returns exactly `id`, `title`, `content`, `evidence`, and `children`.
Leaves return `children: []`; the root returns the same record shape with the
four child records in declared order.

- [English definition](definition.md)
- [中文定义](definition.zh-CN.md)
- [Participant map](participant-map.yaml)
- [Open-source correspondence](correspondence.md)
- [Runnable sample](sample/)
- [Misuse discriminator](misuse/explanation.md)

The local sample is constructive evidence. OpenMontage staged Skill workflows
are only a **candidate correspondence** because the frozen public evidence does
not completely establish a uniform Leaf/Composite result contract and explicit
acyclic part-whole tree. Neither claim establishes ecosystem frequency or a
comparative benefit.
