# 组合模式（Composite）

**Canonical source.** Composite is the structural pattern described in the
Gang of Four tradition by Gamma, Helm, Johnson, and Vlissides in *Design
Patterns: Elements of Reusable Object-Oriented Software* (1994). This record
transfers that established pattern; it does not claim a new pattern or
historical priority for Skillware.

## Intent

Compose components into part-whole trees so a Client can treat an individual
object and a composition of objects uniformly through one Component contract.

## Forces

- A task has both atomic units and structured groups, but the Client should not
  branch on which one it receives.
- Leaves must stay independently inspectable while parent compositions retain
  a meaningful shared identity.
- A shared contract must be useful to both roles without accumulating
  operations meaningful only to one of them.
- Explicit containment order and cycle rules make the part-whole relation
  predictable, but add validation and traversal cost.
- File and folder organization can carry the relation, yet cannot establish it
  without uniform behavior and explicit composition.

## Participants

- **Client:** the task caller invoking the root investment memo, or invoking an
  independently addressable analysis Leaf through the same result contract.
- **Component:** the common node invocation and `memo-section-v1` record with
  exactly `id`, `title`, `content`, `evidence`, and `children`. Demo mode models
  invocation as `build_component(workflow, node_id, leaf_executors=None)`.
- **Leaf:** the market, financial, competition, and risk analysis Skills. Each
  returns one Component record with `children: []`.
- **Composite:** the root investment-memo Skill together with the serialized
  workflow that declares child references. It returns the same Component
  fields and contains complete child Component records in `children`.
- **Agent Host and Agent Runtime:** execution context, not GoF Composite
  participants. A deployed Host may activate a Skill and a Runtime may
  interpret it, but those relations are not observable in this constructive
  sample.

## Collaboration

The Client invokes either the root or a Leaf through the Component contract.
In Agent mode, the root calls each associated child Skill with declared input.
In demo mode, the builder calls an explicit deterministic executor keyed by
that child Skill path. Each Leaf computes and returns the common five-field
record with an empty child list; the Composite validates and assembles those
records without changing their public shape. Complete registry validation runs
first and enforces existence, uniqueness, one parent, reachability, and global
acyclicity.

## Consequences

Clients can process atomic sections and complete memos with one recursive data
shape. Leaves stay independently inspectable, nested groups can be added
without changing the Client contract, and declared order remains observable.
Trade-offs include recursive validation cost, the risk of an overbroad
Component contract, ambiguity about operations that only composites support,
and the need to define ownership, identity, cycle, and error policies.

## Skillware Mapping

Natural-language behavioral sources define atomic and grouped work, while a
serialized workflow supplies node identity, Leaf inputs, associated Skill
paths, and containment references. The deterministic executors and builder are
an executable oracle for the declared collaboration and traversal rules; they
do not interpret `SKILL.md`. The pattern relation spans the root Skill, child
Skills, contract reference, and workflow rather than any one file type.

### Final ontology

The final ontology retains the canonical GoF roles without adding platform
roles: **Client**, **Component**, **Leaf**, and **Composite**. `Agent Host` and
`Agent Runtime` remain contextual roles outside that ontology. A directory is
not a fifth participant, and folder containment is not itself Composite.
Uniform Component treatment plus a valid part-whole relation is the defining
structure.

## Applicability

Use Composite when a Skillware task contains atomic Skills and nested workflow
Skills that should be invoked or consumed through one stable contract, when
the grouped result has a real identity, and when explicit child references can
form a validated part-whole tree. It is useful for reports, plans, review
packages, or other recursive artifacts whose sections can also stand alone.

## Non-Applicability

Do not use Composite for a flat sequence whose stages intentionally return
different shapes, an arbitrary dependency graph, or a directory that only
groups related Skills. Do not force Leaf-only operations into Component merely
to obtain surface symmetry. Use Facade when the main force is simplified
access to subsystems, Pipes and Filters for transformed stage streams, or
Mediator for centralized peer coordination.

## Positive Evidence

The repository sample is **constructive** evidence. Its root memo and four
Leaves return the exact same keys and types. Four explicit executors compute
Leaf records from serialized inputs, and dependency-injection tests prove each
is called exactly once in declared order. Whole-registry tests reject missing
references, repeated children, shared-child DAGs, root parents, unreachable
nodes, disconnected cycles, duplicates, malformed schema, and bad results.

## Counter-Evidence

The deterministic functions do not prove that an Agent Runtime will interpret
natural-language Skills identically across Hosts. The default sample has one
Composite level, although a focused test exercises a nested Composite. The
executors model child collaboration and predictable fixture analysis; Python
does not invoke or interpret the child Skill instructions and the sample does
not model probabilistic analysis quality.

## False Positives

A directory of market, finance, competition, and risk Skills is not Composite
when their results differ and a parent only lists paths. A workflow graph is
also not Composite if the same edge represents dependency rather than
part-whole containment, if a child has multiple parents, or if Leaves and
groups expose different contracts.
The [`misuse/SKILL.md`](misuse/SKILL.md) artifact intentionally demonstrates
this near miss.

## Open-Source Correspondence

OpenMontage is evaluated at commit
`db91727598d08d40919d7d68a47864a5467bd448`, including exact public paths
`pipeline_defs/animation.yaml`,
`skills/pipelines/animation/executive-producer.md`,
`skills/pipelines/animation/research-director.md`, and
`lib/pipeline_loader.py`. The manifest-to-orchestrator-to-stage relation is a
**candidate correspondence**, not a confirmed one. Stage artifacts use
different schemas and may form a pipeline dependency graph rather than one
uniform part-whole tree. `.agents/skills/create-video/SKILL.md` is vendor/API
guidance, not positive stage evidence. See
[`correspondence.md`](correspondence.md) for pinned links and the evidence
boundary.

## Verification

From `sample/`, run `python3 scripts/run_demo.py` and `python3 -m unittest
discover tests -v`. Verification checks the exact assembled memo, all four
Leaves in declared order, identical recursive keys and types, empty Leaf child
lists, exactly-once injected executor calls, complete tree invariants, strict
result validation, input immutability, exact CLI errors, pinned evidence paths,
and absence of network or shared imports.

## Limitations

One constructive scenario and one candidate ecosystem correspondence do not
establish prevalence, comparative benefit, production robustness, or
cross-Host equivalence. The sample validates structural composition, not the
truth or investment quality of its fixture content. The mapping preserves the
canonical GoF intent and roles without claiming that Skillware invented
Composite or that a Skill folder automatically implements it.
