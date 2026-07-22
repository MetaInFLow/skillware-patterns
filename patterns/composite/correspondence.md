# Composite correspondence

## Candidate ecosystem correspondence

- **Status:** candidate correspondence
- **Paper wording:** Candidate correspondence plus constructive repository fixture.
- **Case:** OpenMontage Skill system (`calesthio/OpenMontage`)
- **Fixed upstream commit:** `db91727598d08d40919d7d68a47864a5467bd448`
- **Staged workflow Skill:**
  [`.agents/skills/create-video/SKILL.md`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/.agents/skills/create-video/SKILL.md)
- **Routing Skill:**
  [`.agents/skills/hyperframes/SKILL.md`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/.agents/skills/hyperframes/SKILL.md)
- **Workflow guide:**
  [`AGENT_GUIDE.md`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/AGENT_GUIDE.md)
- **Pipeline loader:**
  [`lib/pipeline_loader.py`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/lib/pipeline_loader.py)
- **Vendored observation record:**
  [frozen evidence](evidence/openmontage-frozen-case.md)

The fixed public paths show a staged Skill workflow, a root routing surface,
and deterministic pipeline support. This is structurally compatible with a
parent Skill coordinating child stages. It remains a candidate because the
bounded frozen review does not fully establish that atomic stages and nested
stage groups return the same invocation/result contract, nor does it fully
establish an explicit acyclic part-whole tree. Those missing Composite
properties must not be inferred from repository nesting or the word "stage."

Agent Host and Agent Runtime are execution context. The public root files can
load instructions and a runtime can interpret them, but neither is a GoF
Composite participant by default.

## Constructive sample

- **Status:** constructive
- **Unit:** [`sample/SKILL.md`](sample/SKILL.md) and four child Skills
- **Component contract:**
  [`sample/references/section-contract.md`](sample/references/section-contract.md)
- **Serialized tree:**
  [`sample/fixtures/valid/investment-memo.json`](sample/fixtures/valid/investment-memo.json)
- **Executable oracle:** [`sample/scripts/run_demo.py`](sample/scripts/run_demo.py)
- **Focused verification:** [`sample/tests/test_demo.py`](sample/tests/test_demo.py)

The local sample demonstrates constructibility with a uniform record, recursive
child references, stable order, and explicit rejection of cycles and malformed
graphs. It is not evidence about OpenMontage. Conversely, OpenMontage does not
validate the local sample. Neither claim supports ecosystem prevalence,
cross-Host equivalence, or comparative quality improvement.
