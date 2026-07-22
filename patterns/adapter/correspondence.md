# Adapter correspondence

## Strong ecosystem correspondence

- **Status:** strong correspondence
- **Paper claim:** Strong correspondence. Parity requires runtime tests.
- **Case:** gstack Skill suite (`garrytan/gstack`)
- **Fixed upstream commit:** `11de390be1be6849eb9a15f91ff4922dd16c589a`
- **Canonical and generated surface:**
  [`scripts/gen-skill-docs.ts`](https://github.com/garrytan/gstack/blob/11de390be1be6849eb9a15f91ff4922dd16c589a/scripts/gen-skill-docs.ts)
- **Claude target configuration:**
  [`hosts/claude.ts`](https://github.com/garrytan/gstack/blob/11de390be1be6849eb9a15f91ff4922dd16c589a/hosts/claude.ts)
- **Codex target configuration:**
  [`hosts/codex.ts`](https://github.com/garrytan/gstack/blob/11de390be1be6849eb9a15f91ff4922dd16c589a/hosts/codex.ts)
- **Codex invocation evidence:**
  [`test/codex-e2e.test.ts`](https://github.com/garrytan/gstack/blob/11de390be1be6849eb9a15f91ff4922dd16c589a/test/codex-e2e.test.ts)
- **Vendored observation record:**
  [frozen evidence](evidence/gstack-frozen-case.md)

The canonical Skill semantics are the Adaptee. A generated or system-specific
binding is the Adapter because it translates discovery paths, frontmatter,
tool names, and other target conventions without making the canonical
procedure target-specific. The Host-specific Skill contract is the Target, and
task-level invocation is the Client. An Agent Host can carry and activate the
binding, while the Agent Runtime interprets it; neither platform role becomes
a GoF participant automatically.

The local evidence record preserves the fixed revision, exact paths,
counterevidence, and claim boundary needed to audit this correspondence without
access to a separate research repository. The source relation is strong, but
runtime parity still requires tests under each Target Host.

## Constructive sample

- **Status:** constructive
- **Unit:** [`sample/SKILL.md`](sample/SKILL.md) with three tracker bindings
- **Target contract:**
  [`sample/references/tracker-contracts.md`](sample/references/tracker-contracts.md)
- **Executable oracle:** [`sample/scripts/run_demo.py`](sample/scripts/run_demo.py)
- **Focused verification:** [`sample/tests/test_demo.py`](sample/tests/test_demo.py)

The local multi-tracker sample demonstrates that semantic translation can be
built and tested. It is not evidence about gstack, open-source frequency, or
comparative quality. Conversely, the gstack case does not validate the local
sample; each claim has its own artifacts and verification boundary.
