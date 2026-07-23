# Observer / 观察者模式

This record transfers the canonical Gang of Four Observer pattern to
Skillware. The Subject is the ordered release subscription and event contract;
the root Software Release Notification Skill plus deterministic publisher is
the ConcreteSubject. Audit, changelog, and team-notification Skills are
ConcreteObservers implementing one `release-observer-v1` update operation.

The sample publishes a typed `release.published.v1` event after a successful
release. It supports explicit registration and unregistration, deterministic
registration-order delivery, isolated event copies, per-observer receipts,
failure isolation, and publication re-entry rejection.

- [English definition](definition.md)
- [中文定义](definition.zh-CN.md)
- [Participant map](participant-map.yaml)
- [Open-source correspondence](correspondence.md)
- [Runnable sample](sample/)
- [Misuse discriminator](misuse/explanation.md)

## Case Skill: upstream implementation

**Case Skill:** ECC's `skills/continuous-learning-v2/SKILL.md`, activated by
the lifecycle hook configuration.

The high-star comparison is [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code):
`hooks/hooks.json` and `scripts/hooks/run-with-flags.js` route lifecycle/tool
events to the `skills/continuous-learning-v2/SKILL.md` observation workflow,
including `skills/continuous-learning-v2/hooks/observe.sh`. It is candidate-only
because registration and delivery accounting are not fully visible; see the
[pinned evidence record](../../docs/upstream-skill-evidence.md#observer--观察者模式).
The local sample supplies those contracts in [`sample/SKILL.md`](sample/SKILL.md).

## Mock sample Skill: this repository

**Mock Skill:** [`sample/SKILL.md`](sample/SKILL.md), named
`software-release-notification`. The root publishes one typed release event to
the `audit`, `changelog`, and `team-notification` child Skills.

The Observer idea is implemented by explicit registration, a frozen delivery
snapshot, isolated event copies, and per-observer receipts. Run
`python3 sample/scripts/run_demo.py`; the mapping is in
[`participant-map.yaml`](participant-map.yaml).

The local sample is **constructive** evidence. ECC hook artifacts are only a
**candidate correspondence** because pinned source shows event-to-handler
configuration and continuous-learning observation, but does not establish the
complete GoF registration, unregistration, deterministic delivery, and
failure-accounting relation. Neither claim establishes ecosystem frequency,
cross-Host equivalence, or comparative benefit.
