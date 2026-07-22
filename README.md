# Skillware Patterns

An executable, bilingual pattern-transfer supplement for the Skillware paper.

[简体中文](README.zh-CN.md)

## Paper and repository role

This repository accompanies the public paper [Skillware: A Software Ontology and Engineering Lifecycle for Persistent Behavioral Artifacts](https://arxiv.org/abs/2607.18970) by Haodi Fan and Zucong Lan. It publishes auditable pattern-transfer records and deterministic examples for one bounded part of the paper's software-engineering continuity argument.

**Skillware is the software abstraction that extends software engineering to persistent behavioral artifacts.** The relevant boundary is:

```text
Behavioral Source -> Skill Artifact -> Skillware Unit -> Agent Host -> Agent Runtime
```

Behavioral Source carries persistent task instructions and constraints. A Skill Artifact packages that source with optional code and resources. A Skillware Unit gives the artifact an independently managed software identity and lifecycle. A compatible Agent Host activates the unit; the Agent Runtime interprets the activated source in a situated execution context. See the [complete definition and category conditions](docs/skillware-definition.md).

## Software-engineering continuity

The repository tests whether established software patterns remain recognizable when persistent behavioral artifacts, rather than conventional classes alone, carry key responsibilities. A transfer is admitted only when source intent, forces, participant relations, consequences, implementation evidence, focused verification, and a misuse discriminator remain observable.

This is not a new design-pattern collection. The source patterns and their traditions remain prior software-engineering knowledge. This supplement contributes bounded Skillware participant mappings and constructive implementations; it does not claim ownership of the patterns or use a pattern name as evidence of transfer.

## Responsibility map

| Artifact | Responsibility | Evidence boundary |
| --- | --- | --- |
| [Public arXiv paper](https://arxiv.org/abs/2607.18970) | Defines the Skillware ontology and argues for software-engineering continuity. | The public abstract record is the authoritative paper entry point. |
| Private authoring/research archive | Preserves manuscript source, corpus analysis, frozen cases, counterevidence, and provenance. | Authoring revision `1fc1dfd` is an unlinked provenance identifier; the archive is not a public dependency. |
| `MetaInFlow/skillware-patterns` (this repository) | Publishes the transfer protocol, sourced catalog, participant maps, runnable samples, misuse cases, and focused tests. | This self-contained executable supplement carries the local evidence required to inspect and run its claims. Its output cannot validate the ontology or establish ecosystem prevalence. |

The [paper map](docs/paper-map.md) keeps these responsibilities separate and binds this supplement to `v0.1-paper-v1`.

## Catalog at a glance

| Declared scope | Meaning | Index |
| --- | --- | --- |
| **23 GoF patterns screened** | One sourced screening record per canonical Gang of Four pattern; screening is not implementation. | [GoF-23 screening matrix](catalog/gof-23-screening.md) |
| **10 detailed GoF implementations** | Six main-text patterns and four repository-supplement patterns, each with a standalone constructive sample. | [Detailed pattern index](catalog/pattern-index.md) |
| **2 patterns from other established traditions** | POSA Pipes and Filters and DDD Specification, labeled separately from GoF. | [Detailed catalog metadata](catalog/pattern-index.yaml) |

The twelve pattern directories are peers in one flat navigation tree. `source_tradition`, `source_category`, `paper_role`, and `implementation_status` are metadata recorded in each `pattern.yaml`; `source_category` preserves the source tradition's category and does not create a second directory hierarchy.

## Main-text mappings

Paper Section 5.3 and Table 5 use these six mappings. Ecosystem correspondence and local constructibility are deliberately separate claim columns.

| Pattern | Source tradition / `source_category` | Skillware participant relation | Ecosystem claim | Local sample claim | Record and evidence |
| --- | --- | --- | --- | --- | --- |
| [Facade](patterns/facade/definition.md) | `gang-of-four` / `structural` | One entry Skill exposes a stable contract over specialist Skills. | confirmed correspondence | constructive | [correspondence](patterns/facade/correspondence.md) · [sample](patterns/facade/sample/) |
| [Adapter](patterns/adapter/definition.md) | `gang-of-four` / `structural` | A thin binding translates canonical Skill semantics into a target system contract. | confirmed correspondence | constructive | [correspondence](patterns/adapter/correspondence.md) · [sample](patterns/adapter/sample/) |
| [Composite](patterns/composite/definition.md) | `gang-of-four` / `structural` | Atomic and composite stages share one invocation and result contract. | candidate correspondence | constructive | [correspondence](patterns/composite/correspondence.md) · [sample](patterns/composite/sample/) |
| [Observer](patterns/observer/definition.md) | `gang-of-four` / `behavioral` | A subject emits typed events to registered independent consumers. | candidate correspondence | constructive | [correspondence](patterns/observer/correspondence.md) · [sample](patterns/observer/sample/) |
| [State](patterns/state/definition.md) | `gang-of-four` / `behavioral` | Persisted state controls permitted actions and transitions. | candidate correspondence | constructive | [correspondence](patterns/state/correspondence.md) · [sample](patterns/state/sample/) |
| [Strategy](patterns/strategy/definition.md) | `gang-of-four` / `behavioral` | One request/result contract selects among interchangeable procedures. | candidate correspondence | constructive | [correspondence](patterns/strategy/correspondence.md) · [sample](patterns/strategy/sample/) |

The statuses reproduce the evidence boundaries in the [paper map](docs/paper-map.md); a constructive sample does not upgrade a candidate ecosystem correspondence.

## Repository supplement

The supplement provides four additional GoF records and two records from other established traditions.

| Pattern | Source tradition / `source_category` | Skillware participant relation | Ecosystem claim | Local sample claim | Record and evidence |
| --- | --- | --- | --- | --- | --- |
| [Decorator](patterns/decorator/definition.md) | `gang-of-four` / `structural` | Optional review Skills wrap one shared component contract. | candidate correspondence | constructive | [correspondence](patterns/decorator/correspondence.md) · [sample](patterns/decorator/sample/) |
| [Template Method](patterns/template-method/definition.md) | `gang-of-four` / `behavioral` | A root Skill owns invariant workflow order and bounded specialization hooks. | candidate correspondence | constructive | [correspondence](patterns/template-method/correspondence.md) · [sample](patterns/template-method/sample/) |
| [Memento](patterns/memento/definition.md) | `gang-of-four` / `behavioral` | A caretaker captures and restores an originator's opaque configuration state. | candidate correspondence | constructive | [correspondence](patterns/memento/correspondence.md) · [sample](patterns/memento/sample/) |
| [Mediator](patterns/mediator/definition.md) | `gang-of-four` / `behavioral` | A coordinator centralizes interaction among deployment-readiness Skills. | candidate correspondence | constructive | [correspondence](patterns/mediator/correspondence.md) · [sample](patterns/mediator/sample/) |
| [Pipes and Filters](patterns/pipes-and-filters/definition.md) | `pattern-oriented-software-architecture` / `architectural` | Ordered Filters transform one versioned ticket record through explicit Pipes. | candidate correspondence | constructive | [correspondence](patterns/pipes-and-filters/correspondence.md) · [sample](patterns/pipes-and-filters/sample/) |
| [Specification](patterns/specification/definition.md) | `domain-driven-design` / `domain` | Named, composable rules evaluate one bounded expense candidate. | not observable | constructive | [correspondence](patterns/specification/correspondence.md) · [sample](patterns/specification/sample/) |

Pipes and Filters is not a GoF pattern; Specification is not a GoF pattern. Their labels preserve the established POSA and DDD provenance.

## Facade walkthrough

The Production Incident Response sample makes the transfer concrete:

1. The root [Facade Skill](patterns/facade/sample/SKILL.md) accepts `service` and `signal`. Its [participant map](patterns/facade/participant-map.yaml) maps that entry contract, three specialist Skills, and the caller to the source participants.
2. The deterministic [demo](patterns/facade/sample/scripts/run_demo.py) reads the valid [incident fixture](patterns/facade/sample/fixtures/valid/incident.json), invokes diagnosis, impact assessment, and communication specialists, then returns the stable [expected result](patterns/facade/sample/expected/incident-result.json): `summary`, `impact`, `actions`, and `communication`.

```bash
python3 patterns/facade/sample/scripts/run_demo.py
```

3. The [focused tests](patterns/facade/sample/tests/test_demo.py) verify the exact result contract, specialist call order and context flow, fallback behavior, validation failures, and standard-library-only isolation.

```bash
python3 -m unittest discover -s patterns/facade/sample/tests -v
```

This is constructive evidence for the local mapping. The separate fixed-revision Facade case remains the basis for the `confirmed correspondence` ecosystem claim.

## Quick start and validation

Python 3.10+ is required. From a clean checkout, run these steps at the repository root; the editable install brings in PyYAML before any catalog-dependent test or validator runs.

1. Create and activate an isolated environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install this repository and its declared dependency.

```bash
python -m pip install -e .
```

3. Run the example, focused verification, complete tests, and integrity validator.

```bash
python3 patterns/facade/sample/scripts/run_demo.py
python3 -m unittest discover -s patterns/facade/sample/tests -v
python3 -m unittest tests/test_docs.py -v
python3 -m unittest discover -s tests -v
python3 scripts/validate_repository.py
```

Each sample is standalone, uses Python's standard library, requires no network access or credentials, and can be run from the repository root or its own sample directory as documented locally.

## Pattern-transfer admission protocol

A candidate transfer must satisfy the [full protocol](docs/pattern-transfer-protocol.md) through seven explicit records:

```text
Source intent
Design forces
Participant correspondence
Consequences
Implementation evidence
Focused verification
Misuse discriminator
```

Names, filenames, comments, and structural resemblance alone do not establish transfer. The seven elements must describe one declared Skillware Unit and revision coherently.

## Claim statuses

The [controlled vocabulary](docs/evidence-and-claim-status.md) has these meanings:

| Status | Meaning |
| --- | --- |
| `constructive` | the repository sample demonstrates that the mapping can be built |
| `confirmed correspondence` | fixed-revision source evidence satisfies the participant relation |
| `candidate correspondence` | partial source evidence exists but a participant or behavior is unverified |
| `unsupported` | available evidence contradicts or fails the source pattern contract |
| `not observable` | the required relation cannot be evaluated from available artifacts |

These statuses are descriptive, not a score. They apply to a named claim, relation, unit, and revision; they do not rank patterns, projects, usefulness, or software quality.

## GoF-23 screen

The [human-readable matrix](catalog/gof-23-screening.md) and its [YAML source](catalog/gof-23-screening.yaml) record **23 GoF patterns screened**. Each row preserves the canonical source intent, plausible Skillware carriers, screening result and reasoning, false-positive risk, and whether a detailed sample exists.

The screen is a bounded analytical inventory. Ten GoF rows have detailed implementations in this release; the other thirteen remain screening records. A row does not establish ecosystem frequency, suitability, quality, correspondence, or implementation merely because a plausible carrier is named.

## Repository map

```text
catalog/                 sourced detailed index and GoF-23 screen
docs/                    ontology boundary, paper map, protocol, statuses, limits
patterns/<pattern>/      one flat, independently inspectable pattern record
  definition*.md         English and Chinese definitions
  participant-map.yaml   source-to-Skillware participant correspondence
  correspondence.md      fixed-revision ecosystem evidence and claim boundary
  sample/                root Skill, fixtures, oracle, expected results, tests
  misuse/                close non-example and decisive discriminator
scripts/                 repository integrity validator
tests/                   catalog, documentation, record, and sample contracts
```

Start with the [detailed index](catalog/pattern-index.md), then enter any peer directory under [`patterns/`](patterns/). The flat layout prevents source category from being mistaken for a new taxonomy or implementation ranking.

## Scientific limitations

These artifacts demonstrate bounded constructibility and, where stated, fixed-revision correspondence. They do not establish ecosystem frequency, automatic quality advantage, production reliability, security, usefulness, comparative performance, or cross-Host behavioral equivalence. Deterministic oracles verify declared sample contracts; they do not reproduce model interpretation or validate the Skillware ontology.

The repository does not claim invention of established patterns. Pattern, implementation dimension, mechanism, and lifecycle stage remain separate analytical axes, with no implied ordering. See the [full limitations](docs/limitations.md).

## Citation

Haodi Fan and Zucong Lan. [*Skillware: A Software Ontology and Engineering Lifecycle for Persistent Behavioral Artifacts*](https://arxiv.org/abs/2607.18970). arXiv:2607.18970 [cs.SE], submitted 21 July 2026.

Use [CITATION.cff](CITATION.cff) for formal software and preferred-paper metadata. The [paper map](docs/paper-map.md) provides claim-level paths; authoring revision `1fc1dfd` is recorded there as unlinked provenance.

## Contributing

Contributions should preserve established source provenance, the flat pattern layout, the seven-element admission protocol, controlled statuses, bilingual definitions, a standalone sample, a close misuse case, and focused tests. A new directory is not admitted solely because it carries a familiar pattern name.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the complete admission contract, validation requirements, and contribution license boundary. Participation is governed by the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). This repository remains in release preparation and is not yet public-release ready; CI, publication, and release creation remain pending.

## Licenses

The license boundary is operative by file location. All `patterns/*/sample/**`, `scripts/**`, `tests/**`, `.github/workflows/**`, and `pyproject.toml` are licensed under the [Apache License 2.0](LICENSE-CODE). Definitions, pattern metadata, participant maps, correspondence records, misuse records, catalog files, docs, READMEs, and governance prose are licensed under [Creative Commons Attribution 4.0 International](LICENSE-DOCS).

Canonical license files retain their own texts. Linked third-party artifacts remain under their upstream license and are not relicensed by this repository. See [CONTRIBUTING.md](CONTRIBUTING.md#license-boundary) for the complete boundary.
