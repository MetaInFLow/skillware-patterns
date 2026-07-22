# Paper Map

This repository release is bound to `v0.1-paper-v1` and the [paper source pinned at `1fc1dfd`](https://github.com/MetaInFLow/skillware/blob/1fc1dfd/paper/manuscript-ars-v1/phase7_output_arxiv/main.tex). Every research link below targets the same frozen revision of the canonical `MetaInFLow/skillware` repository.

## Table 5 traceability

Paper Section 5.3, "Design Pattern Transfer as Software-Continuity Evidence," presents the six main-text mappings summarized in Table 5. Ecosystem correspondence and constructive sample status remain separate claims.

| Pattern | Skillware participant relation | Ecosystem correspondence status | Constructive sample status | Pattern record | Sample | Pinned research evidence | Paper qualification |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Facade | Entry Skill exposes one stable access contract over specialist Skills | confirmed correspondence | constructive | [definition](../patterns/facade/definition.md) | [sample](../patterns/facade/sample/) | [pinned research record](https://github.com/MetaInFLow/skillware/blob/1fc1dfd/research/patterns/facade.md) | Superpowers participant mapping is verified in the frozen case; gstack root routing is also named. |
| Adapter | Thin binding translates canonical Skill semantics into a target system contract | confirmed correspondence | constructive | [definition](../patterns/adapter/definition.md) | [sample](../patterns/adapter/sample/) | [pinned research record](https://github.com/MetaInFLow/skillware/blob/1fc1dfd/research/patterns/adapter.md) | Strong correspondence in the paper; runtime parity requires tests. |
| Composite | Atomic and composite stages share one invocation and result contract | candidate correspondence | constructive | [definition](../patterns/composite/definition.md) | [sample](../patterns/composite/sample/) | [pinned research record](https://github.com/MetaInFLow/skillware/blob/1fc1dfd/research/patterns/composite.md) | Candidate correspondence plus a constructive repository fixture. |
| Observer | Subject emits typed events to registered independent consumers | candidate correspondence | constructive | [definition](../patterns/observer/definition.md) | [sample](../patterns/observer/sample/) | [pinned research record](https://github.com/MetaInFLow/skillware/blob/1fc1dfd/research/patterns/observer.md) | Candidate pending complete registration and delivery evidence. |
| State | Persisted state controls permitted actions and transitions | candidate correspondence | constructive | [definition](../patterns/state/definition.md) | [sample](../patterns/state/sample/) | [pinned research record](https://github.com/MetaInFLow/skillware/blob/1fc1dfd/research/patterns/state.md) | Candidate checkpoint behavior; full GoF participant delegation unverified. |
| Strategy | Stable request and result contract selects among interchangeable procedures | candidate correspondence | constructive | [definition](../patterns/strategy/definition.md) | [sample](../patterns/strategy/sample/) | [pinned research record](https://github.com/MetaInFLow/skillware/blob/1fc1dfd/research/patterns/strategy.md) | Open-source correspondence is motivation only; comparative benefit requires runtime study. |

The statuses normalize Table 5 into the repository's controlled vocabulary without strengthening its evidence. In particular, Adapter confirmation does not imply runtime parity, and the four candidate rows retain the paper's incomplete or motivational qualifications. A constructive sample demonstrates buildability only; it does not confirm ecosystem correspondence.

## Repository supplement

The paper states that the repository supplement contains ten detailed GoF implementations: Facade, Adapter, Composite, Decorator, Strategy, Template Method, Observer, State, Memento, and Mediator. The remaining detailed mappings are auditable through their planned public paths and pinned research records.

| Pattern | Source tradition | Pattern record | Sample | Pinned research record |
| --- | --- | --- | --- | --- |
| Decorator | Gang of Four | [definition](../patterns/decorator/definition.md) | [sample](../patterns/decorator/sample/) | [research record](https://github.com/MetaInFLow/skillware/blob/1fc1dfd/research/patterns/decorator.md) |
| Template Method | Gang of Four | [definition](../patterns/template-method/definition.md) | [sample](../patterns/template-method/sample/) | [research record](https://github.com/MetaInFLow/skillware/blob/1fc1dfd/research/patterns/template-method.md) |
| Memento | Gang of Four | [definition](../patterns/memento/definition.md) | [sample](../patterns/memento/sample/) | [research record](https://github.com/MetaInFLow/skillware/blob/1fc1dfd/research/patterns/memento.md) |
| Mediator | Gang of Four | [definition](../patterns/mediator/definition.md) | [sample](../patterns/mediator/sample/) | [research record](https://github.com/MetaInFLow/skillware/blob/1fc1dfd/research/patterns/mediator.md) |
| Pipes and Filters | Pattern-Oriented Software Architecture, not GoF | [definition](../patterns/pipes-and-filters/definition.md) | [sample](../patterns/pipes-and-filters/sample/) | [research record](https://github.com/MetaInFLow/skillware/blob/1fc1dfd/research/patterns/pipes-and-filters.md) |
| Specification | Domain-Driven Design, not GoF | [definition](../patterns/specification/definition.md) | [sample](../patterns/specification/sample/) | [research record](https://github.com/MetaInFLow/skillware/blob/1fc1dfd/research/patterns/specification.md) |

The [detailed pattern index](../catalog/pattern-index.md) records all twelve selected implementations, source traditions, paper roles, and scenarios. The [GoF-23 screening matrix](../catalog/gof-23-screening.md) records the complete source-pattern screen. A screening result is not a detailed implementation, frequency estimate, or quality judgment.

## Evidence roles

| Artifact | Role |
| --- | --- |
| [Paper source](https://github.com/MetaInFLow/skillware/blob/1fc1dfd/paper/manuscript-ars-v1/phase7_output_arxiv/main.tex) | Defines the Skillware ontology and argues for software-engineering continuity. |
| [Research repository](https://github.com/MetaInFLow/skillware/tree/1fc1dfd) | Preserves manuscript source, corpus analysis, frozen revisions, correspondence records, counterevidence, and research provenance. |
| Public pattern repository | Publishes the transfer protocol, catalog, participant mappings, constructive samples, misuses, and focused verification for `v0.1-paper-v1`. |

## Evidence entry rule

Tool or sample output cannot validate the Skillware ontology. It can support a bounded constructive claim when the sample and verification are reproducible. A cited correspondence is evaluated against its pinned source artifacts rather than confirmed by the citation itself.

New evidence can enter the paper only after the target revision and method version are frozen, evidence paths are recorded, and human review is complete.
