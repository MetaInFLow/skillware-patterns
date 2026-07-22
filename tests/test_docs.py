from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

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

RESEARCH_COMMIT = "1fc1dfd"
RESEARCH_BASE = (
    f"https://github.com/MetaInFLow/skillware/blob/{RESEARCH_COMMIT}"
)

TABLE5_TRACEABILITY = {
    "Facade": (
        "Entry Skill exposes one stable access contract over specialist Skills",
        "confirmed correspondence",
        "constructive",
        "[definition](../patterns/facade/definition.md)",
        "[sample](../patterns/facade/sample/)",
        f"[pinned research record]({RESEARCH_BASE}/research/patterns/facade.md)",
        "Superpowers participant mapping is verified in the frozen case; "
        "gstack root routing is also named.",
    ),
    "Adapter": (
        "Thin binding translates canonical Skill semantics into a target system contract",
        "confirmed correspondence",
        "constructive",
        "[definition](../patterns/adapter/definition.md)",
        "[sample](../patterns/adapter/sample/)",
        f"[pinned research record]({RESEARCH_BASE}/research/patterns/adapter.md)",
        "Strong correspondence in the paper; runtime parity requires tests.",
    ),
    "Composite": (
        "Atomic and composite stages share one invocation and result contract",
        "candidate correspondence",
        "constructive",
        "[definition](../patterns/composite/definition.md)",
        "[sample](../patterns/composite/sample/)",
        f"[pinned research record]({RESEARCH_BASE}/research/patterns/composite.md)",
        "Candidate correspondence plus a constructive repository fixture.",
    ),
    "Observer": (
        "Subject emits typed events to registered independent consumers",
        "candidate correspondence",
        "constructive",
        "[definition](../patterns/observer/definition.md)",
        "[sample](../patterns/observer/sample/)",
        f"[pinned research record]({RESEARCH_BASE}/research/patterns/observer.md)",
        "Candidate pending complete registration and delivery evidence.",
    ),
    "State": (
        "Persisted state controls permitted actions and transitions",
        "candidate correspondence",
        "constructive",
        "[definition](../patterns/state/definition.md)",
        "[sample](../patterns/state/sample/)",
        f"[pinned research record]({RESEARCH_BASE}/research/patterns/state.md)",
        "Candidate checkpoint behavior; full GoF participant delegation unverified.",
    ),
    "Strategy": (
        "Stable request and result contract selects among interchangeable procedures",
        "candidate correspondence",
        "constructive",
        "[definition](../patterns/strategy/definition.md)",
        "[sample](../patterns/strategy/sample/)",
        f"[pinned research record]({RESEARCH_BASE}/research/patterns/strategy.md)",
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


def markdown_table_patterns(section: str) -> set[str]:
    expected = set(MAIN_TEXT_PATTERNS + SUPPLEMENT_PATTERNS)
    found = set()
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        first_cell = line.strip().strip("|").split("|", 1)[0].strip()
        match = re.search(r"\[([^]]+)\]", first_cell)
        name = match.group(1) if match else first_cell
        if name in expected:
            found.add(name)
    return found


def local_markdown_links(text: str) -> list[str]:
    return [
        target
        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text)
        if not re.match(r"(?:https?://|mailto:|#)", target)
    ]


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

    def test_paper_map_has_pinned_source_and_release_binding(self):
        text = read_doc("paper-map.md")

        self.assertIn("Section 5.3", text)
        self.assertIn("Table 5", text)
        self.assertIn("v0.1-paper-v1", text)
        self.assertIn(
            f"[paper source pinned at `{RESEARCH_COMMIT}`]"
            f"({RESEARCH_BASE}/paper/manuscript-ars-v1/phase7_output_arxiv/main.tex)",
            text,
        )

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

    def test_paper_map_catalog_links_resolve(self):
        text = read_doc("paper-map.md")
        targets = re.findall(r"\[[^]]+\]\((\.\./catalog/[^)]+)\)", text)

        self.assertEqual(
            set(targets),
            {"../catalog/pattern-index.md", "../catalog/gof-23-screening.md"},
        )
        for target in targets:
            with self.subTest(target=target):
                self.assertTrue((DOCS / target).resolve().is_file())


class ReadmeContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.english = (ROOT / "README.md").read_text(encoding="utf-8")
        cls.chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")

    def test_readmes_have_aligned_opening_and_cross_links(self):
        english_lines = self.english.splitlines()
        chinese_lines = self.chinese.splitlines()

        self.assertEqual(english_lines[0], "# Skillware Patterns")
        self.assertEqual(chinese_lines[0], "# Skillware Patterns")
        self.assertEqual(english_lines[2], chinese_lines[2])
        self.assertIn("README.zh-CN.md", self.english)
        self.assertIn("README.md", self.chinese)
        for text in (self.english, self.chinese):
            self.assertIn(
                "Skillware: A Software Ontology and Engineering Lifecycle for "
                "Persistent Behavioral Artifacts",
                text,
            )

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
        definition = (
            "Skillware is the software abstraction that extends software "
            "engineering to persistent behavioral artifacts"
        )
        boundary = (
            "Behavioral Source -> Skill Artifact -> Skillware Unit -> "
            "Agent Host -> Agent Runtime"
        )
        for text in (self.english, self.chinese):
            self.assertIn(definition, text)
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

    def test_main_text_and_supplement_tables_have_exact_pattern_sets(self):
        english_main = readme_section(self.english, "Main-text mappings")
        english_supplement = readme_section(self.english, "Repository supplement")
        chinese_main = readme_section(self.chinese, "正文映射")
        chinese_supplement = readme_section(self.chinese, "仓库补充实现")

        self.assertEqual(markdown_table_patterns(english_main), set(MAIN_TEXT_PATTERNS))
        self.assertEqual(
            markdown_table_patterns(english_supplement), set(SUPPLEMENT_PATTERNS)
        )
        self.assertEqual(markdown_table_patterns(chinese_main), set(MAIN_TEXT_PATTERNS))
        self.assertEqual(
            markdown_table_patterns(chinese_supplement), set(SUPPLEMENT_PATTERNS)
        )
        for section in (english_main, chinese_main):
            for status in ("confirmed correspondence", "candidate correspondence", "constructive"):
                self.assertIn(status, section)

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
            self.assertGreaterEqual(len(numbered_steps), 1)
            self.assertLessEqual(len(numbered_steps), 3)
            for command in FACADE_COMMANDS + VALIDATION_COMMANDS:
                self.assertIn(command, section)

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
            self.assertRegex(statuses, r"(?is)descriptive.*not (?:a )?score")

    def test_responsibility_source_category_and_paper_link_boundaries(self):
        paper_url = (
            f"{RESEARCH_BASE}/paper/manuscript-ars-v1/phase7_output_arxiv/main.tex"
        )
        for text in (self.english, self.chinese):
            for repository in ("MetaInFlow/skillware", "MetaInFlow/skillware-patterns"):
                self.assertIn(repository, text)
            self.assertIn(paper_url, text)
            self.assertIn("source_category", text)
            self.assertRegex(text, r"(?is)flat|扁平")
            self.assertNotRegex(text, r"https?://arxiv\.org/(?:abs|pdf)/")
        self.assertIn("will be inserted after assignment", self.english)
        self.assertIn("分配后补入", self.chinese)

    def test_readme_local_links_resolve(self):
        for name, text in (("README.md", self.english), ("README.zh-CN.md", self.chinese)):
            for target in local_markdown_links(text):
                clean_target = target.split("#", 1)[0]
                with self.subTest(readme=name, target=target):
                    self.assertTrue((ROOT / clean_target).exists())


if __name__ == "__main__":
    unittest.main()
