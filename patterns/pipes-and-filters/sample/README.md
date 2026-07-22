# Support Ticket Triage

This standalone sample runs one ticket through normalize, redact, classify,
prioritize, and draft Filters. Every stage accepts and returns
`support-ticket.v1` through a validating, deep-copying Pipe.

```bash
python3 scripts/run_demo.py
python3 -m unittest discover tests -v
```

The default input is `fixtures/valid/urgent-access.json`; exact output and
error fixtures are under `expected/`.
