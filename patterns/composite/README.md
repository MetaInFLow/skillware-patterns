# 组合模式（Composite）

This record transfers the canonical Gang of Four Composite pattern to
Skillware. It maps the task caller to Client, `memo-section-v1` to Component,
four independently inspectable analysis Skills to Leaves, and the root
investment-memo Skill plus serialized containment workflow to Composite.

The standalone sample is **Investment Memo Builder / 投资备忘录生成**. Every
node returns exactly `id`, `title`, `content`, `evidence`, and `children`.
Leaves return `children: []`; the root returns the same record shape with the
four child records in declared order. In Agent mode the root invokes the child
Skills. In demo mode deterministic executors keyed by those Skill paths compute
the same Leaf contract from serialized inputs; Python does not interpret
`SKILL.md`.

- [English definition](definition.md)
- [中文定义](definition.zh-CN.md)
- [Participant map](participant-map.yaml)
- [Open-source correspondence](correspondence.md)
- [Runnable sample](sample/)
- [Misuse discriminator](misuse/explanation.md)

## Upstream Skill example

The high-star comparison is [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage):
`pipeline_defs/animation.yaml` composes the stage Skills
`skills/pipelines/animation/executive-producer.md` and
`skills/pipelines/animation/research-director.md`, resolved by
`lib/pipeline_loader.py`. This remains a candidate correspondence, with exact
paths in the [upstream evidence record](../../docs/upstream-skill-evidence.md#composite--组合模式).
The local demo makes the shared Leaf/Composite result contract explicit in
[`sample/SKILL.md`](sample/SKILL.md).

The local sample is constructive evidence. OpenMontage staged Skill workflows
are only a **candidate correspondence** because the frozen public evidence does
not establish a uniform Leaf/Composite result contract or explicit part-whole
tree. The pinned animation pipeline uses different stage artifact schemas, and
the relation may instead be a pipeline dependency graph. Neither claim
establishes ecosystem frequency or comparative benefit.
