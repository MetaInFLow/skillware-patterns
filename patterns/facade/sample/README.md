# Production Incident Response

This standalone Facade sample accepts `service` and `signal` through one root
Skill. It coordinates independently inspectable diagnosis, impact, and
communication Skills while returning only `summary`, `impact`, `actions`, and
`communication`.

From this directory, run the known-signal fixture:

```bash
python3 scripts/run_demo.py
```

Run another fixture:

```bash
python3 scripts/run_demo.py fixtures/invalid/unknown-signal.json
```

Run the focused tests:

```bash
python3 -m unittest discover tests -v
```

The demo requires Python 3.10 or newer, uses only the standard library, needs
no network or credentials, and imports no other pattern sample. A malformed
fixture exits nonzero with a validation error.
