# Configuration Migration

This standalone Memento sample increments a bounded JSON configuration version
through atomic replacement. The Originator captures exact prior bytes and
portable permissions in an opaque Memento. A preparation or conflict error
discards without restore, preserving newer external content. Once a write is
attempted, the Caretaker restores conservatively on failure and discards the
checkpoint without restore after success.

The Originator retains every immutable prepared payload privately and returns
only a sealed opaque one-use token. Commit and discard validate checkpoint
checksum, ownership, active lifecycle, and identity before retirement.

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
