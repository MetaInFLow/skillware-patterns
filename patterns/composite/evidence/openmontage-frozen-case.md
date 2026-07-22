# OpenMontage frozen Composite candidate evidence

## Evidence identity

- **Claim status:** candidate correspondence
- **Paper wording:** Candidate correspondence plus constructive repository fixture.
- **Target repository:** [`calesthio/OpenMontage`](https://github.com/calesthio/OpenMontage)
- **Frozen commit:** `db91727598d08d40919d7d68a47864a5467bd448`
- **Evaluation unit:** OpenMontage's canonical Agent Skills, root workflow guide,
  and deterministic pipeline support at that commit
- **Method:** bounded source inspection recorded in the frozen public case

This local record vendors the concise observations and limits needed to audit
the candidate claim. It does not reproduce upstream code and does not treat the
constructive investment-memo sample as OpenMontage evidence.

## Public upstream evidence

- Staged video workflow Skill:
  [`.agents/skills/create-video/SKILL.md`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/.agents/skills/create-video/SKILL.md)
- Read-first routing Skill:
  [`.agents/skills/hyperframes/SKILL.md`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/.agents/skills/hyperframes/SKILL.md)
- Root workflow, stages, checkpoints, and lifecycle guide:
  [`AGENT_GUIDE.md`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/AGENT_GUIDE.md)
- Deterministic pipeline loading support:
  [`lib/pipeline_loader.py`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/lib/pipeline_loader.py)
- Checkpoint implementation used by the staged workflow:
  [`lib/checkpoint.py`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/lib/checkpoint.py)

The exact revision and paths come from the frozen OpenMontage case inventory.
No private repository or workstation-specific link is required to inspect the
public source.

## Candidate participant observations

- A task-level caller can be the **Client** of a root video workflow.
- A shared stage invocation/result surface could be the **Component**.
- Independently named atomic stage Skills could be **Leaves**.
- A parent workflow Skill plus pipeline composition could be the **Composite**.

The reviewed paths establish staged coordination and independently inspectable
Skills. They support investigation of this mapping, but they do not complete
all four participant relations.

## Missing or partial evidence

- The frozen case records staged Skills and pipeline tooling, but does not
  verify one exact invocation and result schema shared by atomic stages and
  nested stage groups.
- The reviewed paths do not fully prove that the stage relation is a declared
  part-whole tree rather than a workflow dependency graph.
- A complete acyclicity rule and full cycle path error were not observed in the
  bounded case record.
- Host bootstrap and Agent Runtime interpretation were not executed across
  supported environments.

For these reasons the status remains **candidate correspondence**, not a
confirmed mapping. Repository folders and repeated stage terminology cannot
fill the missing evidence.

## Claim boundary

The public artifacts support a concise claim that OpenMontage staged Skill
workflows are a candidate Composite correspondence at the frozen revision.
They do not establish a complete GoF Composite implementation, ecosystem
frequency, cross-Host behavioral equivalence, quality, robustness, or any
comparative benefit from using the pattern.
