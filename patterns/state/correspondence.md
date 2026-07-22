# State correspondence

## Ecosystem correspondence

- **Status:** no ecosystem correspondence assessed
- **Scope:** no public repository, revision, or fixed source paths were
  evaluated for participant-level State correspondence in this record.

The broader catalog screening names persisted checkpoints, state records, and
transition manifests as possible carriers. Those labels are discovery cues,
not evidence that any specific system materializes Context, State, and
ConcreteState with state-dependent delegation and owned legal transitions.

No confirmed or candidate ecosystem claim is made here. A later assessment
would need a fixed public revision and paths that demonstrate persisted state,
behavior selected by the current state, ConcreteState transition ownership,
illegal-transition handling, and restart recovery.

## Constructive sample

- **Status:** constructive
- **Context:** [`sample/SKILL.md`](sample/SKILL.md)
- **State contract:**
  [`sample/references/vendor-state-contract.md`](sample/references/vendor-state-contract.md)
- **ConcreteStates:** [`sample/child-skills/`](sample/child-skills/)
- **Persistence fixture:**
  [`sample/fixtures/valid/vendor-onboarding.json`](sample/fixtures/valid/vendor-onboarding.json)
- **Recovery fixture:**
  [`sample/fixtures/valid/recover-approved.json`](sample/fixtures/valid/recover-approved.json)
- **Executable oracle:** [`sample/scripts/run_demo.py`](sample/scripts/run_demo.py)
- **Focused verification:** [`sample/tests/test_demo.py`](sample/tests/test_demo.py)

The Context reloads one versioned record, delegates to a distinct ConcreteState,
and atomically persists the successor only after legal handling. Tests prove
restart recovery, deterministic rejection before write, corruption rejection,
and stable fixture output. This local construction is not ecosystem evidence
and does not establish Agent Runtime interpretation.
