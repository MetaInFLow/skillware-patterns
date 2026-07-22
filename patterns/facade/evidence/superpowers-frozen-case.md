# Superpowers frozen Facade evidence

## Evidence identity

- **Claim status:** confirmed correspondence
- **Target repository:** [`obra/superpowers`](https://github.com/obra/superpowers)
- **Frozen commit:** `896224c4b1879920ab573417e68fd51d2ccc9072`
- **Evaluation unit:** the Superpowers Skill suite at that commit
- **Method:** bounded source inspection of the public upstream artifacts below

This record vendors the observations needed to audit the Facade claim. It does
not vendor the upstream Skills or treat this repository's constructive sample
as evidence about Superpowers.

## Public upstream evidence

- Facade policy:
  [`skills/using-superpowers/SKILL.md`](https://github.com/obra/superpowers/blob/896224c4b1879920ab573417e68fd51d2ccc9072/skills/using-superpowers/SKILL.md)
- SessionStart bootstrap implementation:
  [`hooks/session-start`](https://github.com/obra/superpowers/blob/896224c4b1879920ab573417e68fd51d2ccc9072/hooks/session-start)
- SessionStart hook registration:
  [`hooks/hooks.json`](https://github.com/obra/superpowers/blob/896224c4b1879920ab573417e68fd51d2ccc9072/hooks/hooks.json)
- Specialist Skills at the same revision:
  [`skills/`](https://github.com/obra/superpowers/tree/896224c4b1879920ab573417e68fd51d2ccc9072/skills)

No third-party code is reproduced here. The links identify the exact public
source used for the observations.

## Participant mapping observations

- **Client:** task-level agent execution is directed to evaluate applicable
  Skills before continuing with the task.
- **Facade:** `skills/using-superpowers/SKILL.md` supplies one relevance and
  activation policy through which the Client approaches the suite.
- **Subsystem:** the named workflow Skills remain independently addressable
  specialists behind that common policy.

The SessionStart artifacts bootstrap the policy into a session. That Host
integration is execution context for the participant collaboration; Agent Host
and Agent Runtime are not reclassified as GoF Facade participants.

## Counterevidence and limits

- This is source inspection at one fixed commit, not a runtime comparison.
- Relevance judgment and specialist activation still depend on Host loading
  and model behavior.
- The evidence does not establish equal reliability or behavioral equivalence
  across Hosts.
- Specialist Skills remain directly addressable; Facade does not require the
  subsystem to become inaccessible.
- One confirmed correspondence does not establish ecosystem frequency,
  comparative quality, or automatic benefit from using the pattern.

## Claim boundary

The exact revision and paths support a **confirmed correspondence** for the
Facade participant relation described above. They do not validate this
repository's incident-response sample, and the sample does not strengthen the
ecosystem claim.
