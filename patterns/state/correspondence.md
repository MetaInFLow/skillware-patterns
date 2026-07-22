# State correspondence

## Candidate ecosystem correspondence

- **Status:** candidate correspondence
- **Paper wording:** Candidate checkpoint behavior; full GoF participant
  delegation unverified.
- **Case:** OpenMontage (`calesthio/OpenMontage`)
- **Fixed upstream commit:** `db91727598d08d40919d7d68a47864a5467bd448`
- **Agent execution guide:**
  [`AGENT_GUIDE.md`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/AGENT_GUIDE.md)
- **Checkpoint implementation:**
  [`lib/checkpoint.py`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/lib/checkpoint.py)
- **Checkpoint behavioral source:**
  [`skills/meta/checkpoint-protocol.md`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/skills/meta/checkpoint-protocol.md)
- **Checkpoint schema:**
  [`schemas/checkpoints/checkpoint.schema.json`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/schemas/checkpoints/checkpoint.schema.json)
- **Vendored assessment:**
  [frozen evidence](evidence/openmontage-frozen-case.md)

At this revision, OpenMontage persists schema-validated stage checkpoints with
`completed`, `failed`, `awaiting_human`, and `in_progress` status. Its helper
derives the next pipeline stage from completed checkpoints, while the checkpoint
protocol tells execution to resume partial work, wait for approval, or advance
depending on persisted status. This is source evidence for persisted and
resumed task-state-controlled behavior.

The correspondence remains candidate. The reviewed files centralize checkpoint
logic and status branches; they do not materialize separate GoF State and
ConcreteState participants or show a Context delegating the same operation to
those objects. Static source inspection also does not prove end-to-end Agent
Runtime behavior. Checkpoint vocabulary alone is not sufficient to confirm
State.

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
restart recovery, deterministic rejection before write, deletion and corruption
rejection, and stable fixture output. This local construction is independent of
the OpenMontage case and does not establish Agent Runtime interpretation.
