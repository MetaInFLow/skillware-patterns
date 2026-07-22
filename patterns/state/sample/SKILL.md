---
name: vendor-onboarding-workflow
description: Advance vendor onboarding through persisted legal states. Use when verification, approval, and activation behavior depends on recovered state.
intent: Delegate each onboarding action to the current state Skill, atomically persist successful transitions, and recover state before later work.
type: workflow
---

# Vendor Onboarding Workflow

## Trigger

Use this root Skill when a vendor must move through verification, approval, and
activation under an explicit persisted lifecycle. The input must identify one
vendor, one state record, and one requested action.

## Participants

This Skill is the Context. `vendor-onboarding-state-v1` is the State contract.
The draft, verified, approved, and activated child Skills are ConcreteStates;
each owns its permitted action and successor.

Agent Host and Agent Runtime are execution context, not State participants.

## Agent mode

1. At explicit workflow bootstrap, create `draft` only when no record exists.
   After this Context is initialized, load the record before every requested
   action; a missing, corrupted, or non-UTF-8 record is an error and must never
   be recreated implicitly.
2. Validate schema, vendor identity, state, and revision against
   `references/vendor-state-contract.md`.
3. Invoke only the child Skill named by the persisted state through
   `handle-action`.
4. Let that ConcreteState accept its one legal action or return the exact
   illegal-transition error. Do not choose a successor in this Context.
5. For success, atomically persist the complete successor record before
   reporting or updating in-memory state.
6. Return action, source state, successor state, state-specific behavior, and
   revision. A later activation must reload the persisted state first.

## ConcreteState Skills

- `child-skills/draft/SKILL.md`
- `child-skills/verified/SKILL.md`
- `child-skills/approved/SKILL.md`
- `child-skills/activated/SKILL.md`

## Demo mode

`scripts/run_demo.py` implements the Context, State operation, and four distinct
ConcreteState classes with Python standard-library persistence. It reloads
before each action and again after the sequence to expose restart recovery.
Constructing a new workflow is the explicit bootstrap boundary. Deletion after
that point is corruption, not a request to bootstrap again. Python does not
interpret the natural-language Skills.

## Output contract

Return the vendor identity, initial state, ordered transition results, final
state, recovered state, and revision. Illegal transitions and corrupted state
produce errors and do not modify the persisted record.

## Example

The default fixture starts in `draft`, then applies `verify`, `approve`, and
`activate`, ending and recovering in `activated` at revision 3.

## Ontology boundary

Behavioral Source -> Skill Artifact -> Skillware Unit -> Agent Host -> Agent Runtime -> Execution Trace -> Task Outcome

The State roles belong to the pattern mapping. Agent Host and Agent Runtime
remain execution context and are not reclassified as State participants.

## Anti-pattern

Conditional text that mentions phases but stores no state, gives no
ConcreteState ownership, and cannot recover after restart is not State. See
`../misuse/SKILL.md`.
