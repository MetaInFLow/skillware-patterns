# Paper Map

This repository release candidate is bound to `v0.1-paper-v1` and the public paper [Skillware: A Software Ontology and Engineering Lifecycle for Persistent Behavioral Artifacts](https://arxiv.org/abs/2607.18970) by Haodi Fan and Zucong Lan. arXiv records version 1 as submitted on 21 July 2026.

The private authoring/research archive preserves the manuscript source, corpus analysis, and research provenance at authoring revision `1fc1dfd`. That unlinked identifier is retained for provenance; the archive is not a public dependency. Claim-level evidence below resolves to the public paper or to self-contained files in this repository.

## Table 5 traceability

Paper Section 5.3, "Design Pattern Transfer as Software-Continuity Evidence," presents the six main-text mappings summarized in Table 5. Ecosystem correspondence and constructive sample status remain separate claims.

| Pattern | Skillware participant relation | Ecosystem correspondence status | Constructive sample status | Pattern record | Sample | Local correspondence | Paper qualification |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Facade | Entry Skill exposes one stable access contract over specialist Skills | confirmed correspondence | constructive | [definition](../patterns/facade/definition.md) | [sample](../patterns/facade/sample/) | [local correspondence](../patterns/facade/correspondence.md) | Superpowers participant mapping is verified in the frozen case; gstack root routing is also named. |
| Adapter | Thin binding translates canonical Skill semantics into a target system contract | confirmed correspondence | constructive | [definition](../patterns/adapter/definition.md) | [sample](../patterns/adapter/sample/) | [local correspondence](../patterns/adapter/correspondence.md) | Strong correspondence in the paper; runtime parity requires tests. |
| Composite | Atomic and composite stages share one invocation and result contract | candidate correspondence | constructive | [definition](../patterns/composite/definition.md) | [sample](../patterns/composite/sample/) | [local correspondence](../patterns/composite/correspondence.md) | Candidate correspondence plus a constructive repository fixture. |
| Observer | Subject emits typed events to registered independent consumers | candidate correspondence | constructive | [definition](../patterns/observer/definition.md) | [sample](../patterns/observer/sample/) | [local correspondence](../patterns/observer/correspondence.md) | Candidate pending complete registration and delivery evidence. |
| State | Persisted state controls permitted actions and transitions | candidate correspondence | constructive | [definition](../patterns/state/definition.md) | [sample](../patterns/state/sample/) | [local correspondence](../patterns/state/correspondence.md) | Candidate checkpoint behavior; full GoF participant delegation unverified. |
| Strategy | Stable request and result contract selects among interchangeable procedures | candidate correspondence | constructive | [definition](../patterns/strategy/definition.md) | [sample](../patterns/strategy/sample/) | [local correspondence](../patterns/strategy/correspondence.md) | Open-source correspondence is motivation only; comparative benefit requires runtime study. |

The statuses normalize Table 5 into the repository's controlled vocabulary without strengthening its evidence. In particular, Adapter confirmation does not imply runtime parity, and the four candidate rows retain the paper's incomplete or motivational qualifications. A constructive sample demonstrates buildability only; it does not confirm ecosystem correspondence.

## Repository supplement

The paper states that the repository supplement contains ten detailed GoF implementations: Facade, Adapter, Composite, Decorator, Strategy, Template Method, Observer, State, Memento, and Mediator. The remaining detailed mappings are auditable through local records, samples, and correspondence evidence.

| Pattern | Source tradition / category | Ecosystem correspondence status | Constructive sample status | Pattern record | Sample | Local correspondence |
| --- | --- | --- | --- | --- | --- | --- |
| Decorator | `gang-of-four` / `structural` | candidate correspondence | constructive | [definition](../patterns/decorator/definition.md) | [sample](../patterns/decorator/sample/) | [local correspondence](../patterns/decorator/correspondence.md) |
| Template Method | `gang-of-four` / `behavioral` | candidate correspondence | constructive | [definition](../patterns/template-method/definition.md) | [sample](../patterns/template-method/sample/) | [local correspondence](../patterns/template-method/correspondence.md) |
| Memento | `gang-of-four` / `behavioral` | candidate correspondence | constructive | [definition](../patterns/memento/definition.md) | [sample](../patterns/memento/sample/) | [local correspondence](../patterns/memento/correspondence.md) |
| Mediator | `gang-of-four` / `behavioral` | candidate correspondence | constructive | [definition](../patterns/mediator/definition.md) | [sample](../patterns/mediator/sample/) | [local correspondence](../patterns/mediator/correspondence.md) |
| Pipes and Filters | `pattern-oriented-software-architecture` / `architectural` | candidate correspondence | constructive | [definition](../patterns/pipes-and-filters/definition.md) | [sample](../patterns/pipes-and-filters/sample/) | [local correspondence](../patterns/pipes-and-filters/correspondence.md) |
| Specification | `domain-driven-design` / `domain` | not observable | constructive | [definition](../patterns/specification/definition.md) | [sample](../patterns/specification/sample/) | [local correspondence](../patterns/specification/correspondence.md) |

The [detailed pattern index](../catalog/pattern-index.md) records all twelve selected implementations, source traditions, paper roles, and scenarios. The [GoF-23 screening matrix](../catalog/gof-23-screening.md) records the complete source-pattern screen. A screening result is not a detailed implementation, frequency estimate, or quality judgment.

## Evidence roles

| Artifact | Role |
| --- | --- |
| [Public arXiv paper](https://arxiv.org/abs/2607.18970) | Defines the Skillware ontology and argues for software-engineering continuity. |
| Private authoring/research archive | Preserves manuscript source, corpus analysis, frozen revisions, counterevidence, and provenance at unlinked authoring revision `1fc1dfd`; it is not a public dependency. |
| Pattern repository release candidate | Provides the self-contained transfer protocol, catalog, participant mappings, correspondence files, constructive samples, misuses, and focused verification for `v0.1-paper-v1`. |

## Evidence entry rule

Tool or sample output cannot validate the Skillware ontology. It can support a bounded constructive claim when the sample and verification are reproducible. A cited correspondence is evaluated against its pinned source artifacts rather than confirmed by the citation itself.

New evidence can enter the paper only after the target revision and method version are frozen, evidence paths are recorded, and human review is complete.
