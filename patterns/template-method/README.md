# Template Method

Template Method fixes an algorithm skeleton in an AbstractClass while allowing
a ConcreteClass to redefine selected operations without changing the sequence.

This record constructs an Enterprise RFP Response workflow. The root owns
requirement extraction, gap analysis, one bounded domain hook, drafting, and
quality checking in exact order. Healthcare and Finance specialize only the
hook through one contract.

- [Definition](definition.md)
- [中文定义](definition.zh-CN.md)
- [Participant map](participant-map.yaml)
- [Correspondence](correspondence.md)
- [Constructive sample](sample/)
- [Misuse](misuse/explanation.md)

## Case Skill: upstream implementation

**Case Skills:** Superpowers' `skills/brainstorming/SKILL.md` and
`skills/test-driven-development/SKILL.md`.

The high-star comparison is [obra/superpowers](https://github.com/obra/superpowers):
`skills/brainstorming/SKILL.md` and
`skills/test-driven-development/SKILL.md` prescribe invariant ordered
workflows with bounded task-specific content. This is candidate correspondence
because a formal ConcreteClass hook contract is not visible in those files; see
the [pinned evidence record](../../docs/upstream-skill-evidence.md#template-method--模板方法).
The local demo exposes the hook as a complete healthcare or finance child Skill.

## Mock sample Skill: this repository

**Mock Skill:** [`sample/SKILL.md`](sample/SKILL.md), named
`enterprise-rfp-response`. It fixes five stages and allows only the
`healthcare` or `finance` child Skill to implement `apply-domain-hook`.

The Template Method idea is implemented by keeping stage order in the root
Skill while varying one bounded hook. Run
`python3 sample/scripts/run_demo.py`; the mapping is in
[`participant-map.yaml`](participant-map.yaml).

The sample is constructive evidence, not proof of production RFP quality,
ecosystem prevalence, or Agent Runtime interpretation.
