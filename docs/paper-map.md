# Paper Map

This map binds the paper's pattern-transfer claims to the research provenance and the public repository supplement. The paper is authoritative for the ontology; the repositories supply different forms of evidence and reproducibility.

## Main-text continuity argument

Paper Section 5.3, "Design Pattern Transfer as Software-Continuity Evidence," presents the six mappings summarized in Table 5.

| Table 5 pattern | Paper participant relation | Research record | Public pattern path |
| --- | --- | --- | --- |
| Facade | Entry Skill exposes one access contract over specialist Skills. | `research/patterns/facade.md` | `patterns/facade/` |
| Adapter | A thin binding translates canonical semantics into a target contract. | `research/patterns/adapter.md` | `patterns/adapter/` |
| Composite | Atomic and composite stages share an invocation and result contract. | `research/patterns/composite.md` | `patterns/composite/` |
| Observer | A subject emits typed events to registered independent consumers. | `research/patterns/observer.md` | `patterns/observer/` |
| State | Persisted state governs permitted actions and transitions. | `research/patterns/state.md` | `patterns/state/` |
| Strategy | Interchangeable procedures share one request and result contract. | `research/patterns/strategy.md` | `patterns/strategy/` |

These mappings test whether established responsibilities, interfaces, contracts, and dependencies remain observable when persistent behavioral source participates in the implementation. They do not claim ecosystem prevalence or comparative benefit.

## Repository supplement

The paper states that the repository supplement contains ten detailed GoF implementations: Facade, Adapter, Composite, Decorator, Strategy, Template Method, Observer, State, Memento, and Mediator. The four detailed GoF paths beyond Table 5 are:

- `patterns/decorator/`
- `patterns/template-method/`
- `patterns/memento/`
- `patterns/mediator/`

Two other traditions remain explicitly outside GoF:

| Pattern | Prior tradition | Research record | Public pattern path |
| --- | --- | --- | --- |
| Pipes and Filters | Pattern-Oriented Software Architecture | `research/patterns/pipes-and-filters.md` | `patterns/pipes-and-filters/` |
| Specification | Domain-Driven Design | `research/patterns/specification.md` | `patterns/specification/` |

The [detailed pattern index](../catalog/pattern-index.md) records all twelve selected implementations, source traditions, paper roles, and scenarios. The [GoF-23 screening matrix](../catalog/gof-23-screening.md) records the complete source-pattern screen. A screening result is not a detailed implementation, frequency estimate, or quality judgment.

## Evidence roles

| Artifact | Role |
| --- | --- |
| Paper | Defines the Skillware ontology and argues for software-engineering continuity. |
| Research repository | Preserves manuscript source, corpus analysis, frozen revisions, correspondence records, counterevidence, and research provenance. |
| Public pattern repository | Publishes the transfer protocol, catalog, participant mappings, constructive samples, misuses, and focused verification. |

There is no circular evidence: a public sample can demonstrate that a mapping can be constructed, but it cannot establish the ontology that was used to design the sample. Likewise, a correspondence record does not become source-pattern evidence merely because the public repository cites it. A newly discovered public case becomes a future research input only after its revision, method version, evidence paths, and human review are frozen.
