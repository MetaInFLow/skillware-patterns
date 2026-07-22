from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
PATTERNS = ROOT / "patterns"

REQUIRED_FILES = (
    "README.md",
    "pattern.yaml",
    "definition.md",
    "definition.zh-CN.md",
    "participant-map.yaml",
    "correspondence.md",
    "sample/SKILL.md",
    "sample/README.md",
    "sample/README.zh-CN.md",
    "sample/skillware.yaml",
    "sample/scripts/run_demo.py",
    "misuse/SKILL.md",
    "misuse/explanation.md",
)

DEFINITION_SECTIONS = (
    "Intent",
    "Forces",
    "Participants",
    "Collaboration",
    "Consequences",
    "Skillware Mapping",
    "Applicability",
    "Non-Applicability",
    "Positive Evidence",
    "Counter-Evidence",
    "False Positives",
    "Open-Source Correspondence",
    "Verification",
    "Limitations",
)


def referenced_paths(value, key=""):
    if isinstance(value, dict):
        for child_key, child_value in value.items():
            yield from referenced_paths(child_value, child_key)
    elif isinstance(value, list):
        if key == "paths" or key.endswith("_paths"):
            yield from value
        else:
            for child in value:
                yield from referenced_paths(child, key)
    elif key == "path" or key.endswith("_path"):
        yield value


class PatternRecordContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows = yaml.safe_load(
            (ROOT / "catalog/pattern-index.yaml").read_text(encoding="utf-8")
        )
        cls.catalog = {row["id"]: row for row in rows}
        cls.materialized = sorted(
            path for path in PATTERNS.iterdir() if path.is_dir()
        )

    def test_every_materialized_directory_is_a_catalog_pattern(self):
        unknown = [
            path.name for path in self.materialized if path.name not in self.catalog
        ]
        self.assertEqual(unknown, [])

    def test_every_materialized_record_has_required_files(self):
        for record in self.materialized:
            for relative_path in REQUIRED_FILES:
                with self.subTest(pattern=record.name, path=relative_path):
                    self.assertTrue((record / relative_path).is_file())

    def test_pattern_metadata_exactly_matches_catalog_row(self):
        for record in self.materialized:
            with self.subTest(pattern=record.name):
                metadata = yaml.safe_load(
                    (record / "pattern.yaml").read_text(encoding="utf-8")
                )
                self.assertEqual(metadata, self.catalog[record.name])

    def test_definitions_have_the_complete_section_contract(self):
        for record in self.materialized:
            for filename in ("definition.md", "definition.zh-CN.md"):
                text = (record / filename).read_text(encoding="utf-8")
                headings = [line for line in text.splitlines() if line.startswith("## ")]
                for section in DEFINITION_SECTIONS:
                    with self.subTest(
                        pattern=record.name, file=filename, section=section
                    ):
                        self.assertTrue(
                            any(
                                heading == f"## {section}"
                                or f"（{section}）" in heading
                                for heading in headings
                            ),
                            f"{filename} missing {section} heading",
                        )

    def test_participant_map_paths_exist_inside_the_record(self):
        for record in self.materialized:
            participant_map = yaml.safe_load(
                (record / "participant-map.yaml").read_text(encoding="utf-8")
            )
            paths = list(referenced_paths(participant_map))
            self.assertTrue(paths, f"{record.name} has no participant paths")
            for relative_path in paths:
                with self.subTest(pattern=record.name, path=relative_path):
                    resolved = (record / relative_path).resolve()
                    resolved.relative_to(record.resolve())
                    self.assertTrue(resolved.exists())


if __name__ == "__main__":
    unittest.main()
