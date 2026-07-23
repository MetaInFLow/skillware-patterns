# Risk-Aware Code Review

## Scenario

A changed-file review should be fast for ordinary low-risk work and deeper for
security-sensitive or larger changes. Callers still need one review request and
one result shape.

## Why this is Strategy

The Context selects exactly one procedure, Fast Scan or Deep Review, using a
policy. Both ConcreteStrategy Skills accept the same rich contract and return
the same result contract; the procedure can change without changing the
caller-facing Skill.

| GoF role | Skillware carrier in this example |
| --- | --- |
| Context | `risk-aware-code-review` root Skill |
| Strategy | `risk-aware-code-review-v1` in `references/review-strategy-contract.md` |
| ConcreteStrategy | `fast-scan` and `deep-review` child Skills |

## Contract

Input: review id, changed files, and `security_sensitive`. Output: schema,
selected strategy, reviewed files, findings, and summary. Selection is Deep
Review for security-sensitive or four-plus-file requests, otherwise Fast Scan.

## Where to look

- [Root Skill](SKILL.md) defines selection and shared validation.
- [Strategy contract](references/review-strategy-contract.md) defines substitutability.
- `scripts/run_demo.py` supports injected strategies and direct strategy addressing.

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
is checked against the same exact rich contract. Mapping key order is irrelevant;
output fields and findings are canonicalized. Fixtures pin successful output
and stable failures for malformed or duplicate-member JSON, schema, types,
bounds, unsafe paths, lone surrogates, and unknown strategy identifiers.

The module-level `review({"files": int, "security_sensitive": bool})` preserves
the compact plan API separately. It chooses Deep Review for security sensitivity
or `files > 5` and returns exactly `strategy`, `findings`, and `confidence`.
It delegates to exactly one compact `fast_scan` or `deep_review` callable, both
of which can be replaced by spies without calling the unselected alternative.
Injected rich strategies may use custom procedures; the Context enforces the
shared structure, deterministic finding order, and unique identities rather
than the built-in lexical rule sets.

Python is a deterministic oracle for the participant collaboration. It does
not activate or interpret the natural-language Skills, and its small lexical
rule set is not a production security review system.
