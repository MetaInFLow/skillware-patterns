# ECC frozen Observer candidate evidence

## Evidence identity

- **Claim status:** candidate correspondence
- **Paper wording:** Candidate pending complete registration and delivery evidence.
- **Target repository:** `affaan-m/ECC`
- **Frozen commit:** `2bc924faf2f8e893bfe0af86b1931283693c30ae`
- **Evaluation unit:** the public hook manifest and runner together with the
  continuous-learning-v2 Skill, observation hook, configuration, and hook tests
- **Method:** bounded source inspection of the exact public artifacts below

This local record vendors concise observations and limitations. It does not
copy upstream code or use the constructive release sample as ECC evidence.

## Public upstream evidence

- Hook event-to-command configuration:
  [`hooks/hooks.json`](https://github.com/affaan-m/ECC/blob/2bc924faf2f8e893bfe0af86b1931283693c30ae/hooks/hooks.json)
- Profile-aware command dispatch:
  [`scripts/hooks/run-with-flags.js`](https://github.com/affaan-m/ECC/blob/2bc924faf2f8e893bfe0af86b1931283693c30ae/scripts/hooks/run-with-flags.js)
- Hook behavior tests:
  [`tests/hooks/hooks.test.js`](https://github.com/affaan-m/ECC/blob/2bc924faf2f8e893bfe0af86b1931283693c30ae/tests/hooks/hooks.test.js)
- Continuous-learning behavioral source:
  [`skills/continuous-learning-v2/SKILL.md`](https://github.com/affaan-m/ECC/blob/2bc924faf2f8e893bfe0af86b1931283693c30ae/skills/continuous-learning-v2/SKILL.md)
- Continuous-learning observation hook:
  [`skills/continuous-learning-v2/hooks/observe.sh`](https://github.com/affaan-m/ECC/blob/2bc924faf2f8e893bfe0af86b1931283693c30ae/skills/continuous-learning-v2/hooks/observe.sh)
- Background observer configuration:
  [`skills/continuous-learning-v2/config.json`](https://github.com/affaan-m/ECC/blob/2bc924faf2f8e893bfe0af86b1931283693c30ae/skills/continuous-learning-v2/config.json)

At this commit, `hooks/hooks.json` declares multiple lifecycle and tool event
groups, matchers, stable handler IDs, and command targets. It includes an
asynchronous continuous-learning observation command for matching tool use.
The continuous-learning Skill describes hook-driven session observation;
`observe.sh` consumes hook JSON and rejects several automated or observer-owned
sessions to avoid self-observation. The configuration independently controls a
background observer process. The tests exercise hook scripts and their
integration assumptions.

## Candidate participant observations

- Host lifecycle/tool events plus manifest associations are Subject-like in
  that named state changes select independent handler commands.
- Hook commands and the continuous-learning observation support are
  Observer-like consumers of event data.
- The continuous-learning Skill is a separately inspectable Behavioral Source
  associated with one of those event-driven behaviors.

These observations justify investigation but do not establish the full
canonical participant collaboration.

## Missing or partial evidence

- The event source belongs to the Agent Host integration surface. Agent Host
  remains execution context and cannot be relabeled as a GoF Subject without a
  complete participant-level mapping.
- The reviewed handlers do not expose one common Observer update contract.
- Static manifest entries and profile flags do not establish explicit,
  observer-level registration and unregistration operations.
- Manifest array position alone does not prove a documented and tested
  deterministic delivery order across all matching handlers.
- The paths do not establish per-observer delivered/failed accounting, failure
  isolation across every matching handler, or one complete re-entry policy.

Therefore **GoF registration, unregistration, and deterministic delivery** are
not fully evidenced. The claim remains **candidate correspondence**, not a
confirmed ECC implementation of Observer.

## Claim boundary

The pinned artifacts support only a candidate correspondence for configured
event-triggered behavior associated with a Skillware Unit. They do not establish
the complete GoF Observer relation, validate this repository's constructive
sample, prove ecosystem frequency, or establish runtime equivalence across
Agent Hosts and Agent Runtimes.
