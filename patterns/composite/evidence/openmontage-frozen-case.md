# OpenMontage frozen Composite candidate evidence

## Evidence identity

- **Claim status:** candidate correspondence
- **Paper wording:** Candidate correspondence plus constructive repository fixture.
- **Target repository:** `calesthio/OpenMontage`
- **Frozen commit:** `db91727598d08d40919d7d68a47864a5467bd448`
- **Evaluation unit:** the animation pipeline manifest, its executive producer,
  one declared stage director, and the pipeline loader at that commit
- **Method:** bounded source inspection of the exact public artifacts below

This local record vendors concise observations and limits. It does not
reproduce upstream code or use the constructive investment-memo sample as
OpenMontage evidence.

## Public upstream evidence

- Animation pipeline manifest:
  [`pipeline_defs/animation.yaml`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/pipeline_defs/animation.yaml)
- Manifest-selected orchestrator:
  [`skills/pipelines/animation/executive-producer.md`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/skills/pipelines/animation/executive-producer.md)
- Manifest-selected atomic stage director:
  [`skills/pipelines/animation/research-director.md`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/skills/pipelines/animation/research-director.md)
- Manifest loading and stage lookup:
  [`lib/pipeline_loader.py`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/lib/pipeline_loader.py)
- Corrected negative evidence:
  [`.agents/skills/create-video/SKILL.md`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/.agents/skills/create-video/SKILL.md)
  is vendor/API guidance, not pipeline-stage evidence.

At this revision, `pipeline_defs/animation.yaml` names the executive producer
as its orchestration Skill, declares an ordered `stages` list, and associates
the research stage with `pipelines/animation/research-director`. The executive
producer says it loads the manifest and each director in order. The loader
validates manifests and exposes stage order and stage-Skill lookup. These
observations establish staged coordination with separately inspectable stage
instructions.

## Candidate participant observations

- A task-level caller could be the **Client** of the animation pipeline.
- The executive producer plus manifest is structurally parent-like.
- The research director and other manifest-selected directors are separately
  inspectable stage units.

This is evidence for investigating a Composite mapping, not confirmation of
the complete participant relation.

## Missing or partial evidence

- The manifest declares different stage artifact schemas such as
  `research_brief`, `proposal_packet`, and `script`; one uniform Leaf/Composite
  invocation and result contract is not established.
- The ordered stage and artifact-dependency relation may be a pipeline graph
  rather than a GoF part-whole tree.
- The reviewed upstream implementation does not establish the one-parent,
  reachability, repeated-child, and global acyclicity invariants used by the
  constructive Composite sample.
- The stage director files are manifest-addressed Markdown instructions, not
  evidence that Python interprets `SKILL.md` or that all Hosts invoke them
  equivalently.

The status therefore remains **candidate correspondence** and is narrower than
a claim that OpenMontage implements Composite.

## Claim boundary

The pinned artifacts support only a candidate correspondence based on explicit
manifest-to-orchestrator-to-stage relationships. They do not establish a
complete GoF Composite, ecosystem frequency, cross-Host equivalence, quality,
robustness, or comparative benefit.
