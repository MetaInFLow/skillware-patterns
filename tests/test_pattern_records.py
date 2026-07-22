import importlib.util
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

    def test_sample_display_metadata_matches_catalog_scenario(self):
        for record in self.materialized:
            with self.subTest(pattern=record.name):
                metadata = yaml.safe_load(
                    (record / "pattern.yaml").read_text(encoding="utf-8")
                )
                sample = yaml.safe_load(
                    (record / "sample/skillware.yaml").read_text(encoding="utf-8")
                )
                self.assertEqual(sample["name"], metadata["scenario"])
                self.assertEqual(sample["name_zh"], metadata["scenario_zh"])
                self.assertTrue(
                    (record / "sample/README.md")
                    .read_text(encoding="utf-8")
                    .startswith(f"# {metadata['scenario']}\n")
                )
                self.assertTrue(
                    (record / "sample/README.zh-CN.md")
                    .read_text(encoding="utf-8")
                    .startswith(f"# {metadata['scenario_zh']}\n")
                )

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

    def test_state_separates_gof_participants_from_execution_context(self):
        participant_map = yaml.safe_load(
            (PATTERNS / "state/participant-map.yaml").read_text(encoding="utf-8")
        )

        self.assertEqual(
            set(participant_map["participants"]),
            {"Context", "State", "ConcreteState"},
        )
        concrete_state_ids = {
            item["id"]
            for item in participant_map["participants"]["ConcreteState"][
                "implementations"
            ]
        }
        self.assertEqual(
            concrete_state_ids, {"draft", "verified", "approved", "activated"}
        )

        context = participant_map["execution_context"]
        self.assertEqual(set(context), {"Agent Host", "Agent Runtime"})
        for role in context.values():
            self.assertEqual(role["evidence_status"], "not observable")
            self.assertNotIn("path", role)
            self.assertNotIn("evidence_path", role)

    def test_state_contract_declares_owned_transitions_and_recovery(self):
        contract = yaml.safe_load(
            (PATTERNS / "state/sample/skillware.yaml").read_text(encoding="utf-8")
        )

        self.assertEqual(contract["state_contract"], "vendor-onboarding-state-v1")
        self.assertEqual(contract["operation"], "handle-action")
        self.assertEqual(contract["transition_ownership"], "concrete-state")
        self.assertEqual(
            [
                (item["from"], item["action"], item["to"])
                for item in contract["transitions"]
            ],
            [
                ("draft", "verify", "verified"),
                ("verified", "approve", "approved"),
                ("approved", "activate", "activated"),
            ],
        )
        self.assertEqual(contract["persistence"]["format"], "versioned-json")
        self.assertEqual(contract["persistence"]["write"], "atomic-replace")
        self.assertEqual(contract["recovery"], "reload-before-action")
        self.assertEqual(contract["illegal_transition"], "reject-before-write")

    def test_state_has_publicly_verifiable_local_candidate_evidence(self):
        correspondence = (PATTERNS / "state/correspondence.md").read_text(
            encoding="utf-8"
        )
        evidence = PATTERNS / "state/evidence/openmontage-frozen-case.md"

        self.assertTrue(evidence.is_file())
        self.assertIn(
            "[frozen evidence](evidence/openmontage-frozen-case.md)",
            correspondence,
        )
        self.assertIn("**Status:** candidate correspondence", correspondence)
        self.assertNotIn("confirmed correspondence", correspondence)

        evidence_text = evidence.read_text(encoding="utf-8")
        for required in (
            "db91727598d08d40919d7d68a47864a5467bd448",
            "AGENT_GUIDE.md",
            "lib/checkpoint.py",
            "skills/meta/checkpoint-protocol.md",
            "schemas/checkpoints/checkpoint.schema.json",
            "**Claim status:** candidate correspondence",
            "does not establish the complete GoF State participant relation",
        ):
            with self.subTest(required=required):
                self.assertIn(required, evidence_text)
        self.assertNotIn("**Claim status:** confirmed correspondence", evidence_text)

    def test_state_openmontage_evidence_urls_are_structurally_pinned(self):
        evidence = (
            PATTERNS / "state/evidence/openmontage-frozen-case.md"
        ).read_text(encoding="utf-8")
        urls = re.findall(r"https://github\.com/[^)\s]+", evidence)
        expected_paths = {
            "AGENT_GUIDE.md",
            "lib/checkpoint.py",
            "skills/meta/checkpoint-protocol.md",
            "schemas/checkpoints/checkpoint.schema.json",
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
                self.assertEqual((owner, repository), ("calesthio", "OpenMontage"))
                self.assertEqual(
                    revision, "db91727598d08d40919d7d68a47864a5467bd448"
                )
                self.assertIn(upstream_path, expected_paths)
            pinned_paths.add(upstream_path)

        self.assertEqual(pinned_paths, expected_paths)

    def test_state_public_record_has_no_private_research_links(self):
        record = PATTERNS / "state"
        for path in record.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".yaml", ".py", ".json"}:
                with self.subTest(path=path.relative_to(record)):
                    text = path.read_text(encoding="utf-8")
                    self.assertNotIn("skillware-github", text)
                    self.assertNotIn("github.com/MetaInFLow/skillware", text)

    def test_strategy_separates_gof_participants_from_execution_context(self):
        participant_map = yaml.safe_load(
            (PATTERNS / "strategy/participant-map.yaml").read_text(encoding="utf-8")
        )

        self.assertEqual(
            set(participant_map["participants"]),
            {"Context", "Strategy", "ConcreteStrategy"},
        )
        concrete_ids = {
            item["id"]
            for item in participant_map["participants"]["ConcreteStrategy"][
                "implementations"
            ]
        }
        self.assertEqual(concrete_ids, {"fast-scan", "deep-review"})

        context = participant_map["execution_context"]
        self.assertEqual(set(context), {"Agent Host", "Agent Runtime"})
        for role in context.values():
            self.assertEqual(role["evidence_status"], "not observable")
            self.assertNotIn("path", role)
            self.assertNotIn("evidence_path", role)

    def test_strategy_contract_declares_interchangeability_and_selection(self):
        contract = yaml.safe_load(
            (PATTERNS / "strategy/sample/skillware.yaml").read_text(encoding="utf-8")
        )

        self.assertEqual(contract["strategy_contract"], "risk-aware-code-review-v1")
        self.assertEqual(
            contract["request_fields"],
            ["schema", "review_id", "security_sensitive", "files"],
        )
        self.assertEqual(
            contract["result_fields"],
            [
                "schema",
                "review_id",
                "strategy",
                "reviewed_files",
                "findings",
                "summary",
            ],
        )
        self.assertEqual(
            [item["id"] for item in contract["strategies"]],
            ["fast-scan", "deep-review"],
        )
        self.assertTrue(
            all(
                item["implements"] == "risk-aware-code-review-v1"
                for item in contract["strategies"]
            )
        )
        self.assertEqual(
            contract["selection"],
            {
                "security_sensitive": "deep-review",
                "file_count_at_least": 4,
                "threshold_strategy": "deep-review",
                "otherwise": "fast-scan",
            },
        )
        self.assertEqual(
            contract["compatibility_api"],
            {
                "operation": "review",
                "request_fields": ["files", "security_sensitive"],
                "deep_when": {
                    "security_sensitive": True,
                    "file_count_greater_than": 5,
                },
                "result_fields": ["strategy", "findings", "confidence"],
            },
        )

    def test_strategy_has_publicly_verifiable_local_candidate_evidence(self):
        correspondence = (PATTERNS / "strategy/correspondence.md").read_text(
            encoding="utf-8"
        )
        evidence = PATTERNS / "strategy/evidence/ui-ux-pro-max-frozen-case.md"

        self.assertTrue(evidence.is_file())
        self.assertIn(
            "[frozen evidence](evidence/ui-ux-pro-max-frozen-case.md)",
            correspondence,
        )
        self.assertIn("**Status:** candidate correspondence", correspondence)
        self.assertNotIn("**Status:** confirmed correspondence", correspondence)

        evidence_text = evidence.read_text(encoding="utf-8")
        for required in (
            "8a81ed60272d21d4b8808f7308d49a0b1b000555",
            ".claude/skills/ui-ux-pro-max/SKILL.md",
            ".claude/skills/ui-ux-pro-max/scripts/search.py",
            ".claude/skills/ui-ux-pro-max/scripts/core.py",
            ".claude/skills/ui-ux-pro-max/scripts/design_system.py",
            "**Claim status:** candidate correspondence",
            "does not establish the complete GoF Strategy participant relation",
            "incompatible output shapes",
        ):
            with self.subTest(required=required):
                self.assertIn(required, evidence_text)
        self.assertNotIn("**Claim status:** confirmed correspondence", evidence_text)

    def test_strategy_evidence_urls_are_structurally_pinned(self):
        evidence = (
            PATTERNS / "strategy/evidence/ui-ux-pro-max-frozen-case.md"
        ).read_text(encoding="utf-8")
        urls = re.findall(r"https://github\.com/[^)\s]+", evidence)
        expected_paths = {
            ".claude/skills/ui-ux-pro-max/SKILL.md",
            ".claude/skills/ui-ux-pro-max/scripts/search.py",
            ".claude/skills/ui-ux-pro-max/scripts/core.py",
            ".claude/skills/ui-ux-pro-max/scripts/design_system.py",
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
                self.assertEqual(
                    (owner, repository),
                    ("nextlevelbuilder", "ui-ux-pro-max-skill"),
                )
                self.assertEqual(
                    revision, "8a81ed60272d21d4b8808f7308d49a0b1b000555"
                )
                self.assertIn(upstream_path, expected_paths)
            pinned_paths.add(upstream_path)

        self.assertEqual(pinned_paths, expected_paths)

    def test_strategy_public_record_has_no_private_research_links(self):
        record = PATTERNS / "strategy"
        for path in record.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".yaml", ".py", ".json"}:
                with self.subTest(path=path.relative_to(record)):
                    text = path.read_text(encoding="utf-8")
                    self.assertNotIn("skillware-github", text)
                    self.assertNotIn("github.com/MetaInFLow/skillware", text)

    def test_decorator_separates_gof_participants_from_execution_context(self):
        participant_map = yaml.safe_load(
            (PATTERNS / "decorator/participant-map.yaml").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            set(participant_map["participants"]),
            {"Component", "ConcreteComponent", "Decorator", "ConcreteDecorator"},
        )
        decorator_ids = {
            item["id"]
            for item in participant_map["participants"]["ConcreteDecorator"][
                "implementations"
            ]
        }
        self.assertEqual(
            decorator_ids,
            {"privacy-check", "citation-check", "compliance-check"},
        )

        context = participant_map["execution_context"]
        self.assertEqual(set(context), {"Agent Host", "Agent Runtime"})
        for role in context.values():
            self.assertEqual(role["evidence_status"], "not observable")
            self.assertNotIn("path", role)
            self.assertNotIn("evidence_path", role)

    def test_template_method_separates_roles_and_declares_hardened_dispatch(self):
        participant_map = yaml.safe_load(
            (PATTERNS / "template-method/participant-map.yaml").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            set(participant_map["participants"]),
            {"AbstractClass", "ConcreteClass"},
        )
        context = participant_map["execution_context"]
        self.assertEqual(set(context), {"Agent Host", "Agent Runtime"})
        for role in context.values():
            self.assertEqual(role["evidence_status"], "not observable")
            self.assertNotIn("path", role)
            self.assertNotIn("evidence_path", role)

        contract = yaml.safe_load(
            (PATTERNS / "template-method/sample/skillware.yaml").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            contract["abstract_class"]["template_method"]["order"],
            [
                "extract-requirements",
                "analyze-gaps",
                "apply-domain-hook",
                "draft-response",
                "quality-check",
            ],
        )
        self.assertEqual(contract["hook_binding"], "staticmethod")
        self.assertEqual(
            contract["template_dispatch"],
            "explicit-abstract-class-implementation",
        )

    def test_template_method_public_api_ignores_mro_run_bypass(self):
        demo_path = PATTERNS / "template-method/sample/scripts/run_demo.py"
        spec = importlib.util.spec_from_file_location(
            "root_template_method_demo", demo_path
        )
        demo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(demo)
        bypass_calls = []

        class BypassMixin:
            def run(self, request):
                bypass_calls.append(request)
                return {"domain": "healthcare", "stages": ["quality-check"]}

        class BypassHealthcare(BypassMixin, demo.RfpResponseTemplate):
            domain = "healthcare"

            @staticmethod
            def apply_domain_hook(hook_request):
                return demo.healthcare_domain_hook(hook_request)

        result = demo.run_template(
            BypassHealthcare,
            demo.default_request("healthcare"),
        )

        self.assertEqual(bypass_calls, [])
        self.assertEqual(result["stages"], list(demo.REQUIRED_STAGES))

    def test_template_method_evidence_urls_are_exact_and_pinned(self):
        evidence = (
            PATTERNS / "template-method/evidence/superpowers-frozen-case.md"
        ).read_text(encoding="utf-8")
        urls = re.findall(r"https://github\.com/[^)\s]+", evidence)
        expected_paths = {
            "skills/brainstorming/SKILL.md",
            "skills/test-driven-development/SKILL.md",
        }
        pinned_paths = set()

        for url in urls:
            parsed = urlparse(url)
            parts = parsed.path.strip("/").split("/")
            if len(parts) < 5 or parts[2] != "blob":
                continue
            owner, repository, _, revision = parts[:4]
            upstream_path = "/".join(parts[4:])
            with self.subTest(url=url):
                self.assertEqual((owner, repository), ("obra", "superpowers"))
                self.assertEqual(
                    revision, "896224c4b1879920ab573417e68fd51d2ccc9072"
                )
                self.assertIn(upstream_path, expected_paths)
            pinned_paths.add(upstream_path)

        self.assertEqual(pinned_paths, expected_paths)
        self.assertIn("**Claim status:** candidate correspondence", evidence)
        self.assertIn("ConcreteClass substitution", evidence)
        self.assertIn("Agent Runtime behavior is unverified", evidence)

    def test_template_method_chinese_forces_cover_all_validation_boundaries(self):
        chinese = (PATTERNS / "template-method/definition.zh-CN.md").read_text(
            encoding="utf-8"
        )
        forces = chinese.split("## 作用力（Forces）", 1)[1].split(
            "## 参与者（Participants）", 1
        )[0]
        self.assertIn("输入、钩子输出和最终结果", forces)
        self.assertIn("确定性", forces)

    def test_decorator_contract_declares_preservation_and_order(self):
        contract = yaml.safe_load(
            (PATTERNS / "decorator/sample/skillware.yaml").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(contract["component_contract"], "contract-review-v1")
        self.assertEqual(contract["operation"], "review")
        self.assertEqual(contract["request_fields"], ["text"])
        self.assertEqual(contract["result_fields"], ["summary", "findings"])
        self.assertEqual(contract["finding_fields"], ["type", "message"])
        self.assertEqual(contract["base_component"]["id"], "base-contract-review")
        self.assertEqual(
            [item["id"] for item in contract["decorators"]],
            ["privacy-check", "citation-check", "compliance-check"],
        )
        self.assertTrue(
            all(
                item["implements"] == "contract-review-v1"
                for item in contract["decorators"]
            )
        )
        self.assertEqual(
            contract["default_composition"],
            {
                "wrapped_component": "base-contract-review",
                "inside_to_outside": ["privacy-check", "citation-check"],
                "finding_order": ["privacy", "citation"],
            },
        )
        self.assertEqual(contract["mutation_policy"], "copy-at-every-boundary")
        self.assertEqual(contract["failure_policy"], "propagate-unchanged")
        self.assertEqual(contract["finding_identity"], ["type", "message"])
        self.assertEqual(
            contract["duplicate_identity_policy"],
            "reject-component-duplicates-suppress-wrapper-duplicate",
        )
        self.assertEqual(contract["finding_count_limit"], "none")
        self.assertEqual(contract["maximum_nesting_depth"], 64)

    def test_decorator_has_publicly_verifiable_local_candidate_evidence(self):
        correspondence = (PATTERNS / "decorator/correspondence.md").read_text(
            encoding="utf-8"
        )
        evidence = PATTERNS / "decorator/evidence/caveman-frozen-case.md"

        self.assertTrue(evidence.is_file())
        self.assertIn(
            "[frozen evidence](evidence/caveman-frozen-case.md)",
            correspondence,
        )
        self.assertIn("**Status:** candidate correspondence", correspondence)
        self.assertNotIn("**Status:** confirmed correspondence", correspondence)

        evidence_text = evidence.read_text(encoding="utf-8")
        for required in (
            "25d22f864ad68cc447a4cb93aefde918aa4aec9f",
            "src/hooks/caveman-activate.js",
            "skills/caveman/SKILL.md",
            "**Claim status:** candidate correspondence",
            "preserving the Host interaction surface",
            "does not establish complete GoF Component/Decorator contract equivalence",
            "runtime behavior remains unverified",
        ):
            with self.subTest(required=required):
                self.assertIn(required, evidence_text)
        self.assertNotIn("**Claim status:** confirmed correspondence", evidence_text)

    def test_decorator_caveman_evidence_urls_are_structurally_pinned(self):
        evidence = (
            PATTERNS / "decorator/evidence/caveman-frozen-case.md"
        ).read_text(encoding="utf-8")
        urls = re.findall(r"https://github\.com/[^)\s]+", evidence)
        expected_paths = {
            "src/hooks/caveman-activate.js",
            "skills/caveman/SKILL.md",
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
                self.assertEqual((owner, repository), ("JuliusBrussee", "caveman"))
                self.assertEqual(
                    revision, "25d22f864ad68cc447a4cb93aefde918aa4aec9f"
                )
                self.assertIn(upstream_path, expected_paths)
            pinned_paths.add(upstream_path)

        self.assertEqual(pinned_paths, expected_paths)

    def test_decorator_definitions_preserve_source_ontology_and_limits(self):
        english = (PATTERNS / "decorator/definition.md").read_text(
            encoding="utf-8"
        )
        chinese = (PATTERNS / "decorator/definition.zh-CN.md").read_text(
            encoding="utf-8"
        )

        for text in (english, chinese):
            self.assertIn("Design Patterns", text)
            self.assertIn("1994", text)
            self.assertIn("Gang of Four", text)
            self.assertIn("Behavioral Source", text)
            self.assertIn("Skill Artifact", text)
        self.assertIn(
            "Behavioral Source defines and informs the root and child Skill Artifacts",
            english,
        )
        self.assertNotIn("Skills are the behavioral source", english)
        self.assertIn("装饰器之间发现冲突的解决策略不在本契约范围内", chinese)

    def test_decorator_public_record_has_no_private_research_links(self):
        record = PATTERNS / "decorator"
        for path in record.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".yaml", ".py", ".json"}:
                with self.subTest(path=path.relative_to(record)):
                    text = path.read_text(encoding="utf-8")
                    self.assertNotIn("skillware-github", text)
                    self.assertNotIn("github.com/MetaInFLow/skillware", text)

    def test_memento_roles_contract_evidence_and_chinese_parity(self):
        record = PATTERNS / "memento"
        participant_map = yaml.safe_load(
            (record / "participant-map.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(
            set(participant_map["participants"]),
            {"Originator", "Memento", "Caretaker"},
        )
        context = participant_map["execution_context"]
        self.assertEqual(set(context), {"Agent Host", "Agent Runtime"})
        for role in context.values():
            self.assertEqual(role["evidence_status"], "not observable")
            self.assertNotIn("path", role)
            self.assertNotIn("evidence_path", role)

        contract = yaml.safe_load(
            (record / "sample/skillware.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(contract["memento_contract"], "configuration-memento-v1")
        self.assertEqual(contract["capture"], "exact-bytes-plus-metadata")
        self.assertEqual(
            contract["preparation"],
            "originator-private-immutable-payload",
        )
        self.assertEqual(
            contract["prepared_token"],
            "opaque-originator-issued-one-use",
        )
        self.assertEqual(contract["restore"], "atomic-replace")
        self.assertEqual(contract["successful_commit"], "discard-without-restore")
        self.assertEqual(
            contract["retirement_integrity"],
            "checksum-owner-active-identity",
        )
        self.assertEqual(
            contract["rollback_restore_admission"],
            "wrap-and-preserve-original-error",
        )

        evidence = (record / "evidence/skillopt-frozen-case.md").read_text(
            encoding="utf-8"
        )
        urls = re.findall(r"https://github\.com/[^)\s]+", evidence)
        self.assertEqual(len(urls), 1)
        parsed = urlparse(urls[0])
        parts = parsed.path.strip("/").split("/")
        self.assertEqual(parsed.scheme, "https")
        self.assertEqual(parsed.netloc, "github.com")
        self.assertEqual(parts[:4], [
            "microsoft",
            "SkillOpt",
            "blob",
            "b860a5cf88ce75e2bd02ca981ac21fb28cffba83",
        ])
        self.assertEqual("/".join(parts[4:]), "skillopt_sleep/staging.py")
        self.assertIn("**Claim status:** candidate correspondence", evidence)
        self.assertIn("no owned restore path", evidence)

        chinese = (record / "definition.zh-CN.md").read_text(encoding="utf-8")
        for required in (
            "完整快照会增加内存消耗",
            "不提供并发控制、授权、加密或持久历史",
            "恢复失败时，检查点保持活跃",
            "报告迁移与恢复两个错误",
            "确定性 oracle 不解释自然语言 Skill",
            "同目录临时文件",
            "原子替换并不保证每种文件系统都具有相同的崩溃持久性",
        ):
            with self.subTest(required=required):
                self.assertIn(required, chinese)

        for path in record.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".yaml", ".py", ".json"}:
                with self.subTest(path=path.relative_to(record)):
                    self.assertNotIn("EvoZeus", path.read_text(encoding="utf-8"))

    def test_mediator_roles_contract_evidence_and_chinese_parity(self):
        record = PATTERNS / "mediator"
        participant_map = yaml.safe_load(
            (record / "participant-map.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(
            set(participant_map["participants"]),
            {"Mediator", "ConcreteMediator", "Colleague"},
        )
        context = participant_map["execution_context"]
        self.assertEqual(set(context), {"Agent Host", "Agent Runtime"})
        for role in context.values():
            self.assertEqual(role["evidence_status"], "not observable")
            self.assertNotIn("path", role)
            self.assertNotIn("evidence_path", role)

        contract = yaml.safe_load(
            (record / "sample/skillware.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(contract["mediator_contract"], "deployment-readiness-v1")
        self.assertEqual(contract["communication_path"], "participants->mediator->release")
        self.assertEqual(
            contract["participant_order"],
            ["build", "security", "docs", "approval"],
        )
        self.assertEqual(contract["status_values"], ["pass", "fail"])
        self.assertEqual(contract["release_policy"], "all-participants-pass")
        self.assertEqual(contract["specialist_failure_policy"], "isolate-and-fail-closed")
        self.assertEqual(contract["mutation_policy"], "copy-statuses")

        evidence = (
            record / "evidence/financial-services-frozen-case.md"
        ).read_text(encoding="utf-8")
        urls = re.findall(r"https://github\.com/[^)\s]+", evidence)
        expected_paths = {
            "managed-agent-cookbooks/gl-reconciler/agent.yaml",
            "managed-agent-cookbooks/gl-reconciler/subagents/reader.yaml",
            "managed-agent-cookbooks/gl-reconciler/subagents/critic.yaml",
            "managed-agent-cookbooks/gl-reconciler/subagents/resolver.yaml",
            "scripts/test-cookbooks.sh",
        }
        pinned_paths = set()
        for url in urls:
            parsed = urlparse(url)
            parts = parsed.path.strip("/").split("/")
            if len(parts) < 5 or parts[2] != "blob":
                continue
            with self.subTest(url=url):
                self.assertEqual(parsed.scheme, "https")
                self.assertEqual(parsed.netloc, "github.com")
                self.assertEqual(parts[:2], ["anthropics", "financial-services"])
                self.assertEqual(parts[3], "4aa51ed3d379731f8f9beff498d749580372699c")
                upstream_path = "/".join(parts[4:])
                self.assertIn(upstream_path, expected_paths)
                pinned_paths.add(upstream_path)
        self.assertEqual(pinned_paths, expected_paths)
        self.assertIn("**Claim status:** candidate correspondence", evidence)
        self.assertIn("central orchestration", evidence)
        self.assertIn("common Colleague contract", evidence)
        self.assertIn("runtime decision behavior", evidence)

        chinese = (record / "definition.zh-CN.md").read_text(encoding="utf-8")
        for required in (
            "Mediator",
            "ConcreteMediator",
            "Colleague",
            "Design Patterns",
            "1994",
            "Gang of Four",
            "Behavioral Source",
            "Skill Artifact",
            "可信进程内代码",
            "确定性 oracle 不解释自然语言 Skill",
        ):
            with self.subTest(required=required):
                self.assertIn(required, chinese)

        for path in record.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".yaml", ".py", ".json"}:
                with self.subTest(path=path.relative_to(record)):
                    text = path.read_text(encoding="utf-8")
                    self.assertNotIn("EvoZeus", text)
                    self.assertNotIn("skillware-github", text)
                    self.assertNotIn("github.com/MetaInFLow/skillware", text)

    def test_pipes_and_filters_roles_contract_and_posa_boundary(self):
        record = PATTERNS / "pipes-and-filters"
        participant_map = yaml.safe_load(
            (record / "participant-map.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(
            set(participant_map["participants"]),
            {"Data Source", "Filter", "Pipe", "Data Sink"},
        )
        filter_ids = {
            item["id"]
            for item in participant_map["participants"]["Filter"]["implementations"]
        }
        self.assertEqual(
            filter_ids,
            {"normalize", "redact", "classify", "prioritize", "draft"},
        )
        context = participant_map["execution_context"]
        self.assertEqual(set(context), {"Agent Host", "Agent Runtime"})
        for role in context.values():
            self.assertEqual(role["evidence_status"], "not observable")
            self.assertNotIn("path", role)
            self.assertNotIn("evidence_path", role)

        contract = yaml.safe_load(
            (record / "sample/skillware.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(contract["pipeline_contract"], "support-ticket-pipeline-v1")
        self.assertEqual(contract["record_contract"], "support-ticket.v1")
        self.assertEqual(
            contract["filter_order"],
            ["normalize", "redact", "classify", "prioritize", "draft"],
        )
        self.assertEqual(contract["invocation_policy"], "exactly-once-in-runner-order")
        self.assertEqual(
            contract["filter_descriptor_policy"],
            "immutable-after-construction",
        )
        self.assertEqual(
            contract["topology_snapshot"],
            "filter-id-and-transform-at-runner-construction",
        )
        self.assertEqual(contract["normalization_policy"], "casefold-then-nfc")
        self.assertEqual(contract["input_limit_bytes"], 65536)
        self.assertEqual(contract["serialized_input_limit_bytes"], 394240)
        self.assertGreaterEqual(
            contract["serialized_input_limit_bytes"],
            contract["input_limit_bytes"] * 6 + len(b'{"text":""}'),
        )
        self.assertEqual(contract["pipe_validation"], "before-and-after-every-filter")
        self.assertEqual(contract["mutation_policy"], "deep-copy-at-every-pipe-transfer")
        self.assertEqual(contract["failure_policy"], "stop-with-stage-attribution")
        self.assertEqual(contract["filter_substitution"], "same-record-contract")

        english = (record / "definition.md").read_text(encoding="utf-8")
        chinese = (record / "definition.zh-CN.md").read_text(encoding="utf-8")
        for text in (english, chinese):
            self.assertIn("Pattern-Oriented Software Architecture", text)
            self.assertIn("Data Source", text)
            self.assertIn("Filter", text)
            self.assertIn("Pipe", text)
            self.assertIn("Data Sink", text)
        self.assertIn("not a Gang of Four pattern", english)
        self.assertIn("不是 Gang of Four（GoF）模式", chinese)
        self.assertIn("buffering, backpressure, concurrency, and network transport", english)
        self.assertIn("缓冲、背压、并发和网络传输", chinese)

    def test_pipes_and_filters_openmontage_evidence_is_exact_pinned_candidate(self):
        record = PATTERNS / "pipes-and-filters"
        correspondence = (record / "correspondence.md").read_text(encoding="utf-8")
        evidence = (record / "evidence/openmontage-frozen-case.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("[frozen evidence](evidence/openmontage-frozen-case.md)", correspondence)
        self.assertIn("**Status:** candidate correspondence", correspondence)
        self.assertNotIn("**Status:** confirmed correspondence", correspondence)
        self.assertIn("**Claim status:** candidate correspondence", evidence)
        self.assertNotIn("**Claim status:** confirmed correspondence", evidence)

        expected_paths = {
            "pipeline_defs/animated-explainer.yaml",
            "lib/pipeline_loader.py",
            "skills/pipelines/explainer/research-director.md",
            "skills/pipelines/explainer/proposal-director.md",
            "skills/pipelines/explainer/script-director.md",
            "skills/pipelines/explainer/scene-director.md",
            "skills/pipelines/explainer/asset-director.md",
            "skills/pipelines/explainer/edit-director.md",
            "skills/pipelines/explainer/compose-director.md",
            "skills/pipelines/explainer/publish-director.md",
        }
        pinned_paths = set()
        for url in re.findall(r"https://github\.com/[^)\s]+", evidence):
            parsed = urlparse(url)
            parts = parsed.path.strip("/").split("/")
            if len(parts) < 5 or parts[2] != "blob":
                continue
            with self.subTest(url=url):
                self.assertEqual(parsed.scheme, "https")
                self.assertEqual(parsed.netloc, "github.com")
                self.assertEqual(parts[:2], ["calesthio", "OpenMontage"])
                self.assertEqual(parts[3], "db91727598d08d40919d7d68a47864a5467bd448")
                upstream_path = "/".join(parts[4:])
                self.assertIn(upstream_path, expected_paths)
                pinned_paths.add(upstream_path)
        self.assertEqual(pinned_paths, expected_paths)
        self.assertIn("eight pinned stage director files", evidence)
        self.assertNotIn("nine pinned director files", evidence)

        for required in (
            "common versioned record envelope remains unverified",
            "filter isolation remains unverified",
            "runtime behavior remains unverified",
        ):
            with self.subTest(required=required):
                self.assertIn(required, evidence)

        for path in record.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".yaml", ".py", ".json"}:
                with self.subTest(path=path.relative_to(record)):
                    text = path.read_text(encoding="utf-8")
                    self.assertNotIn("skillware-github", text)
                    self.assertNotIn("github.com/MetaInFLow/skillware", text)


if __name__ == "__main__":
    unittest.main()
