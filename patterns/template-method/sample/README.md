# Enterprise RFP Response

This standalone sample constructs Template Method with an invariant
five-operation RFP skeleton and two bounded domain ConcreteClasses.

Run from this directory with Python 3.10 or newer:

```bash
python3 scripts/run_demo.py
python3 scripts/run_demo.py fixtures/valid/finance-rfp.json
python3 -m unittest discover tests -v
```

The default result is byte-for-byte equal to
`expected/healthcare-rfp-result.json`. Invalid fixtures produce the matching
stable error files with exit status 2. The demo uses only the Python standard
library and performs no network or cross-pattern imports.

The tests prove the literal `run_rfp("healthcare")` API, fixed order, exactly
one hook invocation, failure stop, shared hook contract, bounded substitution,
explicit AbstractClass dispatch, inherited mixin `run` irrelevance, direct
override admission, static hook signature validation, ordinary hook-argument
copy mutation, unknown stage-claim rejection, deterministic outputs,
duplicate-member rejection,
Unicode handling, and depth/type bounds. Focused tests and the oracle use only
the Python standard library.

Hooks are cooperative, trusted extension code. The sample does not claim
sandboxing or protection from closures, module globals, monkeypatching,
introspection, or other arbitrary in-process Python behavior.

Domain findings are illustrative, not professional RFP or compliance advice.
