# Template Method correspondence

## Candidate ecosystem correspondence

- **Status:** candidate correspondence
- **Paper wording:** Superpowers workflows are an invariant-skeleton candidate;
  bounded specialization and runtime behavior remain unverified.
- **Case:** Superpowers (`obra/superpowers`)
- **Fixed upstream commit:** `896224c4b1879920ab573417e68fd51d2ccc9072`
- **Ordered brainstorming workflow:**
  [`skills/brainstorming/SKILL.md`](https://github.com/obra/superpowers/blob/896224c4b1879920ab573417e68fd51d2ccc9072/skills/brainstorming/SKILL.md)
- **Ordered TDD workflow:**
  [`skills/test-driven-development/SKILL.md`](https://github.com/obra/superpowers/blob/896224c4b1879920ab573417e68fd51d2ccc9072/skills/test-driven-development/SKILL.md)
- **Vendored assessment:**
  [frozen evidence](evidence/superpowers-frozen-case.md)

At this revision, the brainstorming Skill requires its checklist in order and
fixes approval and transition gates, while the TDD Skill fixes Red, verified
Red, Green, verified Green, and Refactor sequencing. These exact sources
support workflow-owned invariant skeletons.

Neither source defines multiple ConcreteClasses behind one bounded primitive
operation contract. Bounded domain-hook substitution, protection against
specialization reorder, Agent Host activation, and Agent Runtime behavior are
unverified. The correspondence is therefore candidate, not confirmed.

## Constructive sample

- **Status:** constructive
- **AbstractClass:** [`sample/SKILL.md`](sample/SKILL.md)
- **Hook contract:**
  [`sample/references/rfp-domain-hook-contract.md`](sample/references/rfp-domain-hook-contract.md)
- **ConcreteClasses:** [`sample/child-skills/`](sample/child-skills/)
- **Healthcare fixture:**
  [`sample/fixtures/valid/healthcare-rfp.json`](sample/fixtures/valid/healthcare-rfp.json)
- **Executable oracle:** [`sample/scripts/run_demo.py`](sample/scripts/run_demo.py)
- **Focused verification:** [`sample/tests/test_demo.py`](sample/tests/test_demo.py)

The root owns all five stages and allows only `apply-domain-hook` to vary.
Healthcare and Finance supply static callables under the exact same hook
contract. Focused tests prove explicit AbstractClass dispatch, exact order,
once-only invocation, inherited mixin `run` irrelevance, direct override
admission, stop-on-failure behavior, ordinary hook-argument copy mutation and
unknown stage-claim rejection, input and result validation, deterministic
output, and copied boundaries. This local construction
does not establish upstream or model behavior.
