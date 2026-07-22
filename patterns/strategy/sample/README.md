# Risk-Aware Code Review

This standalone sample realizes Strategy with a code-review Context, one exact
request/result Strategy contract, and two interchangeable ConcreteStrategies.
Fast Scan applies high-signal rules; Deep Review adds contextual rules. The
Context selects Deep Review for security-sensitive requests or at least four
files and Fast Scan otherwise.

Run:

```bash
python3 scripts/run_demo.py
python3 scripts/run_demo.py fixtures/valid/security-sensitive-review.json
python3 scripts/run_demo.py fixtures/valid/low-risk-review.json --strategy deep-review
python3 -m unittest discover tests -v
```

The demo uses only the Python standard library and performs no network or model
calls. Both strategies can be injected or addressed directly, and every result
is checked against the same exact contract. Fixtures pin successful output and
stable failures for malformed JSON, schema, types, bounds, unsafe paths, and
unknown strategy identifiers.

Python is a deterministic oracle for the participant collaboration. It does
not activate or interpret the natural-language Skills, and its small lexical
rule set is not a production security review system.
