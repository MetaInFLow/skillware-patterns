# 备忘录模式（Memento）

This record transfers the canonical Gang of Four Memento pattern to Skillware.
It maps the configuration owner to **Originator**, the opaque exact-byte
checkpoint to **Memento**, and the migration workflow to **Caretaker**.

The standalone sample is **Configuration Migration / 配置迁移回滚**. A
successful run atomically increments `version` and disposes its checkpoint.
Preparation and conflict failures discard the checkpoint without restoration,
so a newer external value is not overwritten. Once a write is attempted, any
write or post-write validation failure invokes the owned restore path; original
bytes and portable permission bits are atomically reinstated before the
original error is re-raised. A failed restore is reported explicitly and never
mislabeled as recovery.

Start with [`definition.md`](definition.md), inspect the role mapping in
[`participant-map.yaml`](participant-map.yaml), then run the
[`sample`](sample/). The open-source record is candidate-only because SkillOpt
backs up before adoption but does not expose an owned restore path in the
inspected source.
