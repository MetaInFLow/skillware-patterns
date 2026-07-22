# Software Release Notification

This standalone Observer sample publishes one typed software release event to
explicitly registered audit, changelog, and team-notification consumer Skills.

Run the default valid workflow from this directory:

```bash
python3 scripts/run_demo.py
```

Run the fixture that unregisters changelog before publication:

```bash
python3 scripts/run_demo.py fixtures/valid/release-after-unregistration.json
```

Run the focused tests:

```bash
python3 -m unittest discover tests -v
```

The demo requires Python 3.10 or newer, uses only the standard library, needs
no network or external accounts, and imports no shared pattern code. Three
deterministic update functions model separately inspectable child Skills;
Python does not load or interpret `SKILL.md`.

The Subject applies explicit registration operations, freezes insertion order
for delivery, gives each Observer an isolated event copy, records every attempt,
continues after failure, and rejects publication re-entry. Notification is not
transaction completion and this sample performs no implicit retry.
