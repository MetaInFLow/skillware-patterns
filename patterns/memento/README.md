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

## Case Skill: upstream implementation

**Case Skill:** Microsoft SkillOpt's staging implementation at
`skillopt_sleep/staging.py`.

The high-star comparison is [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt):
`skillopt_sleep/staging.py` creates a backup before adopting a candidate Skill
configuration. It is candidate correspondence because an owned opaque restore
operation is not observable; the pinned path and limitation are in the [evidence
record](../../docs/upstream-skill-evidence.md#memento--备忘录模式). The local
demo implements exact-byte capture, validation, and restoration.

## Mock sample Skill: this repository

**Mock Skill:** [`sample/SKILL.md`](sample/SKILL.md), named
`configuration-migration`. The `configuration-originator` creates an opaque
checkpoint, while the root and `migration-caretaker` decide when to restore or
discard it.

The Memento idea is implemented by hiding exact prior bytes from the Caretaker
and enforcing one-use ownership, checksum, and lifecycle checks. Run
`python3 sample/scripts/run_demo.py --fail`; the mapping is in
[`participant-map.yaml`](participant-map.yaml).
