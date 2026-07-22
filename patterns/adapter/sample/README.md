# Multi-Tracker Issue Publisher

This standalone Adapter sample accepts a canonical issue, a target of
`github`, `jira`, or `linear`, and exact target location context. Each thin
binding builds a documented REST or GraphQL request descriptor while preserving
canonical identity and severity.

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

The output is an offline descriptor. The demo never sends it and does not claim
that GitHub, Jira, or Linear accepted it. See
`references/tracker-contracts.md` for the official vendor documentation.
