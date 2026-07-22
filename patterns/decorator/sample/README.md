# Contract Review Enhancers

This standalone sample realizes Decorator with one exact
`contract-review-v1` Component interface. Base Contract Review is the
ConcreteComponent. Privacy Check and Citation Check are composable
ConcreteDecorators. Optional Compliance Check is a third ConcreteDecorator.
Every participant accepts exactly `text` and returns exactly `summary` and
`findings`.

Run:

```bash
python3 scripts/run_demo.py
python3 scripts/run_demo.py fixtures/valid/clean-contract.json
python3 scripts/run_demo.py --decorators citation-check,privacy-check
python3 scripts/run_demo.py --decorators privacy-check,citation-check,compliance-check
python3 -m unittest discover tests -v
```

The default composition is
`with_citation_check(with_privacy_check(base_review))`. Delegation returns the
base result first; Privacy Check appends its finding; Citation Check appends
last. Reversing the wrapper order reverses only those enhancements. Each
boundary validates and copies input and output, so the caller, wrapped
Component, and wrapper cannot mutate one another's owned values. Exact
`(type, message)` identity makes repeated identical wrappers idempotent. The
contract bounds individual strings and nesting depth but does not cap the
finding array, preserving substitution under additional wrapper composition.

The demo uses only the Python standard library and makes no network or model
calls. JSON fixtures pin exact success output and stable errors for malformed
JSON, duplicate members, exact fields and types, blank text, lone Unicode
surrogates, and excessive depth. Focused programmatic tests cover invalid
UTF-8, non-string mapping keys, cyclic values, parser recursion, per-string
bounds, more than 100 findings and wrappers, duplicate finding identity and
idempotency, and alias isolation. Python is a deterministic oracle, not a
legal, privacy, citation, or compliance review system and not evidence of Agent
Runtime interpretation.
