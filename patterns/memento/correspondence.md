# Memento correspondence

## Public open-source candidate

- **Project:** Microsoft SkillOpt
- **Revision:** `b860a5cf88ce75e2bd02ca981ac21fb28cffba83`
- **Exact path:** `skillopt_sleep/staging.py`
- **Status:** candidate correspondence
- **Frozen record:** [frozen evidence](evidence/skillopt-frozen-case.md)

At the pinned path, `adopt` reads a staging manifest, creates a `backup`
directory, calls `_backup` on an existing live file, and then copies a staged
proposal over that live path. This supports a narrow capture-before-change
observation.

The same inspected file does not define an operation that gives the backup
back to the live-file owner, verifies byte-exact recovery, controls checkpoint
lifecycle, rejects stale/cross-target snapshots, or handles restore failure.
Therefore the public source does not confirm the canonical
Originator/Memento/Caretaker collaboration. The claim remains candidate-only.

## Constructive sample

- **Status:** constructive
- **Originator:**
  [`sample/child-skills/configuration-originator/SKILL.md`](sample/child-skills/configuration-originator/SKILL.md)
- **Memento contract:**
  [`sample/references/configuration-memento-contract.md`](sample/references/configuration-memento-contract.md)
- **Caretaker:** [`sample/SKILL.md`](sample/SKILL.md)
- **Executable oracle:**
  [`sample/scripts/run_demo.py`](sample/scripts/run_demo.py)
- **Focused verification:**
  [`sample/tests/test_demo.py`](sample/tests/test_demo.py)

The constructive sample provides the missing owned restore path and verifies
exact bytes, metadata, integrity, lifecycle, atomic replacement, successful
disposal without restore, and restore-failure reporting. This local evidence
does not establish public upstream or Agent Runtime behavior.
