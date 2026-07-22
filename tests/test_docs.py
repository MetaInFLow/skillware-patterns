from pathlib import Path
import re
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ARXIV_URL = "https://arxiv.org/abs/2607.18970"
PAPER_TITLE = (
    "Skillware: A Software Ontology and Engineering Lifecycle for "
    "Persistent Behavioral Artifacts"
)
AUTHORING_REVISION = "1fc1dfd"

REQUIRED_DOCS = (
    "skillware-definition.md",
    "paper-map.md",
    "pattern-transfer-protocol.md",
    "evidence-and-claim-status.md",
    "limitations.md",
)

ONTOLOGY = (
    "Behavioral Source",
    "Skill Artifact",
    "Skillware Unit",
    "Agent Host",
    "Agent Runtime",
    "Execution Trace",
    "Task Outcome",
)

ADMISSION_ELEMENTS = (
    "Source intent",
    "Design forces",
    "Participant correspondence",
    "Consequences",
    "Implementation evidence",
    "Focused verification",
    "Misuse discriminator",
)

STATUS_MEANINGS = {
    "constructive": (
        "the repository sample demonstrates that the mapping can be built"
    ),
    "confirmed correspondence": (
        "fixed-revision source evidence satisfies the participant relation"
    ),
    "candidate correspondence": (
        "partial source evidence exists but a participant or behavior is unverified"
    ),
    "unsupported": (
        "available evidence contradicts or fails the source pattern contract"
    ),
    "not observable": (
        "the required relation cannot be evaluated from available artifacts"
    ),
}

MAIN_TEXT_PATTERNS = (
    "Facade",
    "Adapter",
    "Composite",
    "Observer",
    "State",
    "Strategy",
)

SUPPLEMENT_PATTERNS = (
    "Decorator",
    "Template Method",
    "Memento",
    "Mediator",
    "Pipes and Filters",
    "Specification",
)

README_SECTIONS = (
    "Paper and repository role",
    "Software-engineering continuity",
    "Responsibility map",
    "Catalog at a glance",
    "Main-text mappings",
    "Repository supplement",
    "Facade walkthrough",
    "Quick start and validation",
    "Pattern-transfer admission protocol",
    "Claim statuses",
    "GoF-23 screen",
    "Repository map",
    "Scientific limitations",
    "Citation",
    "Contributing",
    "Licenses",
)

README_ZH_SECTIONS = (
    "论文与仓库定位",
    "软件工程连续性",
    "职责分工",
    "目录概览",
    "正文映射",
    "仓库补充实现",
    "Facade 示例导览",
    "快速开始与验证",
    "模式迁移准入协议",
    "主张状态",
    "GoF-23 筛查",
    "仓库结构",
    "科学局限",
    "引用",
    "贡献",
    "许可证",
)

README_COUNTS = (
    "23 GoF patterns screened",
    "10 detailed GoF implementations",
    "2 patterns from other established traditions",
)

VALIDATION_COMMANDS = (
    "python3 -m unittest tests/test_docs.py -v",
    "python3 -m unittest discover -s tests -v",
    "python3 scripts/validate_repository.py",
)

FACADE_COMMANDS = (
    "python3 patterns/facade/sample/scripts/run_demo.py",
    "python3 -m unittest discover -s patterns/facade/sample/tests -v",
)

SETUP_COMMANDS = (
    "python3 -m venv .venv",
    "source .venv/bin/activate",
    "python -m pip install -e .",
)

PATTERN_CLAIMS = {
    "Facade": ("confirmed correspondence", "constructive"),
    "Adapter": ("confirmed correspondence", "constructive"),
    "Composite": ("candidate correspondence", "constructive"),
    "Observer": ("candidate correspondence", "constructive"),
    "State": ("candidate correspondence", "constructive"),
    "Strategy": ("candidate correspondence", "constructive"),
    "Decorator": ("candidate correspondence", "constructive"),
    "Template Method": ("candidate correspondence", "constructive"),
    "Memento": ("candidate correspondence", "constructive"),
    "Mediator": ("candidate correspondence", "constructive"),
    "Pipes and Filters": ("candidate correspondence", "constructive"),
    "Specification": ("not observable", "constructive"),
}

TABLE5_TRACEABILITY = {
    "Facade": (
        "Entry Skill exposes one stable access contract over specialist Skills",
        "confirmed correspondence",
        "constructive",
        "[definition](../patterns/facade/definition.md)",
        "[sample](../patterns/facade/sample/)",
        "[local correspondence](../patterns/facade/correspondence.md)",
        "Superpowers participant mapping is verified in the frozen case; "
        "gstack root routing is also named.",
    ),
    "Adapter": (
        "Thin binding translates canonical Skill semantics into a target system contract",
        "confirmed correspondence",
        "constructive",
        "[definition](../patterns/adapter/definition.md)",
        "[sample](../patterns/adapter/sample/)",
        "[local correspondence](../patterns/adapter/correspondence.md)",
        "Strong correspondence in the paper; runtime parity requires tests.",
    ),
    "Composite": (
        "Atomic and composite stages share one invocation and result contract",
        "candidate correspondence",
        "constructive",
        "[definition](../patterns/composite/definition.md)",
        "[sample](../patterns/composite/sample/)",
        "[local correspondence](../patterns/composite/correspondence.md)",
        "Candidate correspondence plus a constructive repository fixture.",
    ),
    "Observer": (
        "Subject emits typed events to registered independent consumers",
        "candidate correspondence",
        "constructive",
        "[definition](../patterns/observer/definition.md)",
        "[sample](../patterns/observer/sample/)",
        "[local correspondence](../patterns/observer/correspondence.md)",
        "Candidate pending complete registration and delivery evidence.",
    ),
    "State": (
        "Persisted state controls permitted actions and transitions",
        "candidate correspondence",
        "constructive",
        "[definition](../patterns/state/definition.md)",
        "[sample](../patterns/state/sample/)",
        "[local correspondence](../patterns/state/correspondence.md)",
        "Candidate checkpoint behavior; full GoF participant delegation unverified.",
    ),
    "Strategy": (
        "Stable request and result contract selects among interchangeable procedures",
        "candidate correspondence",
        "constructive",
        "[definition](../patterns/strategy/definition.md)",
        "[sample](../patterns/strategy/sample/)",
        "[local correspondence](../patterns/strategy/correspondence.md)",
        "Open-source correspondence is motivation only; comparative benefit "
        "requires runtime study.",
    ),
}


def read_doc(name: str) -> str:
    return (DOCS / name).read_text(encoding="utf-8")


def table5_rows(text: str) -> dict[str, tuple[str, ...]]:
    section = text.split("## Table 5 traceability", 1)[1].split("\n## ", 1)[0]
    rows = {}
    for line in section.splitlines():
        cells = tuple(cell.strip() for cell in line.strip().strip("|").split("|"))
        if cells and cells[0] in MAIN_TEXT_PATTERNS:
            rows[cells[0]] = cells[1:]
    return rows


def readme_section(text: str, heading: str) -> str:
    return text.split(f"## {heading}", 1)[1].split("\n## ", 1)[0]


def markdown_pattern_rows(
    section: str, expected_names: tuple[str, ...]
) -> list[tuple[str, tuple[str, ...]]]:
    expected = set(expected_names)
    found = []
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = tuple(cell.strip() for cell in line.strip().strip("|").split("|"))
        first_cell = cells[0]
        match = re.search(r"\[([^]]+)\]", first_cell)
        name = match.group(1) if match else first_cell
        if name in expected:
            found.append((name, cells))
    return found


def markdown_links(text: str) -> list[str]:
    return re.findall(r"\[[^]]+\]\(([^)]+)\)", text)


def local_markdown_links(text: str) -> list[str]:
    return [
        target
        for target in markdown_links(text)
        if not re.match(r"(?:https?://|mailto:|#)", target)
    ]


def external_markdown_links(text: str) -> list[str]:
    return [target for target in markdown_links(text) if target.startswith("http")]


class MethodologyDocsTest(unittest.TestCase):
    def test_required_methodology_documents_exist(self):
        for name in REQUIRED_DOCS:
            with self.subTest(name=name):
                self.assertTrue((DOCS / name).is_file(), name)

    def test_skillware_definition_uses_final_ontology_and_conditions(self):
        text = read_doc("skillware-definition.md")
        chain = " -> ".join(ONTOLOGY)

        self.assertIn(chain, text)
        for clause in (
            "Skillware is an emerging AI-native software abstraction",
            "whose primary Behavioral Artifact is a separately addressable Agent Skill "
            "or coherent Skill suite",
            "A Skillware Unit is the independently managed software identity that "
            "carries this artifact as software.",
            "reusable task behavior primarily through persistent natural-language "
            "behavioral source",
            "A compatible Agent Host activates the unit",
            "the Agent Runtime interprets its activated behavioral source",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, text)
        for heading in (
            "C1: Skill-centered behavioral primacy",
            "C2: Independent software identity",
            "C3: Agent Host execution relationship",
            "Lifecycle Continuity",
        ):
            with self.subTest(heading=heading):
                self.assertIn(heading, text)
        self.assertNotRegex(text, r"(?i)\bA Skill is\b|\bSkill means\b")

    def test_skillware_definition_preserves_chain_semantics(self):
        text = read_doc("skillware-definition.md")

        self.assertIn("The Agent Host activates the Skillware Unit", text)
        self.assertIn(
            "The Agent Runtime interprets the activated behavioral source", text
        )
        self.assertIn(
            "Task Outcome is the effect or result of the execution, evaluated "
            "against task criteria.",
            text,
        )
        self.assertNotIn("| Task Outcome | Evaluates", text)

    def test_methodology_docs_exclude_outdated_terms(self):
        for name in REQUIRED_DOCS:
            text = read_doc(name)
            with self.subTest(name=name):
                self.assertNotIn("Agent Execution Core", text)
                self.assertNotIn("Behavioral Compiler", text)

    def test_transfer_protocol_has_exact_standalone_admission_elements(self):
        text = read_doc("pattern-transfer-protocol.md")
        lines = text.splitlines()
        controlled_block = "```text\n" + "\n".join(ADMISSION_ELEMENTS) + "\n```"

        self.assertIn(controlled_block, text)
        for element in ADMISSION_ELEMENTS:
            with self.subTest(element=element):
                self.assertEqual(lines.count(element), 1)
        self.assertRegex(text, r"(?is)names? alone.*(?:do not|does not|cannot).*transfer")

    def test_evidence_statuses_have_exact_descriptive_meanings(self):
        text = read_doc("evidence-and-claim-status.md")

        for status, meaning in STATUS_MEANINGS.items():
            with self.subTest(status=status):
                self.assertRegex(
                    text,
                    rf"(?m)^{re.escape(status)}: {re.escape(meaning)}$",
                )
        self.assertRegex(text, r"(?is)descriptive.*not (?:a )?score")

    def test_limitations_reject_overclaims_and_separate_analytical_axes(self):
        text = read_doc("limitations.md")

        for phrase in (
            "ecosystem frequency",
            "automatic quality advantage",
            "cross-Host behavioral equivalence",
            "invention of source patterns",
            "maturity ordering",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
        for term in ("pattern", "implementation dimension", "mechanism", "lifecycle stage"):
            with self.subTest(term=term):
                self.assertRegex(text, rf"(?im)^\| {re.escape(term)} \|")

    def test_paper_map_has_public_paper_and_unlinked_authoring_provenance(self):
        text = read_doc("paper-map.md")

        self.assertIn("Section 5.3", text)
        self.assertIn("Table 5", text)
        self.assertIn("v0.1-paper-v1", text)
        self.assertIn(f"[{PAPER_TITLE}]({ARXIV_URL})", text)
        self.assertIn("Haodi Fan", text)
        self.assertIn("Zucong Lan", text)
        self.assertIn(AUTHORING_REVISION, text)
        self.assertNotIn("github.com/MetaInFLow/skillware", text)
        self.assertNotRegex(text, rf"\[[^]]*{AUTHORING_REVISION}[^]]*\]\([^)]+\)")

    def test_table5_traceability_preserves_row_level_associations(self):
        text = read_doc("paper-map.md")

        self.assertEqual(table5_rows(text), TABLE5_TRACEABILITY)

    def test_paper_map_covers_repository_supplement(self):
        text = read_doc("paper-map.md")

        self.assertIn("ten detailed GoF implementations", text)
        self.assertIn("Pipes and Filters", text)
        self.assertIn("Specification", text)

    def test_paper_map_has_operational_evidence_boundary(self):
        text = read_doc("paper-map.md")

        self.assertNotIn("no circular evidence", text.lower())
        self.assertIn(
            "Tool or sample output cannot validate the Skillware ontology.", text
        )
        self.assertIn(
            "New evidence can enter the paper only after the target revision and "
            "method version are frozen, evidence paths are recorded, and human "
            "review is complete.",
            text,
        )

    def test_paper_map_links_are_public_or_local_and_resolve(self):
        text = read_doc("paper-map.md")

        self.assertEqual(set(external_markdown_links(text)), {ARXIV_URL})
        for target in local_markdown_links(text):
            with self.subTest(target=target):
                self.assertTrue((DOCS / target).resolve().exists())


class ReadmeContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.english = (ROOT / "README.md").read_text(encoding="utf-8")
        cls.chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        cls.paper_map = read_doc("paper-map.md")
        catalog = yaml.safe_load(
            (ROOT / "catalog/pattern-index.yaml").read_text(encoding="utf-8")
        )
        cls.catalog_by_name = {row["name"]: row for row in catalog}

    def test_readmes_have_language_specific_openings_and_cross_links(self):
        english_lines = self.english.splitlines()
        chinese_lines = self.chinese.splitlines()

        self.assertEqual(english_lines[0], "# Skillware Patterns")
        self.assertEqual(chinese_lines[0], "# Skillware Patterns")
        self.assertEqual(
            english_lines[2],
            "An executable, bilingual pattern-transfer supplement for the "
            "Skillware paper.",
        )
        self.assertEqual(
            chinese_lines[2], "Skillware 论文的双语可执行模式迁移补充材料。"
        )
        self.assertIn("README.zh-CN.md", self.english)
        self.assertIn("README.md", self.chinese)
        for text in (self.english, self.chinese):
            self.assertIn(PAPER_TITLE, text)

    def test_readme_sections_follow_the_approved_order(self):
        for headings, text in (
            (README_SECTIONS, self.english),
            (README_ZH_SECTIONS, self.chinese),
        ):
            positions = []
            for heading in headings:
                with self.subTest(heading=heading):
                    marker = f"## {heading}"
                    self.assertEqual(text.count(marker), 1)
                    positions.append(text.index(marker))
            self.assertEqual(positions, sorted(positions))

    def test_readmes_define_skillware_and_runtime_boundary(self):
        english_definition = (
            "Skillware is the software abstraction that extends software "
            "engineering to persistent behavioral artifacts"
        )
        chinese_definition = (
            "Skillware 是将软件工程扩展至持久行为制品的软件抽象"
        )
        boundary = (
            "Behavioral Source -> Skill Artifact -> Skillware Unit -> "
            "Agent Host -> Agent Runtime"
        )
        self.assertIn(english_definition, self.english)
        self.assertNotIn(english_definition, self.chinese)
        self.assertIn(chinese_definition, self.chinese)
        for text in (self.english, self.chinese):
            self.assertIn(boundary, text)
            self.assertNotIn("Agent Execution Core", text)
            self.assertNotIn("Behavioral Compiler", text)

    def test_catalog_count_claims_are_bounded_and_aligned(self):
        for phrase in README_COUNTS:
            self.assertIn(phrase, self.english)
            self.assertIn(phrase, self.chinese)
        self.assertIn("不是新的设计模式集合", self.chinese)
        for text in (self.english, self.chinese):
            self.assertNotRegex(
                text,
                r"(?i)(?:all|全部|所有) 23 (?:GoF )?(?:patterns?|模式).{0,40}"
                r"(?:implemented|implementations?|实现)",
            )
            self.assertNotRegex(text, r"(?i)maturity (?:score|rating)|成熟度(?:评分|分数)")

    def assert_readme_pattern_table(self, text, heading, expected_names, paper_heading):
        rows = markdown_pattern_rows(readme_section(text, heading), expected_names)
        names = tuple(name for name, _ in rows)
        self.assertEqual(names, expected_names)
        self.assertEqual(len(names), len(set(names)))

        paper_rows = dict(
            markdown_pattern_rows(
                readme_section(self.paper_map, paper_heading), expected_names
            )
        )
        self.assertEqual(set(paper_rows), set(expected_names))

        for name, cells in rows:
            with self.subTest(heading=heading, pattern=name):
                catalog = self.catalog_by_name[name]
                expected_role = (
                    "main-text"
                    if expected_names == MAIN_TEXT_PATTERNS
                    else "repository-supplement"
                )
                self.assertEqual(catalog["paper_role"], expected_role)
                metadata = (
                    f"`{catalog['source_tradition']}` / "
                    f"`{catalog['source_category']}`"
                )
                self.assertEqual(cells[1], metadata)
                self.assertEqual(cells[3:5], PATTERN_CLAIMS[name])
                self.assertEqual(
                    markdown_links(" | ".join(cells)),
                    [
                        f"patterns/{catalog['id']}/definition.md",
                        f"patterns/{catalog['id']}/correspondence.md",
                        f"patterns/{catalog['id']}/sample/",
                    ],
                )

                paper_cells = paper_rows[name]
                self.assertEqual(paper_cells[2:4], PATTERN_CLAIMS[name])
                self.assertEqual(
                    markdown_links(" | ".join(paper_cells)),
                    [
                        f"../patterns/{catalog['id']}/definition.md",
                        f"../patterns/{catalog['id']}/sample/",
                        f"../patterns/{catalog['id']}/correspondence.md",
                    ],
                )

    def test_main_text_and_supplement_tables_match_catalog_and_paper_map(self):
        for text, main_heading, supplement_heading in (
            (self.english, "Main-text mappings", "Repository supplement"),
            (self.chinese, "正文映射", "仓库补充实现"),
        ):
            self.assert_readme_pattern_table(
                text,
                main_heading,
                MAIN_TEXT_PATTERNS,
                "Table 5 traceability",
            )
            self.assert_readme_pattern_table(
                text,
                supplement_heading,
                SUPPLEMENT_PATTERNS,
                "Repository supplement",
            )

    def test_facade_walkthrough_links_real_artifacts_and_exact_commands(self):
        required_paths = (
            "patterns/facade/sample/SKILL.md",
            "patterns/facade/participant-map.yaml",
            "patterns/facade/sample/fixtures/valid/incident.json",
            "patterns/facade/sample/expected/incident-result.json",
            "patterns/facade/sample/scripts/run_demo.py",
            "patterns/facade/sample/tests/test_demo.py",
        )
        for text in (self.english, self.chinese):
            for path in required_paths:
                self.assertIn(f"]({path})", text)
            for command in FACADE_COMMANDS:
                self.assertIn(command, text)

    def test_quick_start_is_at_most_three_steps_and_has_all_validation_commands(self):
        for heading, text in (
            ("Quick start and validation", self.english),
            ("快速开始与验证", self.chinese),
        ):
            section = readme_section(text, heading)
            numbered_steps = re.findall(r"(?m)^\d+\. ", section)
            self.assertEqual(len(numbered_steps), 3)
            commands = SETUP_COMMANDS + FACADE_COMMANDS + VALIDATION_COMMANDS
            for command in commands:
                self.assertIn(command, section)
            positions = [section.index(command) for command in commands]
            self.assertEqual(positions, sorted(positions))
            install_position = section.index("python -m pip install -e .")
            for command in VALIDATION_COMMANDS:
                self.assertLess(install_position, section.index(command))

    def test_protocol_and_claim_statuses_are_complete_in_both_languages(self):
        for protocol_heading, status_heading, text in (
            ("Pattern-transfer admission protocol", "Claim statuses", self.english),
            ("模式迁移准入协议", "主张状态", self.chinese),
        ):
            protocol = readme_section(text, protocol_heading)
            statuses = readme_section(text, status_heading)
            for element in ADMISSION_ELEMENTS:
                self.assertIn(element, protocol)
            for status in STATUS_MEANINGS:
                self.assertIn(status, statuses)
        english_statuses = readme_section(self.english, "Claim statuses")
        chinese_statuses = readme_section(self.chinese, "主张状态")
        self.assertIn("These statuses are descriptive, not a score.", english_statuses)
        self.assertIn("这些状态是描述性的，而非评分。", chinese_statuses)
        self.assertNotIn("These statuses are descriptive", chinese_statuses)

    def test_responsibility_source_category_and_paper_link_boundaries(self):
        for text in (self.english, self.chinese):
            self.assertIn("MetaInFlow/skillware-patterns", text)
            self.assertIn(ARXIV_URL, text)
            self.assertIn("Haodi Fan", text)
            self.assertIn("Zucong Lan", text)
            self.assertIn(AUTHORING_REVISION, text)
            self.assertIn("source_category", text)
            self.assertRegex(text, r"(?is)flat|扁平")
            self.assertEqual(set(external_markdown_links(text)), {ARXIV_URL})
            self.assertNotIn("github.com/MetaInFLow/skillware", text)
            self.assertNotIn("arxiv.org/submit", text)
            self.assertNotRegex(
                text, rf"\[[^]]*{AUTHORING_REVISION}[^]]*\]\([^)]+\)"
            )
            self.assertIn(f"[{PAPER_TITLE}]({ARXIV_URL})", text)
        self.assertIn("submitted 21 July 2026", self.english)
        self.assertIn("2026 年 7 月 21 日提交", self.chinese)
        self.assertIn("not a public dependency", self.english)
        self.assertIn("self-contained executable supplement", self.english)
        self.assertIn("不是公开依赖", self.chinese)
        self.assertIn("自包含的可执行补充", self.chinese)
        self.assertIn("not yet public-release ready", self.english)
        self.assertIn("尚未达到公开发布就绪状态", self.chinese)
        self.assertNotIn("will be inserted after assignment", self.english)
        self.assertNotIn("分配后补入", self.chinese)

    def test_readme_local_links_resolve(self):
        for name, text in (("README.md", self.english), ("README.zh-CN.md", self.chinese)):
            for target in local_markdown_links(text):
                clean_target = target.split("#", 1)[0]
                with self.subTest(readme=name, target=target):
                    self.assertTrue((ROOT / clean_target).exists())


if __name__ == "__main__":
    unittest.main()
