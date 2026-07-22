# Caveman frozen Decorator candidate evidence

## Evidence identity

- **Claim status:** candidate correspondence
- **Paper wording:** The activation hook is wrapper-like motivation; complete
  Component contract equivalence and runtime behavior require further study.
- **Target repository:** `JuliusBrussee/caveman`
- **Frozen commit:** `25d22f864ad68cc447a4cb93aefde918aa4aec9f`
- **Evaluation unit:** one session-activation hook and the canonical Caveman
  Skill Artifact at the fixed revision
- **Method:** bounded static inspection of the two exact public artifacts below

This record preserves a narrow audit of activation wrapping. It does not copy
upstream code, infer Agent Runtime behavior, or treat the words hook and
wrapper as sufficient proof of Decorator.

## Fixed source paths

1. [`src/hooks/caveman-activate.js`](https://github.com/JuliusBrussee/caveman/blob/25d22f864ad68cc447a4cb93aefde918aa4aec9f/src/hooks/caveman-activate.js)
2. [`skills/caveman/SKILL.md`](https://github.com/JuliusBrussee/caveman/blob/25d22f864ad68cc447a4cb93aefde918aa4aec9f/skills/caveman/SKILL.md)

Both paths use a 40-character commit rather than a moving branch.

## Observed wrapper-like behavior

The hook identifies itself as a Claude Code `SessionStart` activation hook. At
session start it obtains the configured mode, writes an activation flag, reads
the canonical Caveman Skill Artifact when available, filters mode-specific
instructions, and emits activated instructions through standard output. It can
also add a status-line setup nudge. In off mode it removes the flag, emits
`OK`, and exits. The Skill Artifact contains the persistent compression,
intensity, language-preservation, clarity, and boundary instructions consumed
by that activation path.

This supports a bounded observation: the hook wraps session activation with
additional behavior while preserving the Host interaction surface used by the
hook, namely process execution and standard-output context. The added flag,
instruction injection, and optional nudge are responsibilities around the
session-start interaction rather than a replacement Host protocol.

## Missing or contradictory evidence

- The two paths do not declare a GoF Component request/result contract that
  both wrapped and unwrapped session activation implement.
- Static inspection does not show a substitutability test for a base Component,
  one hook wrapper, and arbitrary nested hook wrappers.
- The hook filters and emits Skill content, but the inspected paths do not
  establish whether the Agent Runtime interprets the emitted instructions or
  preserves behavior across every Host and mode.
- Flag writes and status-line advice are observable side responsibilities, yet
  exact failure equivalence with an unwrapped session-start Component is not
  specified.

The evidence therefore does not establish complete GoF Component/Decorator contract equivalence,
and runtime behavior remains unverified. It cannot support a confirmed
correspondence claim.

## Claim boundary

The proper status is **candidate correspondence**. The pinned paths motivate
activation wrappers as a possible Skillware Decorator carrier and support only
the narrow Host-surface observation above. The local Contract Review Enhancers
sample independently constructs and tests the missing Component interface,
delegation, idempotency, ordering, and substitution properties; it cannot
upgrade the upstream case or prove comparative benefit.
