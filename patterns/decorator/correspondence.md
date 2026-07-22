# Decorator correspondence

## Candidate ecosystem correspondence

- **Status:** candidate correspondence
- **Paper wording:** The activation hook is wrapper-like motivation; complete
  Component contract equivalence and runtime behavior require further study.
- **Case:** Caveman (`JuliusBrussee/caveman`)
- **Fixed upstream commit:** `25d22f864ad68cc447a4cb93aefde918aa4aec9f`
- **Activation hook:**
  [`src/hooks/caveman-activate.js`](https://github.com/JuliusBrussee/caveman/blob/25d22f864ad68cc447a4cb93aefde918aa4aec9f/src/hooks/caveman-activate.js)
- **Skill Artifact:**
  [`skills/caveman/SKILL.md`](https://github.com/JuliusBrussee/caveman/blob/25d22f864ad68cc447a4cb93aefde918aa4aec9f/skills/caveman/SKILL.md)
- **Vendored assessment:**
  [frozen evidence](evidence/caveman-frozen-case.md)

The pinned activation hook runs at session start, reads the Caveman Skill
Artifact, and adds flag maintenance, filtered instruction injection, and an
optional status-line nudge while continuing to communicate through the hook's
process/stdout Host surface. That supports a narrow wrapper-like candidate.

The two reviewed paths do not declare or test one GoF Component request/result
contract for wrapped and unwrapped activation, arbitrary wrapper composition,
or identical failure semantics. Static inspection also cannot prove Agent
Runtime interpretation or cross-Host behavior. The correspondence therefore
remains candidate rather than confirmed.

## Constructive sample

- **Status:** constructive
- **Root composition:** [`sample/SKILL.md`](sample/SKILL.md)
- **Component contract:**
  [`sample/references/contract-review-component.md`](sample/references/contract-review-component.md)
- **ConcreteComponent:**
  [`sample/child-skills/base-contract-review/SKILL.md`](sample/child-skills/base-contract-review/SKILL.md)
- **ConcreteDecorators:** [`sample/child-skills/`](sample/child-skills/)
- **Enhanced fixture:**
  [`sample/fixtures/valid/enhanced-contract.json`](sample/fixtures/valid/enhanced-contract.json)
- **Executable oracle:** [`sample/scripts/run_demo.py`](sample/scripts/run_demo.py)
- **Focused verification:** [`sample/tests/test_demo.py`](sample/tests/test_demo.py)

The tests show that all three wrappers accept and return the Component contract,
delegate once, preserve the wrapped result, append in nesting order, propagate
failure unchanged, suppress identical findings idempotently, and isolate
mutable inputs and results. They also load the manifest composition, exercise
more than 100 findings and wrappers, swap wrapper order, and inject a
replacement Component. This construction is independent of the upstream case
and does not establish model interpretation or production review quality.
