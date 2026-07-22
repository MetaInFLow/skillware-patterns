# Strategy correspondence

## Candidate ecosystem correspondence

- **Status:** candidate correspondence
- **Paper wording:** Open-source correspondence is motivation only;
  comparative benefit requires runtime study.
- **Case:** UI/UX Pro Max (`nextlevelbuilder/ui-ux-pro-max-skill`)
- **Fixed upstream commit:** `8a81ed60272d21d4b8808f7308d49a0b1b000555`
- **Skill source:**
  [`.claude/skills/ui-ux-pro-max/SKILL.md`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/8a81ed60272d21d4b8808f7308d49a0b1b000555/.claude/skills/ui-ux-pro-max/SKILL.md)
- **CLI router:**
  [`.claude/skills/ui-ux-pro-max/scripts/search.py`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/8a81ed60272d21d4b8808f7308d49a0b1b000555/.claude/skills/ui-ux-pro-max/scripts/search.py)
- **Search procedures:**
  [`.claude/skills/ui-ux-pro-max/scripts/core.py`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/8a81ed60272d21d4b8808f7308d49a0b1b000555/.claude/skills/ui-ux-pro-max/scripts/core.py)
- **Design-system procedure:**
  [`.claude/skills/ui-ux-pro-max/scripts/design_system.py`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/8a81ed60272d21d4b8808f7308d49a0b1b000555/.claude/skills/ui-ux-pro-max/scripts/design_system.py)
- **Vendored assessment:**
  [frozen evidence](evidence/ui-ux-pro-max-frozen-case.md)

The pinned router chooses domain search, stack search, or full design-system
generation. That is relevant routing evidence. The procedures do not expose a
declared common request/result interface: design-system generation returns
rendered text, while the search paths return differing mappings. The reviewed
paths also provide no substitution/conformance test across alternatives.

The correspondence therefore remains candidate. Multiple procedures and a
branch are not enough to establish Strategy when exact interchangeability and
the complete Context, Strategy, and ConcreteStrategy relation remain
unverified. Static inspection also cannot prove Agent Runtime behavior or
comparative benefit.

## Constructive sample

- **Status:** constructive
- **Context:** [`sample/SKILL.md`](sample/SKILL.md)
- **Strategy contract:**
  [`sample/references/review-strategy-contract.md`](sample/references/review-strategy-contract.md)
- **ConcreteStrategies:** [`sample/child-skills/`](sample/child-skills/)
- **Low-risk fixture:**
  [`sample/fixtures/valid/low-risk-review.json`](sample/fixtures/valid/low-risk-review.json)
- **Security-sensitive fixture:**
  [`sample/fixtures/valid/security-sensitive-review.json`](sample/fixtures/valid/security-sensitive-review.json)
- **Executable oracle:** [`sample/scripts/run_demo.py`](sample/scripts/run_demo.py)
- **Focused verification:** [`sample/tests/test_demo.py`](sample/tests/test_demo.py)

The Context selects or directly addresses one injected ConcreteStrategy, then
validates the same result contract. Tests isolate selection from delegation and
show that Fast Scan and Deep Review can be substituted without changing the
Context or output fields. This construction is independent of the upstream case
and does not establish model interpretation or production review quality.
