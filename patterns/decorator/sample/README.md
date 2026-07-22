# Contract Review Enhancers

This standalone sample realizes Decorator with one exact
`contract-review-v1` Component interface. Base Contract Review is the
ConcreteComponent. Privacy Check and Citation Check are composable
ConcreteDecorators. Every participant accepts exactly `text` and returns
exactly `summary` and `findings`.

Run:

```bash
python3 scripts/run_demo.py
python3 scripts/run_demo.py fixtures/valid/clean-contract.json
python3 scripts/run_demo.py --decorators citation,privacy
python3 -m unittest discover tests -v
```

The default composition is
`with_citation_check(with_privacy_check(base_review))`. Delegation returns the
base result first; Privacy Check appends its finding; Citation Check appends
last. Reversing the wrapper order reverses only those enhancements. Each
boundary validates and copies input and output, so the caller, wrapped
Component, and wrapper cannot mutate one another's owned values.

The demo uses only the Python standard library and makes no network or model
calls. Fixtures pin exact success output and stable errors for malformed or
duplicate-member JSON, schema, types, bounds, invalid UTF-8, and lone Unicode
surrogates. Python is a deterministic oracle, not a legal, privacy, or citation
review system and not evidence of Agent Runtime interpretation.
