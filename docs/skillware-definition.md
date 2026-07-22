# Skillware Definition

Skillware is the software abstraction extending software engineering to persistent Behavioral Artifacts. A Skill Artifact specifies reusable task behavior; a Skillware Unit manages that artifact as an independently addressable software object. A compatible Agent Host activates the unit for interpretation by an Agent Runtime.

## Ontology

Behavioral Source -> Skill Artifact -> Skillware Unit -> Agent Host -> Agent Runtime -> Execution Trace -> Task Outcome

The chain assigns a distinct responsibility to each object:

| Object | Responsibility |
| --- | --- |
| Behavioral Source | Expresses persistent instructions, constraints, policies, examples, and evaluation criteria that carry a reusable task contract. |
| Skill Artifact | Persists the reusable behavior and its supporting materials. |
| Skillware Unit | Gives one Skill Artifact or coherent suite an independently managed identity, version, provenance, compatibility boundary, and lifecycle. |
| Agent Host | Discovers or receives the unit, activates it, and supplies or delegates runtime execution. |
| Agent Runtime | Interprets activated source with a task, model, context, tools, permissions, state, and agent loop. |
| Execution Trace | Records situated performance for a particular execution context. |
| Task Outcome | Evaluates the effect of that execution against task criteria. |

An artifact specification is therefore not evidence of actual runtime behavior, and an execution trace is not by itself evidence of task effectiveness.

## C1: Skill-centered behavioral primacy

One Skill or coherent Skill suite carries and organizes the reusable task behavior. Its source defines the task interface, decision procedure, constraints, and relation to support components. Supporting code may be substantial, but it does not displace the Skill-centered source as the primary carrier of behavior, routing, and user-facing identity.

## C2: Independent software identity

The candidate Skillware Unit has an addressable software identity that can be acquired, installed, and tracked independently of the Agent Host. Observable identity may include a name, address, package boundary, version, compatibility declaration, and provenance record.

## C3: Agent Host execution relationship

At least one identified compatible Agent Host can discover or receive, activate, load, and use the same Skillware Unit through skills-compatible operations. The Host owns activation; the Agent Runtime owns situated interpretation and execution. Cross-Host parity is a separate compatibility question.

C1, C2, and C3 are necessary membership conditions and must converge on the same declared Skillware Unit. They do not score quality, security, usefulness, popularity, complexity, or maturity.

## Lifecycle Continuity

Lifecycle Continuity is a separate software-grade property, not a fourth membership condition. It records whether the same Skillware Unit identity persists through update, maintenance, disablement or rollback, and removal. It is evaluated only after C1-C3 establish category membership.
