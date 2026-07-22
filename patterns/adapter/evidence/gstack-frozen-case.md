# gstack frozen Adapter evidence

## Evidence identity

- **Claim status:** confirmed correspondence
- **Paper wording:** Strong correspondence. Parity requires runtime tests.
- **Target repository:** [`garrytan/gstack`](https://github.com/garrytan/gstack)
- **Frozen commit:** `11de390be1be6849eb9a15f91ff4922dd16c589a`
- **Evaluation unit:** the gstack Skill suite, generated Host bindings, and
  Host configuration at that commit
- **Method:** bounded source inspection of the public upstream artifacts below

This record vendors the observations needed to audit the Adapter claim. It does
not vendor upstream code or treat this repository's constructive sample as
evidence about gstack.

## Public upstream evidence

- Canonical Adaptee template:
  [`SKILL.md.tmpl`](https://github.com/garrytan/gstack/blob/11de390be1be6849eb9a15f91ff4922dd16c589a/SKILL.md.tmpl)
- Generated `SKILL.md` surface:
  [`SKILL.md`](https://github.com/garrytan/gstack/blob/11de390be1be6849eb9a15f91ff4922dd16c589a/SKILL.md)
- Host-specific generation:
  [`scripts/gen-skill-docs.ts`](https://github.com/garrytan/gstack/blob/11de390be1be6849eb9a15f91ff4922dd16c589a/scripts/gen-skill-docs.ts)
- Claude target configuration:
  [`hosts/claude.ts`](https://github.com/garrytan/gstack/blob/11de390be1be6849eb9a15f91ff4922dd16c589a/hosts/claude.ts)
- Codex target configuration:
  [`hosts/codex.ts`](https://github.com/garrytan/gstack/blob/11de390be1be6849eb9a15f91ff4922dd16c589a/hosts/codex.ts)
- Host registry and system-specific surfaces:
  [`hosts/index.ts`](https://github.com/garrytan/gstack/blob/11de390be1be6849eb9a15f91ff4922dd16c589a/hosts/index.ts)
- Setup and installation paths:
  [`setup`](https://github.com/garrytan/gstack/blob/11de390be1be6849eb9a15f91ff4922dd16c589a/setup)
- Codex discovery and invocation test:
  [`test/codex-e2e.test.ts`](https://github.com/garrytan/gstack/blob/11de390be1be6849eb9a15f91ff4922dd16c589a/test/codex-e2e.test.ts)

No third-party code is reproduced here. The links identify the exact public
source used for the observations.

## Participant mapping observations

- **Client:** task-level invocation asks a target Host to discover and use a
  generated `SKILL.md` surface.
- **Target:** each Host-specific Skill discovery and activation contract,
  including its frontmatter, path, and tool-name conventions.
- **Adaptee:** `SKILL.md.tmpl`, the canonical Adaptee template from which
  target surfaces are generated.
- **Adapter:** the generator plus a selected system-specific binding that
  translates canonical sources into the Target conventions.

The Host configurations and generator make compatibility an explicit boundary
instead of maintaining unrelated copies of each procedure. An Agent Host can
carry and activate the resulting Adapter and an Agent Runtime can interpret
the loaded source, but Host and Runtime remain execution context rather than
automatic GoF participants.

## Counterevidence and limits

- This is source inspection at one fixed commit, not a cross-Host runtime
  comparison.
- The reviewed generator performs path, frontmatter, and tool-name rewrites;
  source inspection alone cannot establish equal behavior after interpretation.
- The host registry names more systems than the directly evidenced installation
  and invocation paths. The claim does not extend equal support to every name.
- Some Host integrations use methodology-oriented artifacts rather than the
  same direct generated-Skill installation path.
- One confirmed correspondence does not establish ecosystem frequency,
  comparative quality, or an automatic benefit from using Adapter.

## Runtime-parity limitation

The exact revision and paths support a **confirmed correspondence** for explicit
canonical-to-Target translation. They do not prove that every generated
binding installs successfully, exposes the same capabilities, or produces
behaviorally equivalent Agent Runtime execution across Hosts. Runtime parity
requires target-specific discovery, activation, invocation, result, and error
tests under each supported Host.

## Claim boundary

This evidence supports the Adapter participant relation described above at the
frozen revision. It does not validate this repository's multi-tracker sample,
and the sample does not strengthen the ecosystem claim.
