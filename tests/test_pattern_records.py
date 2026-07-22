from pathlib import Path
import re
import unittest
from urllib.parse import urlparse

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
                    self.assertTrue(resolved.is_file())

    def test_facade_has_publicly_verifiable_local_evidence(self):
        record = PATTERNS / "facade"
        evidence = record / "evidence/superpowers-frozen-case.md"
        correspondence = (record / "correspondence.md").read_text(encoding="utf-8")

        self.assertTrue(evidence.is_file())
        self.assertIn(
            "[frozen evidence](evidence/superpowers-frozen-case.md)",
            correspondence,
        )
        local_links = [
            target
            for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", correspondence)
            if "://" not in target
        ]
        for target in local_links:
            with self.subTest(target=target):
                self.assertTrue((record / target).is_file())

        evidence_text = evidence.read_text(encoding="utf-8")
        for required in (
            "896224c4b1879920ab573417e68fd51d2ccc9072",
            "skills/using-superpowers/SKILL.md",
            "hooks/session-start",
            "confirmed correspondence",
            "Counterevidence and limits",
        ):
            with self.subTest(required=required):
                self.assertIn(required, evidence_text)

    def test_facade_public_record_has_no_private_research_links(self):
        record = PATTERNS / "facade"
        for path in record.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".yaml", ".py", ".json"}:
                with self.subTest(path=path.relative_to(record)):
                    text = path.read_text(encoding="utf-8")
                    self.assertNotIn("github.com/MetaInFLow/skillware", text)

    def test_facade_separates_gof_participants_from_unobserved_runtime_context(self):
        participant_map = yaml.safe_load(
            (PATTERNS / "facade/participant-map.yaml").read_text(encoding="utf-8")
        )

        self.assertEqual(
            set(participant_map["participants"]), {"Client", "Facade", "Subsystem"}
        )
        context = participant_map["execution_context"]
        self.assertEqual(set(context), {"Agent Host", "Agent Runtime"})
        for role in context.values():
            self.assertEqual(role["evidence_status"], "not observable")
            self.assertNotIn("path", role)
            self.assertNotIn("evidence_path", role)

    def test_facade_chinese_definition_uses_human_triage_term(self):
        text = (PATTERNS / "facade/definition.zh-CN.md").read_text(encoding="utf-8")

        self.assertIn("人工分诊回退", text)
        self.assertNotIn("人工作业回退", text)

    def test_adapter_has_publicly_verifiable_local_evidence(self):
        record = PATTERNS / "adapter"
        evidence = record / "evidence/gstack-frozen-case.md"
        correspondence = (record / "correspondence.md").read_text(encoding="utf-8")

        self.assertTrue(evidence.is_file())
        self.assertIn(
            "[frozen evidence](evidence/gstack-frozen-case.md)",
            correspondence,
        )
        local_links = [
            target
            for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", correspondence)
            if "://" not in target
        ]
        for target in local_links:
            with self.subTest(target=target):
                self.assertTrue((record / target).is_file())

        evidence_text = evidence.read_text(encoding="utf-8")
        for required in (
            "11de390be1be6849eb9a15f91ff4922dd16c589a",
            "SKILL.md.tmpl",
            "scripts/gen-skill-docs.ts",
            "hosts/claude.ts",
            "hosts/codex.ts",
            "test/codex-e2e.test.ts",
            "**Claim status:** confirmed correspondence",
            "canonical Adaptee template",
            "generated `SKILL.md` surface",
            "Strong correspondence. Parity requires runtime tests.",
            "Runtime-parity limitation",
        ):
            with self.subTest(required=required):
                self.assertIn(required, evidence_text)

        self.assertIn("**Status:** confirmed correspondence", correspondence)
        self.assertIn(
            "**Paper wording:** Strong correspondence. Parity requires runtime tests.",
            correspondence,
        )
        self.assertNotIn("**Status:** strong correspondence", correspondence)
        self.assertNotIn("**Claim status:** strong correspondence", evidence_text)

        for filename in ("definition.md", "definition.zh-CN.md"):
            with self.subTest(filename=filename):
                definition = (record / filename).read_text(encoding="utf-8")
                self.assertIn("confirmed correspondence", definition)
                self.assertIn(
                    "Strong correspondence. Parity requires runtime tests.",
                    definition,
                )

    def test_adapter_public_record_has_no_private_research_links(self):
        record = PATTERNS / "adapter"
        for path in record.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".yaml", ".py", ".json"}:
                with self.subTest(path=path.relative_to(record)):
                    text = path.read_text(encoding="utf-8")
                    self.assertNotIn("skillware-github", text)
                    self.assertNotIn("github.com/MetaInFLow/skillware", text)

    def test_adapter_gstack_evidence_urls_are_structurally_pinned(self):
        evidence = (
            PATTERNS / "adapter/evidence/gstack-frozen-case.md"
        ).read_text(encoding="utf-8")
        urls = re.findall(r"https://github\.com/[^)\s]+", evidence)
        expected_paths = {
            "SKILL.md.tmpl",
            "SKILL.md",
            "scripts/gen-skill-docs.ts",
            "hosts/claude.ts",
            "hosts/codex.ts",
            "hosts/index.ts",
            "setup",
            "test/codex-e2e.test.ts",
        }
        pinned_paths = set()

        for url in urls:
            parsed = urlparse(url)
            parts = parsed.path.strip("/").split("/")
            if len(parts) < 5 or parts[2] not in {"blob", "tree"}:
                continue
            owner, repository, _, revision = parts[:4]
            upstream_path = "/".join(parts[4:])
            with self.subTest(url=url):
                self.assertEqual(parsed.scheme, "https")
                self.assertEqual(parsed.netloc, "github.com")
                self.assertEqual((owner, repository), ("garrytan", "gstack"))
                self.assertRegex(revision, r"^[0-9a-f]{40}$")
                self.assertEqual(
                    revision, "11de390be1be6849eb9a15f91ff4922dd16c589a"
                )
                self.assertIn(upstream_path, expected_paths)
            pinned_paths.add(upstream_path)

        self.assertEqual(pinned_paths, expected_paths)

    def test_adapter_separates_gof_participants_from_execution_context(self):
        participant_map = yaml.safe_load(
            (PATTERNS / "adapter/participant-map.yaml").read_text(encoding="utf-8")
        )

        self.assertEqual(
            set(participant_map["participants"]),
            {"Client", "Target", "Adaptee", "Adapter"},
        )
        self.assertEqual(
            participant_map["participants"]["Adaptee"]["path"],
            "sample/SKILL.md",
        )
        adapter_ids = {
            item["id"]
            for item in participant_map["participants"]["Adapter"]["implementations"]
        }
        self.assertEqual(adapter_ids, {"github", "jira", "linear"})

        context = participant_map["execution_context"]
        self.assertEqual(set(context), {"Agent Host", "Agent Runtime"})
        for role in context.values():
            self.assertEqual(role["evidence_status"], "not observable")
            self.assertNotIn("path", role)
            self.assertNotIn("evidence_path", role)

    def test_observer_has_publicly_verifiable_local_candidate_evidence(self):
        record = PATTERNS / "observer"
        evidence = record / "evidence/ecc-frozen-case.md"
        correspondence = (record / "correspondence.md").read_text(encoding="utf-8")

        self.assertTrue(evidence.is_file())
        self.assertIn("[frozen evidence](evidence/ecc-frozen-case.md)", correspondence)
        self.assertIn("**Status:** candidate correspondence", correspondence)
        self.assertNotIn("**Status:** confirmed correspondence", correspondence)

        evidence_text = evidence.read_text(encoding="utf-8")
        for required in (
            "2bc924faf2f8e893bfe0af86b1931283693c30ae",
            "hooks/hooks.json",
            "scripts/hooks/run-with-flags.js",
            "tests/hooks/hooks.test.js",
            "skills/continuous-learning-v2/SKILL.md",
            "skills/continuous-learning-v2/hooks/observe.sh",
            "skills/continuous-learning-v2/config.json",
            "**Claim status:** candidate correspondence",
            "GoF registration, unregistration, and deterministic delivery",
        ):
            with self.subTest(required=required):
                self.assertIn(required, evidence_text)
        self.assertNotIn("**Claim status:** confirmed correspondence", evidence_text)

    def test_observer_ecc_evidence_urls_are_structurally_pinned(self):
        evidence = (PATTERNS / "observer/evidence/ecc-frozen-case.md").read_text(
            encoding="utf-8"
        )
        urls = re.findall(r"https://github\.com/[^)\s]+", evidence)
        expected_paths = {
            "hooks/hooks.json",
            "scripts/hooks/run-with-flags.js",
            "tests/hooks/hooks.test.js",
            "skills/continuous-learning-v2/SKILL.md",
            "skills/continuous-learning-v2/hooks/observe.sh",
            "skills/continuous-learning-v2/config.json",
        }
        pinned_paths = set()

        for url in urls:
            parsed = urlparse(url)
            parts = parsed.path.strip("/").split("/")
            if len(parts) < 5 or parts[2] not in {"blob", "tree"}:
                continue
            owner, repository, _, revision = parts[:4]
            upstream_path = "/".join(parts[4:])
            with self.subTest(url=url):
                self.assertEqual(parsed.scheme, "https")
                self.assertEqual(parsed.netloc, "github.com")
                self.assertEqual((owner, repository), ("affaan-m", "ECC"))
                self.assertRegex(revision, r"^[0-9a-f]{40}$")
                self.assertEqual(
                    revision, "2bc924faf2f8e893bfe0af86b1931283693c30ae"
                )
                self.assertIn(upstream_path, expected_paths)
            pinned_paths.add(upstream_path)

        self.assertEqual(pinned_paths, expected_paths)

    def test_observer_separates_gof_participants_from_execution_context(self):
        participant_map = yaml.safe_load(
            (PATTERNS / "observer/participant-map.yaml").read_text(encoding="utf-8")
        )

        self.assertEqual(
            set(participant_map["participants"]),
            {"Subject", "Observer", "ConcreteSubject", "ConcreteObserver"},
        )
        observer_ids = {
            item["id"]
            for item in participant_map["participants"]["ConcreteObserver"][
                "implementations"
            ]
        }
        self.assertEqual(observer_ids, {"audit", "changelog", "team-notification"})

        context = participant_map["execution_context"]
        self.assertEqual(set(context), {"Agent Host", "Agent Runtime"})
        for role in context.values():
            self.assertEqual(role["evidence_status"], "not observable")
            self.assertNotIn("path", role)
            self.assertNotIn("evidence_path", role)

    def test_observer_contract_declares_complete_notification_policy(self):
        contract = yaml.safe_load(
            (PATTERNS / "observer/sample/skillware.yaml").read_text(encoding="utf-8")
        )

        self.assertEqual(contract["event"]["type"], "release.published.v1")
        self.assertEqual(contract["observer_contract"], "release-observer-v1")
        self.assertEqual(contract["subscription_operations"], ["register", "unregister"])
        self.assertEqual(
            [item["id"] for item in contract["observers"]],
            ["audit", "changelog", "team-notification"],
        )
        self.assertEqual(contract["delivery"]["order"], "registration-order")
        self.assertTrue(contract["delivery"]["per_observer_accounting"])
        self.assertTrue(contract["delivery"]["failure_isolation"])
        self.assertEqual(contract["delivery"]["reentry"], "rejected")

    def test_observer_public_record_has_no_private_research_links(self):
        record = PATTERNS / "observer"
        for path in record.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".yaml", ".py", ".json"}:
                with self.subTest(path=path.relative_to(record)):
                    text = path.read_text(encoding="utf-8")
                    self.assertNotIn("skillware-github", text)
                    self.assertNotIn("github.com/MetaInFLow/skillware", text)


if __name__ == "__main__":
    unittest.main()
