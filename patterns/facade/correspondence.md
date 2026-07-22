# Facade correspondence

## Confirmed ecosystem correspondence

- **Status:** confirmed correspondence
- **Case:** Superpowers Skill suite (`obra/superpowers`)
- **Fixed upstream commit:** `896224c4b1879920ab573417e68fd51d2ccc9072`
- **Exact Facade path:**
  [`skills/using-superpowers/SKILL.md`](https://github.com/obra/superpowers/blob/896224c4b1879920ab573417e68fd51d2ccc9072/skills/using-superpowers/SKILL.md)
- **Bootstrap evidence:**
  [`hooks/session-start`](https://github.com/obra/superpowers/blob/896224c4b1879920ab573417e68fd51d2ccc9072/hooks/session-start)
- **Frozen research case:**
  [`research/cases/superpowers.md`](https://github.com/MetaInFLow/skillware/blob/1fc1dfd/research/cases/superpowers.md)
- **Frozen pattern analysis:**
  [`research/patterns/facade.md`](https://github.com/MetaInFLow/skillware/blob/1fc1dfd/research/patterns/facade.md)

Task-level agent execution is the Client. The `using-superpowers` Skill is the
Facade because it supplies one relevance and activation policy over the named
specialist workflow Skills, which form the subsystem. The SessionStart hook
bootstraps this behavioral source. The Agent Host activates it and the Agent
Runtime interprets it; neither role is the Client by default.

The confirmation is limited to the participant relation observable at that
revision. It does not establish equal activation reliability or behavioral
equivalence across supported Hosts.

## Constructive sample

- **Status:** constructive
- **Unit:** [`sample/SKILL.md`](sample/SKILL.md) and its three child Skills
- **Executable oracle:** [`sample/scripts/run_demo.py`](sample/scripts/run_demo.py)
- **Focused verification:** [`sample/tests/test_demo.py`](sample/tests/test_demo.py)

The local production-incident sample demonstrates that the mapping can be
built and tested. It is not evidence about Superpowers, open-source frequency,
or comparative quality. Conversely, the Superpowers case does not validate
the local sample; each claim has its own artifacts and verification boundary.

## Named but not upgraded

The paper also names gstack root routing. This record does not upgrade that
mention to confirmed correspondence because the bounded claim above already
has exact, frozen Superpowers evidence and no additional claim is necessary for
the constructive demonstration.
