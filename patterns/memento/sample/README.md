# Configuration Migration

## Scenario

A service configuration must move from version `n` to `n+1` atomically. If the
write or post-write validation fails, the exact prior bytes must be restorable;
if preparation fails before a write attempt, newer external content must be
preserved.

## Why this is Memento

The Originator owns configuration state, the Memento stores an opaque exact
checkpoint, and the Caretaker controls when to capture, restore, or discard it.
The Caretaker cannot inspect or forge the captured configuration.

| GoF role | Skillware carrier in this example |
| --- | --- |
| Originator | `configuration-originator` child Skill |
| Memento | Opaque `configuration-memento-v1` checkpoint |
| Caretaker | Root Configuration Migration and `migration-caretaker` |

## Contract

Input: one bounded JSON configuration file. Output: migration status, old/new
version, endpoint, and `restored`. Capture is opaque and one-use; checksum,
owner, target, and lifecycle checks reject stale or foreign checkpoints.

## Where to look

- [Root Skill](SKILL.md) defines preparation, write-attempt, restore, and discard phases.
- [Memento contract](references/configuration-memento-contract.md) defines opacity and admission checks.
- `scripts/run_demo.py --fail` exercises the rollback path without modifying repository fixtures.

This standalone Memento sample increments a bounded JSON configuration version
through atomic replacement. The Originator captures exact prior bytes and
portable permissions in an opaque Memento. A preparation or conflict error
discards without restore, preserving newer external content. Once a write is
attempted, the Caretaker restores conservatively on failure and discards the
checkpoint without restore after success.

The Originator retains every immutable prepared payload privately and returns
only a sealed opaque one-use token. Commit and discard validate checkpoint
checksum, ownership, active lifecycle, and identity before retirement.
During rollback, those admission checks are inside the restoration-error
boundary. A failed admission preserves both errors and may leave the complete
migrated file in place because the checkpoint cannot safely be applied.

Run the deterministic default demo without modifying its fixture:

```bash
python3 scripts/run_demo.py
```

Run a supplied file in place or exercise the rollback path:

```bash
python3 scripts/run_demo.py path/to/service.json
python3 scripts/run_demo.py path/to/service.json --fail
```

Run focused tests:

```bash
python3 -m unittest discover tests -v
```

The sample requires Python 3.10 or later, uses only the standard library, needs
no network or account, and imports no shared pattern code. It assumes one
trusted cooperative writer. Atomic replacement prevents partial file content;
it does not provide locking or identical crash guarantees on every filesystem.
Mode is applied to the open temporary file before file fsync and rename; a
portable path-based fallback is used only where descriptor mode is unavailable.
