# SkillOpt frozen Memento candidate

**Project:** Microsoft SkillOpt

**Pinned revision:** `b860a5cf88ce75e2bd02ca981ac21fb28cffba83`

**Claim status:** candidate correspondence

## Inspected source

- [`skillopt_sleep/staging.py`](https://github.com/microsoft/SkillOpt/blob/b860a5cf88ce75e2bd02ca981ac21fb28cffba83/skillopt_sleep/staging.py)

This is the only upstream path used for the Memento correspondence claim. The
revision is a full immutable commit id rather than a moving branch.

## Observed relation

The module describes staging and adoption. Its `_backup` helper copies an
existing live file into a staging-local `backup` directory. Its `adopt`
function calls that helper before copying a proposed Skill or memory file over
the live path. Thus the inspected candidate **backs up before adoption** and
separates the saved prior file from the subsequent copy operation.

## Counterevidence and limits

The file returns updated live paths, but it exposes **no owned restore path**
that applies a saved file back through the state owner. It does not show an
opaque Memento interface, exact-byte or checksum validation, snapshot-to-target
binding, stale snapshot rejection, checkpoint disposal, restoration failure
handling, or a verified recovery test. Consequently, the canonical Caretaker
restore collaboration and full Memento is unverified. Backup-before-write is
candidate evidence only; it is not promoted to confirmed correspondence.

Source inspection also cannot establish Agent Host activation or Agent Runtime
interpretation. No runtime trace or task outcome is inferred from this file.
