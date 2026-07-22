# Superpowers frozen Template Method candidate evidence

## Evidence identity

- **Claim status:** candidate correspondence
- **Paper wording:** Superpowers workflows are an invariant-skeleton candidate;
  bounded specialization and runtime behavior remain unverified.
- **Target repository:** `obra/superpowers`
- **Frozen commit:** `896224c4b1879920ab573417e68fd51d2ccc9072`
- **Evaluation unit:** two workflow Skill Artifacts at the fixed revision
- **Method:** bounded static inspection of only the exact public paths below

This record does not infer participant completeness from the word "workflow",
copy upstream source, or claim Agent Runtime execution.

## Fixed source paths

1. [`skills/brainstorming/SKILL.md`](https://github.com/obra/superpowers/blob/896224c4b1879920ab573417e68fd51d2ccc9072/skills/brainstorming/SKILL.md)
2. [`skills/test-driven-development/SKILL.md`](https://github.com/obra/superpowers/blob/896224c4b1879920ab573417e68fd51d2ccc9072/skills/test-driven-development/SKILL.md)

Both blob URLs resolve to the full 40-character public commit. No repository
root, moving branch, release note, hook, or unrelated workflow is counted as
participant evidence.

## Observed invariant skeleton behavior

`skills/brainstorming/SKILL.md` explicitly says its checklist items must be
completed in order. Its process flow fixes context exploration, questions,
approach comparison, design presentation and approval, written specification,
self-review, user review, and the final transition to writing plans. Revisions
loop back through declared gates rather than allowing a task-specific profile
to rearrange the workflow.

`skills/test-driven-development/SKILL.md` fixes Red, verified Red, Green,
verified Green, Refactor, and repeat. It identifies the order as mandatory and
treats implementation before an observed failing test as a violation. This is
direct static evidence that a workflow Skill can own an invariant algorithm
skeleton.

## Participant audit

- **AbstractClass:** partially suggested. Each inspected workflow Skill owns
  mandatory order and step policies analogous to a template skeleton.
- **ConcreteClass:** unverified. Neither inspected path declares a common
  specialization contract with multiple domain implementations that may
  replace only one primitive operation.

The paths therefore do not establish a bounded domain hook, ConcreteClass
substitution, or enforcement that a specialization cannot reorder mandatory
stages. Those relations are constructed locally in the Enterprise RFP Response
sample and cannot upgrade the upstream evidence.

## Counterevidence and limits

The inspected workflows adapt their prompts and artifacts to task context, but
ordinary task variation is not ConcreteClass substitution. No declared
`apply-domain-hook`-like contract connects multiple specializations to either
workflow. Static prose inspection also cannot show which Agent Host activated a
Skill Artifact, whether an Agent Runtime followed every gate, or what Task
Outcome resulted. Agent Runtime behavior is unverified.

The proper claim remains **candidate correspondence**. The invariant skeleton
is supported at exact public paths; the complete GoF participant collaboration
is not.
