# State / 状态模式

This record transfers the canonical Gang of Four State pattern to Skillware
through a Vendor Onboarding Workflow / 供应商接入工作流. The persisted workflow is
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

The local sample is **constructive** evidence. No fixed public ecosystem case
was assessed for this record, so it claims no confirmed or candidate ecosystem
correspondence. The sample does not establish ecosystem frequency, production
reliability, cross-Host equivalence, or comparative benefit.
