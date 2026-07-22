# Observer correspondence

## Candidate ecosystem correspondence

- **Status:** candidate correspondence
- **Paper wording:** Candidate pending complete registration and delivery evidence.
- **Case:** Everything Claude Code (`affaan-m/ECC`)
- **Fixed upstream commit:** `2bc924faf2f8e893bfe0af86b1931283693c30ae`
- **Hook manifest:**
  [`hooks/hooks.json`](https://github.com/affaan-m/ECC/blob/2bc924faf2f8e893bfe0af86b1931283693c30ae/hooks/hooks.json)
- **Profile-aware hook runner:**
  [`scripts/hooks/run-with-flags.js`](https://github.com/affaan-m/ECC/blob/2bc924faf2f8e893bfe0af86b1931283693c30ae/scripts/hooks/run-with-flags.js)
- **Hook tests:**
  [`tests/hooks/hooks.test.js`](https://github.com/affaan-m/ECC/blob/2bc924faf2f8e893bfe0af86b1931283693c30ae/tests/hooks/hooks.test.js)
- **Continuous-learning Skill:**
  [`skills/continuous-learning-v2/SKILL.md`](https://github.com/affaan-m/ECC/blob/2bc924faf2f8e893bfe0af86b1931283693c30ae/skills/continuous-learning-v2/SKILL.md)
- **Observation hook:**
  [`skills/continuous-learning-v2/hooks/observe.sh`](https://github.com/affaan-m/ECC/blob/2bc924faf2f8e893bfe0af86b1931283693c30ae/skills/continuous-learning-v2/hooks/observe.sh)
- **Observer configuration:**
  [`skills/continuous-learning-v2/config.json`](https://github.com/affaan-m/ECC/blob/2bc924faf2f8e893bfe0af86b1931283693c30ae/skills/continuous-learning-v2/config.json)
- **Vendored observation record:**
  [frozen evidence](evidence/ecc-frozen-case.md)

At this revision, the hook manifest associates lifecycle/tool events and
matchers with separately named commands. The continuous-learning Skill states
that hooks capture session activity, while `observe.sh` consumes hook JSON and
contains explicit self-observation guards. These are source-level observations
of event-triggered independent behavior and motivate an Observer investigation.

The correspondence is not confirmed. The Agent Host lifecycle surface is
execution context, not automatically a GoF Subject, and the reviewed paths do
not establish one common Observer update contract, observer-level register and
unregister operations, deterministic multi-observer delivery, per-observer
failure accounting, or a complete re-entry policy. Static hook configuration
must not be upgraded to full GoF registration by analogy.

## Constructive sample

- **Status:** constructive
- **Root ConcreteSubject:** [`sample/SKILL.md`](sample/SKILL.md)
- **Observer contract:**
  [`sample/references/release-event-contract.md`](sample/references/release-event-contract.md)
- **Registered ConcreteObservers:**
  [`sample/child-skills/`](sample/child-skills/)
- **Subscription fixture:**
  [`sample/fixtures/valid/release.json`](sample/fixtures/valid/release.json)
- **Executable oracle:** [`sample/scripts/run_demo.py`](sample/scripts/run_demo.py)
- **Focused verification:** [`sample/tests/test_demo.py`](sample/tests/test_demo.py)

The root applies explicit registration and unregistration operations, creates
one `release.published.v1` event, and delivers isolated copies in registration
order. Every attempted Observer receives a separate delivered/failed record;
exceptions are isolated and a nested publish attempt fails only that Observer.

The local sample is not ECC evidence, and ECC does not validate the sample.
Neither claim supports prevalence, comparative benefit, production durability,
or cross-Host behavioral equivalence.
