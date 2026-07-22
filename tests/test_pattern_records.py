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


if __name__ == "__main__":
    unittest.main()
