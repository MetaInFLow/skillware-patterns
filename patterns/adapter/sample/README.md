# Multi-Tracker Issue Publisher

This standalone Adapter sample accepts a canonical issue with `id`, `title`,
`description`, and `severity`, plus a target of `github`, `jira`, or `linear`.
Each thin binding returns the selected tracker's exact payload while preserving
canonical identity and meaning.

From this directory, run the default GitHub fixture:

```bash
python3 scripts/run_demo.py
```

Run another fixture:

```bash
python3 scripts/run_demo.py fixtures/valid/linear.json
```

Run the focused tests:

```bash
python3 -m unittest discover tests -v
```

The demo requires Python 3.10 or newer, uses only the standard library, needs
no network or credentials, and imports no other pattern sample. Unknown targets
and malformed canonical issues exit nonzero with clear validation errors.
Additional request or issue fields are rejected rather than ignored.
