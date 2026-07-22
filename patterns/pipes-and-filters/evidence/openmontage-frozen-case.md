# OpenMontage frozen Pipes and Filters candidate

- **Project:** calesthio/OpenMontage
- **Pinned revision:** `db91727598d08d40919d7d68a47864a5467bd448`
- **Claim status:** candidate correspondence

## Inspected paths

- [animated-explainer manifest](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/pipeline_defs/animated-explainer.yaml)
- [pipeline loader](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/lib/pipeline_loader.py)
- [research director](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/skills/pipelines/explainer/research-director.md)
- [proposal director](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/skills/pipelines/explainer/proposal-director.md)
- [script director](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/skills/pipelines/explainer/script-director.md)
- [scene director](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/skills/pipelines/explainer/scene-director.md)
- [asset director](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/skills/pipelines/explainer/asset-director.md)
- [edit director](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/skills/pipelines/explainer/edit-director.md)
- [compose director](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/skills/pipelines/explainer/compose-director.md)
- [publish director](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/skills/pipelines/explainer/publish-director.md)

## Observed source structure

The manifest contains ordered `stages`. Its entries name stage Skills and use
`required_artifacts_in` and `produces` to describe adjacent artifact flow. The
loader validates a selected manifest, `get_stage_order` reads manifest order,
and `get_stage_skill` reads the declared Skill identifier. The eight pinned stage director files
provide stage-specific instruction surfaces. The manifest names its executive
producer separately under orchestration, not as a ninth stage.

This is source evidence for independently named processing stages connected by
declared artifacts. It is sufficient for a candidate, not confirmation.

## Counterevidence and limits

The common versioned record envelope remains unverified: the manifest names
different artifacts rather than demonstrating one invariant record schema.
The filter isolation remains unverified because the inspected files do not
prove that a stage cannot read shared state or mutate aliases. The runtime behavior remains unverified
because the pinned media pipeline was not executed for this record.
Buffering, backpressure, concurrency, network transport, failure propagation,
and replay behavior were also not established. The claim is candidate-only.
