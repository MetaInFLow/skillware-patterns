# OpenMontage frozen State candidate evidence

## Evidence identity

- **Claim status:** candidate correspondence
- **Paper wording:** Candidate checkpoint behavior; full GoF participant
  delegation unverified.
- **Target repository:** `calesthio/OpenMontage`
- **Frozen commit:** `db91727598d08d40919d7d68a47864a5467bd448`
- **Evaluation unit:** the agent guide, checkpoint behavioral source, checkpoint
  implementation, and checkpoint schema at the fixed revision
- **Method:** bounded source inspection of the four exact public artifacts below

This local record summarizes observations and counterevidence. It does not copy
upstream code, infer runtime success, or treat a checkpoint name as sufficient
proof of State.

## Fixed source paths

1. [`AGENT_GUIDE.md`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/AGENT_GUIDE.md)
2. [`lib/checkpoint.py`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/lib/checkpoint.py)
3. [`skills/meta/checkpoint-protocol.md`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/skills/meta/checkpoint-protocol.md)
4. [`schemas/checkpoints/checkpoint.schema.json`](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/schemas/checkpoints/checkpoint.schema.json)

All four paths were inspected at the 40-character commit above. The public blob
URLs resolve to that revision rather than a moving branch.

## Observed checkpoint behavior

`AGENT_GUIDE.md` requires stage-by-stage execution through director Skills and
forbids bypassing checkpoints. It describes the guide and pipeline as the
production execution protocol, connecting the checkpoint source to agent work
rather than presenting it only as unused library code.

`lib/checkpoint.py` validates stage and status, writes a complete checkpoint via
temporary file plus atomic replacement, reads persisted checkpoints, collects
only checkpoints whose status is `completed`, and selects the first incomplete
stage as the next stage. Persisted checkpoint content therefore affects which
work runs next.

`skills/meta/checkpoint-protocol.md` declares checkpoints as pipeline save
points. At stage entry it requires `in_progress`; on restart it reads persisted
state and distinguishes at least three behaviors: resume partial work and skip
completed subtasks for `in_progress`, wait for user approval for
`awaiting_human`, and advance past completed stages through `get_next_stage`.

`schemas/checkpoints/checkpoint.schema.json` defines a resumable snapshot with
required stage and status fields and the finite statuses `completed`, `failed`,
`awaiting_human`, and `in_progress`. It supports validation of the persisted
records used by the implementation and protocol.

## Participant audit

- **Context:** partially suggested by the pipeline execution protocol and the
  checkpoint helper that selects subsequent work, but no single GoF Context
  participant is established across the inspected paths.
- **State:** persisted `stage` and `status` affect resume and next-stage behavior,
  providing state-dependent behavior evidence.
- **ConcreteState:** not established. Status handling is described through
  central branches and helper functions, not separate objects implementing one
  State operation.

This evidence does not establish the complete GoF State participant relation.
In particular, it does not show Context-to-State delegation or legal transition
ownership by ConcreteState implementations.

## Counterevidence and limits

The source provides a checkpoint schema, helper functions, and instructions,
not a complete object collaboration matching the canonical participants.
Stage order comes from pipeline manifests, and status-dependent instructions
remain centralized. The bounded review found no end-to-end recovery test among
these four paths and did not execute a media pipeline. Agent Host activation and
Agent Runtime interpretation are contextual relations, not GoF State roles.

The proper claim is **candidate correspondence**, not confirmed correspondence.
The local vendor-onboarding sample constructs the missing participant relation,
but that construction cannot validate or upgrade the OpenMontage evidence.
