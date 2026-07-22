# Composite correspondence

## Candidate ecosystem correspondence

- **Status:** candidate correspondence
- **Paper wording:** Candidate correspondence plus constructive repository fixture.
- **Case:** OpenMontage Skill system (`calesthio/OpenMontage`)
- **Fixed upstream commit:** `db91727598d08d40919d7d68a47864a5467bd448`
- **Pipeline manifest:**
  [`pipeline_defs/animation.yaml`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/pipeline_defs/animation.yaml)
- **Manifest-selected orchestrator:**
  [`skills/pipelines/animation/executive-producer.md`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/skills/pipelines/animation/executive-producer.md)
- **Manifest-selected stage director:**
  [`skills/pipelines/animation/research-director.md`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/skills/pipelines/animation/research-director.md)
- **Pipeline loader:**
  [`lib/pipeline_loader.py`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/lib/pipeline_loader.py)
- **Corrected non-stage Skill:**
  [`.agents/skills/create-video/SKILL.md`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/.agents/skills/create-video/SKILL.md)
- **Vendored observation record:**
  [frozen evidence](evidence/openmontage-frozen-case.md)

The animation manifest explicitly selects an executive producer and stage
director instructions, and the loader exposes ordered stage and Skill lookup.
This supports a narrowly scoped candidate correspondence for a parent-like
workflow coordinating separately inspectable stages. The `create-video` Skill
is HeyGen vendor/API guidance and is not positive pipeline evidence.

The correspondence is not confirmed. OpenMontage stages declare different
artifact schemas, so a shared Leaf/Composite result contract is missing. The
stage relation may also be pipeline dependency rather than part-whole
containment, and the reviewed paths do not establish a single-parent reachable
tree or global cycle rejection. Agent Host and Agent Runtime remain execution
context rather than GoF participants.

## Constructive sample

- **Status:** constructive
- **Unit:** [`sample/SKILL.md`](sample/SKILL.md) and four child Skills
- **Component contract:**
  [`sample/references/section-contract.md`](sample/references/section-contract.md)
- **Serialized tree:**
  [`sample/fixtures/valid/investment-memo.json`](sample/fixtures/valid/investment-memo.json)
- **Executable oracle:** [`sample/scripts/run_demo.py`](sample/scripts/run_demo.py)
- **Focused verification:** [`sample/tests/test_demo.py`](sample/tests/test_demo.py)

In Agent mode the root instructions call each child Skill through the shared
contract. In demo mode explicit deterministic executors keyed by child Skill
model those calls; Python does not interpret `SKILL.md`. The builder invokes
each Leaf once in declared order, validates every returned Component record,
and assembles the root after validating the entire serialized tree.

The local sample is not evidence about OpenMontage, and OpenMontage does not
validate the sample. Neither claim supports prevalence, cross-Host equivalence,
or comparative quality improvement.
