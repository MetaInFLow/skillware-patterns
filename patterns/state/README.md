# State / 状态模式

This record transfers the canonical Gang of Four State pattern to Skillware
through a Vendor Onboarding Workflow / 供应商准入流程. The persisted workflow is
the Context, `vendor-onboarding-state-v1` is the State contract, and four child
Skills are ConcreteStates for draft, verified, approved, and activated.

Each ConcreteState owns its permitted action and successor. The Context reloads
persisted state before delegation and atomically commits only a legal result:
`draft --verify--> verified --approve--> approved --activate--> activated`.

- [English definition](definition.md)
- [中文定义](definition.zh-CN.md)
- [Participant map](participant-map.yaml)
- [Correspondence assessment](correspondence.md)
- [Runnable sample](sample/)
- [Misuse discriminator](misuse/explanation.md)

## Upstream Skill example

The high-star comparison is [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage):
`lib/checkpoint.py` persists stage status described by
`skills/meta/checkpoint-protocol.md` and
`schemas/checkpoints/checkpoint.schema.json`, with lifecycle guidance in
`AGENT_GUIDE.md`. This is candidate correspondence rather than a complete GoF
State claim; the frozen paths and limits are in the [evidence record](../../docs/upstream-skill-evidence.md#state--状态模式).
The local sample supplies explicit ConcreteState Skills and restart recovery.

The local sample is **constructive** evidence. OpenMontage checkpoint behavior
is a **candidate correspondence** at one fixed public revision: persisted
checkpoint status controls resume and next-stage behavior, but the reviewed
paths do not establish the complete GoF participant relation. Neither claim
establishes ecosystem frequency, production reliability, cross-Host
equivalence, or comparative benefit.
