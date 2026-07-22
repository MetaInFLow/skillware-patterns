# Contributing to Skillware Patterns

Thank you for improving this executable supplement. Contributions must preserve the repository's evidence boundaries, source attribution, bilingual parity, and deterministic validation. Participation is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).

## Contribution Types

Focused corrections, stronger evidence, documentation improvements, sample hardening, and protocol-complete pattern records are welcome. Keep changes reviewable and do not combine unrelated cleanup with a pattern or evidence contribution.

The current scope of 10 GoF implementations and 2 implementations from other established traditions is neither an automatic admission cap nor a claim that this repository introduces new patterns. Scope may change only through evidence-based review; a familiar name or useful mechanism does not receive automatic admission.

## Pattern Admission Requirements

A proposed pattern record must meet every requirement below:

1. Identify a canonical, established source or tradition and record its source intent, category, provenance, and terminology without claiming ownership or invention.
2. Apply the [seven-element pattern-transfer protocol](docs/pattern-transfer-protocol.md) in full:

```text
Source intent
Design forces
Participant correspondence
Consequences
Implementation evidence
Focused verification
Misuse discriminator
```

3. Provide an exact participant map from source-pattern participants and relations to named Skillware artifacts. Labels, filenames, or approximate structural resemblance are insufficient.
4. Include both a runnable positive case and a close negative or misuse case whose discriminator explains precisely which required relation is absent.
5. Supply a standalone sample that runs from its own sample directory with Python 3.10+ and the Python standard library only. It must require no network access, credentials, repository-root imports, or undeclared dependencies.
6. Provide pinned public correspondence evidence at an immutable revision and assign each ecosystem claim a controlled claim status from the [evidence vocabulary](docs/evidence-and-claim-status.md). Constructive local evidence and ecosystem correspondence remain separate claims.
7. Maintain bilingual parity for English and Simplified Chinese definitions and sample instructions. Neither language may omit a material contract, limitation, command, or claim boundary.
8. Add focused tests for the positive and negative cases, then run the full repository test suite and validator before requesting review.
9. Include this declaration in the proposal or pull request: **This contribution does not rename an engineering mechanism as a pattern.**

Changes to an existing record must preserve the same requirements wherever the change affects the pattern mapping, evidence, sample behavior, or public claims.

## Validation

From an installed checkout, run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_repository.py
```

Run the affected sample's local tests from its sample directory as well. Commit generated expected outputs only when they are deterministic, reviewed, and asserted by tests.

## License Boundary

By contributing, you agree that all `patterns/*/sample/**`, `scripts/**`, `tests/**`, `.github/workflows/**`, and `pyproject.toml` are licensed under the [Apache License 2.0](LICENSE-CODE).

Definitions, pattern metadata, participant maps, correspondence records, misuse records, catalog files, docs, READMEs, and governance prose are licensed under [Creative Commons Attribution 4.0 International](LICENSE-DOCS).

Canonical license files retain their own license texts. Linked third-party artifacts remain under their upstream licenses. A link, citation, or pinned revision does not relicense upstream material, and contributors must not copy third-party content unless its license permits inclusion under the applicable repository boundary.
