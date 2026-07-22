# Skillware Definition

Skillware is an emerging AI-native software abstraction whose primary Behavioral Artifact is a separately addressable Agent Skill or coherent Skill suite. A Skillware Unit is the independently managed software identity that carries this artifact as software. The Skill source carries reusable task behavior primarily through persistent natural-language behavioral source, optionally supported by code and resources. A compatible Agent Host activates the unit, and the Agent Runtime interprets its activated behavioral source for execution.

Skillware extends software engineering to persistent Behavioral Artifacts. AI-native identifies software whose primary task behavior depends on model-mediated interpretation during execution. The Skillware Unit carries its own name, address, version, compatibility, provenance, and lifecycle responsibilities; it is the identity acquired, tracked, versioned, maintained, and removed independently of the Agent Host.

## Ontology

Behavioral Source -> Skill Artifact -> Skillware Unit -> Agent Host -> Agent Runtime -> Execution Trace -> Task Outcome

The arrows assign distinct responsibilities rather than collapsing these objects. The Agent Host activates the Skillware Unit and provides or delegates runtime execution. The Agent Runtime interprets the activated behavioral source with a task, model, assembled context, tools, permissions, state, and agent loop, producing an Execution Trace. Task Outcome is the effect or result of the execution, evaluated against task criteria.

| Object | Responsibility |
| --- | --- |
| Behavioral Source | Expresses persistent instructions, constraints, policies, examples, and evaluation criteria that carry a reusable task contract. |
| Skill Artifact | Specifies and persists reusable behavior and its supporting materials. |
| Skillware Unit | Manages the artifact as a separately addressable software object with independent identity and lifecycle. |
| Agent Host | Discovers or receives and activates the unit, then supplies or delegates runtime execution. |
| Agent Runtime | Interprets the activated source in a situated execution context. |
| Execution Trace | Records situated performance for one task, model, context, tool set, permission policy, and state. |
| Task Outcome | Is the evaluated effect or result of that execution. |

An artifact specification is not evidence of actual runtime behavior. An execution trace observes a situated run but does not by itself establish task effectiveness.

## C1: Skill-centered behavioral primacy

One Skill or a coherent Skill suite carries and organizes the reusable task behavior. The Skill source defines the task interface, decision procedure, constraints, and relation to support components. Supporting code can be substantial. The category test asks which artifact remains primary in the acquired unit's behavior, routing, and user-facing identity.

## C2: Independent software identity

The candidate unit has an addressable software identity that can be acquired, installed, and tracked independently of the Agent Host. A directory, package, installer, plugin, or repository release can establish observable name, address, version, compatibility, and provenance records.

## C3: Agent Host execution relationship

At least one identified compatible Agent Host can discover or receive, activate, load, and use the unit through skills-compatible operations. A documented or reproduced path in a compatible system is sufficient for category membership. Cross-Host parity remains a separate compatibility question.

C1, C2, and C3 are necessary membership conditions and must converge on the same declared Skillware Unit. They do not score quality, security, usefulness, popularity, implementation complexity, or lifecycle maturity.

## Lifecycle Continuity

Lifecycle Continuity is a separate software-grade property, not a fourth membership condition. The same unit identity persists across update, maintenance, disablement or rollback, and removal. Responsibility can be distributed among the project, installer, package manager, lifecycle infrastructure, and Agent Host. Lifecycle Continuity is evaluated after C1-C3 establish category membership.
