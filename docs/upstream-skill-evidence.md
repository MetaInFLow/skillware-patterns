# Upstream Skill evidence

This page records the public Skill repositories used as concrete comparison
points for the ten detailed Gang of Four mappings. A star count is a discovery
context snapshot taken on **2026-07-23**; it is volatile and is not evidence of
pattern quality or correspondence strength. Each observation is pinned to a
commit and names the exact paths inspected.

## Facade / 外观模式

- **Project:** [obra/superpowers](https://github.com/obra/superpowers) (about
  259k stars on 2026-07-23).
- **Pinned revision:**
  [`896224c4b1879920ab573417e68fd51d2ccc9072`](https://github.com/obra/superpowers/tree/896224c4b1879920ab573417e68fd51d2ccc9072)
- **Exact locations:** [`skills/using-superpowers/SKILL.md`](https://github.com/obra/superpowers/blob/896224c4b1879920ab573417e68fd51d2ccc9072/skills/using-superpowers/SKILL.md), [`hooks/session-start`](https://github.com/obra/superpowers/blob/896224c4b1879920ab573417e68fd51d2ccc9072/hooks/session-start), [`hooks/hooks.json`](https://github.com/obra/superpowers/blob/896224c4b1879920ab573417e68fd51d2ccc9072/hooks/hooks.json).
- **Observed use:** `using-superpowers` provides one bootstrap and selection/invocation policy over specialist Skills; the session-start hook injects that policy into the Host session. This is a **confirmed correspondence**, bounded to the entry-policy/subsystem relation; it does not establish runtime equivalence or quality improvement.
- **Local analogue:** [`patterns/facade/sample/SKILL.md`](../patterns/facade/sample/SKILL.md) and its three specialist Skills.

## Adapter / 适配器模式

- **Project:** [garrytan/gstack](https://github.com/garrytan/gstack) (about
  124k stars on 2026-07-23).
- **Pinned revision:**
  [`11de390be1be6849eb9a15f91ff4922dd16c589a`](https://github.com/garrytan/gstack/tree/11de390be1be6849eb9a15f91ff4922dd16c589a)
- **Exact locations:** [`SKILL.md.tmpl`](https://github.com/garrytan/gstack/blob/11de390be1be6849eb9a15f91ff4922dd16c589a/SKILL.md.tmpl), [`SKILL.md`](https://github.com/garrytan/gstack/blob/11de390be1be6849eb9a15f91ff4922dd16c589a/SKILL.md), [`scripts/gen-skill-docs.ts`](https://github.com/garrytan/gstack/blob/11de390be1be6849eb9a15f91ff4922dd16c589a/scripts/gen-skill-docs.ts), [`hosts/claude.ts`](https://github.com/garrytan/gstack/blob/11de390be1be6849eb9a15f91ff4922dd16c589a/hosts/claude.ts), [`hosts/codex.ts`](https://github.com/garrytan/gstack/blob/11de390be1be6849eb9a15f91ff4922dd16c589a/hosts/codex.ts), [`test/codex-e2e.test.ts`](https://github.com/garrytan/gstack/blob/11de390be1be6849eb9a15f91ff4922dd16c589a/test/codex-e2e.test.ts).
- **Observed use:** a canonical Skill template is translated into Host-specific paths, frontmatter, tool names, setup, and invocation surfaces. This is a **confirmed correspondence** for semantic/host translation; source inspection does not prove runtime parity.
- **Local analogue:** [`patterns/adapter/sample/SKILL.md`](../patterns/adapter/sample/SKILL.md) with GitHub, Jira, and Linear child bindings.

## Composite / 组合模式

- **Project:** [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) (about 41.2k stars on 2026-07-23).
- **Pinned revision:** [`db91727598d08d40919d7d68a47864a5467bd448`](https://github.com/calesthio/OpenMontage/tree/db91727598d08d40919d7d68a47864a5467bd448)
- **Exact locations:** [`pipeline_defs/animation.yaml`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/pipeline_defs/animation.yaml), [`skills/pipelines/animation/executive-producer.md`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/skills/pipelines/animation/executive-producer.md), [`skills/pipelines/animation/research-director.md`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/skills/pipelines/animation/research-director.md), [`lib/pipeline_loader.py`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/lib/pipeline_loader.py).
- **Observed use:** a named pipeline composes stage Skills and a loader resolves the declared graph. It is a **candidate correspondence** only: the inspected artifacts do not establish a uniform Leaf/Composite result contract or a strict part-whole tree.
- **Local analogue:** [`patterns/composite/sample/SKILL.md`](../patterns/composite/sample/SKILL.md) and the four uniform Leaf Skills.

## Observer / 观察者模式

- **Project:** [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) (about 232k stars on 2026-07-23).
- **Pinned revision:** [`2bc924faf2f8e893bfe0af86b1931283693c30ae`](https://github.com/affaan-m/everything-claude-code/tree/2bc924faf2f8e893bfe0af86b1931283693c30ae)
- **Exact locations:** [`hooks/hooks.json`](https://github.com/affaan-m/everything-claude-code/blob/2bc924faf2f8e893bfe0af86b1931283693c30ae/hooks/hooks.json), [`scripts/hooks/run-with-flags.js`](https://github.com/affaan-m/everything-claude-code/blob/2bc924faf2f8e893bfe0af86b1931283693c30ae/scripts/hooks/run-with-flags.js), [`skills/continuous-learning-v2/SKILL.md`](https://github.com/affaan-m/everything-claude-code/blob/2bc924faf2f8e893bfe0af86b1931283693c30ae/skills/continuous-learning-v2/SKILL.md), [`skills/continuous-learning-v2/hooks/observe.sh`](https://github.com/affaan-m/everything-claude-code/blob/2bc924faf2f8e893bfe0af86b1931283693c30ae/skills/continuous-learning-v2/hooks/observe.sh), [`tests/hooks/hooks.test.js`](https://github.com/affaan-m/everything-claude-code/blob/2bc924faf2f8e893bfe0af86b1931283693c30ae/tests/hooks/hooks.test.js).
- **Observed use:** lifecycle/tool events are routed to an observation handler and the continuous-learning Skill records observations. It is a **candidate correspondence** because explicit registration, unregistration, deterministic delivery, and failure accounting are not all observable.
- **Local analogue:** [`patterns/observer/sample/SKILL.md`](../patterns/observer/sample/SKILL.md) and the three registered consumer Skills.

## State / 状态模式

- **Project:** [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) (about 41.2k stars on 2026-07-23).
- **Pinned revision:** [`db91727598d08d40919d7d68a47864a5467bd448`](https://github.com/calesthio/OpenMontage/tree/db91727598d08d40919d7d68a47864a5467bd448)
- **Exact locations:** [`AGENT_GUIDE.md`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/AGENT_GUIDE.md), [`lib/checkpoint.py`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/lib/checkpoint.py), [`skills/meta/checkpoint-protocol.md`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/skills/meta/checkpoint-protocol.md), [`schemas/checkpoints/checkpoint.schema.json`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/schemas/checkpoints/checkpoint.schema.json).
- **Observed use:** persisted checkpoint status controls resume and next-stage behavior. It is a **candidate correspondence** because separate ConcreteState ownership and explicit transition delegation are not established by the frozen paths.
- **Local analogue:** [`patterns/state/sample/SKILL.md`](../patterns/state/sample/SKILL.md) and its four persisted ConcreteState Skills.

## Strategy / 策略模式

- **Project:** [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (about 109k stars on 2026-07-23).
- **Pinned revision:** [`8a81ed60272d21d4b8808f7308d49a0b1b000555`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/8a81ed60272d21d4b8808f7308d49a0b1b000555)
- **Exact locations:** [`.claude/skills/ui-ux-pro-max/SKILL.md`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/8a81ed60272d21d4b8808f7308d49a0b1b000555/.claude/skills/ui-ux-pro-max/SKILL.md), [`scripts/search.py`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/8a81ed60272d21d4b8808f7308d49a0b1b000555/scripts/search.py), [`scripts/core.py`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/8a81ed60272d21d4b8808f7308d49a0b1b000555/scripts/core.py), [`scripts/design_system.py`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/8a81ed60272d21d4b8808f7308d49a0b1b000555/scripts/design_system.py).
- **Observed use:** a router selects domain, stack, and design-system procedures. It is a **candidate correspondence** because outputs and substitution under one common contract are not fully evidenced.
- **Local analogue:** [`patterns/strategy/sample/SKILL.md`](../patterns/strategy/sample/SKILL.md) with Fast Scan and Deep Review.

## Decorator / 装饰模式

- **Project:** [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) (about 92.1k stars on 2026-07-23).
- **Pinned revision:** [`25d22f864ad68cc447a4cb93aefde918aa4aec9f`](https://github.com/JuliusBrussee/caveman/tree/25d22f864ad68cc447a4cb93aefde918aa4aec9f)
- **Exact locations:** [`src/hooks/caveman-activate.js`](https://github.com/JuliusBrussee/caveman/blob/25d22f864ad68cc447a4cb93aefde918aa4aec9f/src/hooks/caveman-activate.js), [`skills/caveman/SKILL.md`](https://github.com/JuliusBrussee/caveman/blob/25d22f864ad68cc447a4cb93aefde918aa4aec9f/skills/caveman/SKILL.md).
- **Observed use:** an activation hook adds session behavior around the Host's existing interaction surface. It is a **candidate correspondence** because a common Component result contract and explicit delegation boundary are not fully observable.
- **Local analogue:** [`patterns/decorator/sample/SKILL.md`](../patterns/decorator/sample/SKILL.md) and its contract-preserving wrappers.

## Template Method / 模板方法

- **Project:** [obra/superpowers](https://github.com/obra/superpowers) (about
  259k stars on 2026-07-23).
- **Pinned revision:** [`896224c4b1879920ab573417e68fd51d2ccc9072`](https://github.com/obra/superpowers/tree/896224c4b1879920ab573417e68fd51d2ccc9072)
- **Exact locations:** [`skills/brainstorming/SKILL.md`](https://github.com/obra/superpowers/blob/896224c4b1879920ab573417e68fd51d2ccc9072/skills/brainstorming/SKILL.md), [`skills/test-driven-development/SKILL.md`](https://github.com/obra/superpowers/blob/896224c4b1879920ab573417e68fd51d2ccc9072/skills/test-driven-development/SKILL.md).
- **Observed use:** the Skills prescribe invariant ordered workflows while allowing task-specific content at bounded steps. It is a **candidate correspondence** because a formal ConcreteClass hook contract is not observable from the cited files alone.
- **Local analogue:** [`patterns/template-method/sample/SKILL.md`](../patterns/template-method/sample/SKILL.md) with healthcare and finance hook Skills.

## Memento / 备忘录模式

- **Project:** [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt) (about 14.5k stars on 2026-07-23).
- **Pinned revision:** [`b860a5cf88ce75e2bd02ca981ac21fb28cffba83`](https://github.com/microsoft/SkillOpt/tree/b860a5cf88ce75e2bd02ca981ac21fb28cffba83)
- **Exact location:** [`skillopt_sleep/staging.py`](https://github.com/microsoft/SkillOpt/blob/b860a5cf88ce75e2bd02ca981ac21fb28cffba83/skillopt_sleep/staging.py).
- **Observed use:** staging creates a backup before adopting a candidate Skill configuration. It is a **candidate correspondence** because an owned, opaque restore operation and complete Caretaker lifecycle are not observable.
- **Local analogue:** [`patterns/memento/sample/SKILL.md`](../patterns/memento/sample/SKILL.md) with exact-byte capture and restore.

## Mediator / 中介者模式

- **Project:** [anthropics/financial-services](https://github.com/anthropics/financial-services) (about 33.7k stars on 2026-07-23).
- **Pinned revision:** [`4aa51ed3d379731f8f9beff498d749580372699c`](https://github.com/anthropics/financial-services/tree/4aa51ed3d379731f8f9beff498d749580372699c)
- **Exact locations:** [`managed-agent-cookbooks/gl-reconciler/agent.yaml`](https://github.com/anthropics/financial-services/blob/4aa51ed3d379731f8f9beff498d749580372699c/managed-agent-cookbooks/gl-reconciler/agent.yaml), [`subagents/reader.yaml`](https://github.com/anthropics/financial-services/blob/4aa51ed3d379731f8f9beff498d749580372699c/subagents/reader.yaml), [`subagents/critic.yaml`](https://github.com/anthropics/financial-services/blob/4aa51ed3d379731f8f9beff498d749580372699c/subagents/critic.yaml), [`subagents/resolver.yaml`](https://github.com/anthropics/financial-services/blob/4aa51ed3d379731f8f9beff498d749580372699c/subagents/resolver.yaml), [`scripts/test-cookbooks.sh`](https://github.com/anthropics/financial-services/blob/4aa51ed3d379731f8f9beff498d749580372699c/scripts/test-cookbooks.sh).
- **Observed use:** one cookbook orchestrates isolated reader, critic, and resolver workers through a central agent configuration. It is a **candidate correspondence** because a shared Colleague operation and runtime decision boundary are not established.
- **Local analogue:** [`patterns/mediator/sample/SKILL.md`](../patterns/mediator/sample/SKILL.md) and its four isolated readiness checks.

## Interpretation boundary

These comparisons are source observations, not claims that upstream authors used
GoF terminology. The local samples are complete, deterministic Skill artifacts
with offline Python oracles; the upstream links are empirical evidence about
recurring Skill structures. Agent Host and Agent Runtime remain contextual
execution layers in every mapping.
