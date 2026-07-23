from pathlib import Path
import re
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ARXIV_URL = "https://arxiv.org/abs/2607.18970"
REPOSITORY_URL = "https://github.com/MetaInFLow/skillware-patterns"
RELEASE_TAG = "v0.1-paper-v1"
RELEASE_URL = f"{REPOSITORY_URL}/releases/tag/{RELEASE_TAG}"
WORKFLOW_URL = f"{REPOSITORY_URL}/actions/workflows/validate.yml"
PAPER_TITLE = (
    "Skillware: A Software Ontology and Engineering Lifecycle for "
    "Persistent Behavioral Artifacts"
)
AUTHORING_REVISION = "1fc1dfd"
GOVERNANCE_DOCS = (
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
)
CITATION_TOP_LEVEL_KEYS = {
    "cff-version",
    "title",
    "message",
    "type",
    "authors",
    "version",
    "repository-code",
    "date-released",
    "preferred-citation",
}
SOFTWARE_AUTHORS = [
    {
        "family-names": "Fan",
        "given-names": "Anthony",
        "email": "anthonyfan@metainflow.cn",
    },
    {
        "family-names": "Lan",
        "given-names": "Neil",
        "email": "neillan@metainflow.cn",
    },
]
PREFERRED_CITATION = {
    "type": "article",
    "title": PAPER_TITLE,
    "authors": [
        {"family-names": "Fan", "given-names": "Haodi"},
        {"family-names": "Lan", "given-names": "Zucong"},
    ],
    "year": 2026,
    "url": ARXIV_URL,
    "doi": "10.48550/arXiv.2607.18970",
}
LICENSE_BOUNDARY_BLOCK = """```text
Apache-2.0
  .github/**
  .gitignore
  pyproject.toml
  scripts/**
  tests/**
  patterns/*/sample/**

CC-BY-4.0
  README.md
  README.zh-CN.md
  CITATION.cff
  CONTRIBUTING.md
  CODE_OF_CONDUCT.md
  catalog/**
  docs/**
  patterns/.gitkeep
  patterns/*/** excluding patterns/*/sample/**

Canonical upstream texts (outside repository relicensing)
  LICENSE-CODE
  LICENSE-DOCS
```"""

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

MAIN_TEXT_RELATIONS_EN = {
    "Facade": "One entry Skill exposes a stable contract over specialist Skills.",
    "Adapter": (
        "A thin binding translates canonical Skill semantics into a target "
        "system contract."
    ),
    "Composite": (
        "Atomic and composite stages share one invocation and result contract."
    ),
    "Observer": (
        "A subject emits typed events to registered independent consumers."
    ),
    "State": "Persisted state controls permitted actions and transitions.",
    "Strategy": (
        "One request/result contract selects among interchangeable procedures."
    ),
}

MAIN_TEXT_RELATIONS_ZH = {
    "Facade": "一个入口 Skill 在多个专家 Skill 之上提供稳定契约。",
    "Adapter": "薄绑定把规范 Skill 语义转换为目标系统契约。",
    "Composite": "原子阶段和组合阶段共享同一调用及结果契约。",
    "Observer": "Subject 向已注册且相互独立的消费者发送类型化事件。",
    "State": "持久状态控制允许的动作与转换。",
    "Strategy": "一个请求/结果契约在可互换过程之间进行选择。",
}

SUPPLEMENT_RELATIONS_EN = {
    "Decorator": "Optional review Skills wrap one shared component contract.",
    "Template Method": (
        "A root Skill owns invariant workflow order and bounded specialization "
        "hooks."
    ),
    "Memento": (
        "A caretaker captures and restores an originator's opaque configuration "
        "state."
    ),
    "Mediator": (
        "A coordinator centralizes interaction among deployment-readiness Skills."
    ),
    "Pipes and Filters": (
        "Ordered Filters transform one versioned ticket record through explicit "
        "Pipes."
    ),
    "Specification": (
        "Named, composable rules evaluate one bounded expense candidate."
    ),
}

SUPPLEMENT_RELATIONS_ZH = {
    "Decorator": "可选审查 Skill 围绕同一个组件契约逐层包装。",
    "Template Method": "根 Skill 固定工作流顺序，并开放有边界的特化钩子。",
    "Memento": "Caretaker 捕获并恢复 Originator 的不透明配置状态。",
    "Mediator": "协调器集中管理部署就绪 Skill 之间的交互。",
    "Pipes and Filters": (
        "有序 Filter 通过显式 Pipe 转换同一个带版本工单记录。"
    ),
    "Specification": "具名且可组合的规则评估一个有边界的费用候选对象。",
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


def readme_section(text: str, heading: str) -> str:
    return text.split(f"## {heading}", 1)[1].split("\n## ", 1)[0]


def markdown_data_rows(section: str) -> list[tuple[str, tuple[str, ...]]]:
    rows = []
    header_seen = False
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = tuple(cell.strip() for cell in stripped.strip("|").split("|"))
        if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        if not header_seen:
            header_seen = True
            continue
        first_cell = cells[0]
        match = re.search(r"\[([^]]+)\]", first_cell)
        name = match.group(1) if match else first_cell
        rows.append((name, cells))
    return rows


def assert_exact_pattern_names(rows, expected_names: tuple[str, ...]) -> None:
    names = tuple(name for name, _ in rows)
    if len(rows) != len(expected_names):
        raise AssertionError(
            f"expected exactly {len(expected_names)} rows, found {len(rows)}: {names}"
        )
    if len(names) != len(set(names)):
        raise AssertionError(f"duplicate pattern rows: {names}")
    if names != expected_names:
        raise AssertionError(f"expected ordered rows {expected_names}, found {names}")


def assert_exact_row_widths(rows, expected_width: int) -> None:
    invalid = {
        name: len(cells) for name, cells in rows if len(cells) != expected_width
    }
    if invalid:
        raise AssertionError(
            f"expected {expected_width} cells in every row, found {invalid}"
        )


def assert_exact_participant_relations(rows, expected_relations) -> None:
    names = tuple(name for name, _ in rows)
    if tuple(expected_relations) != names:
        raise AssertionError("relation expectations do not match the table rows")
    actual = {name: cells[2] for name, cells in rows}
    if actual != expected_relations:
        raise AssertionError(
            f"participant relations differ: expected {expected_relations}, found {actual}"
        )


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


def assert_citation_contract(citation) -> None:
    if not isinstance(citation, dict):
        raise AssertionError("citation must be a mapping")
    actual_keys = set(citation)
    if actual_keys != CITATION_TOP_LEVEL_KEYS:
        missing = sorted(CITATION_TOP_LEVEL_KEYS - actual_keys)
        illegal = sorted(actual_keys - CITATION_TOP_LEVEL_KEYS)
        raise AssertionError(
            f"invalid top-level keys: missing={missing}, illegal={illegal}"
        )
    expected_strings = {
        "cff-version": "1.2.0",
        "title": "Skillware Patterns",
        "message": "Cite the Skillware paper and this software artifact.",
        "type": "software",
        "version": "0.1.0",
        "repository-code": REPOSITORY_URL,
        "date-released": "2026-07-22",
    }
    for key, expected in expected_strings.items():
        value = citation[key]
        if not isinstance(value, str) or value != expected:
            raise AssertionError(f"{key} must be the exact required string")
    if citation["authors"] != SOFTWARE_AUTHORS:
        raise AssertionError("software authors do not match the required people")
    if citation["preferred-citation"] != PREFERRED_CITATION:
        raise AssertionError("preferred-citation does not match the public paper")


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
        rows = markdown_data_rows(readme_section(text, "Table 5 traceability"))

        assert_exact_pattern_names(rows, MAIN_TEXT_PATTERNS)
        assert_exact_row_widths(rows, 8)
        self.assertEqual(
            {name: cells[1:] for name, cells in rows}, TABLE5_TRACEABILITY
        )

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


class GovernanceDocsTest(unittest.TestCase):
    def test_citation_has_exact_software_and_preferred_paper_metadata(self):
        citation = yaml.safe_load(
            (ROOT / "CITATION.cff").read_text(encoding="utf-8")
        )

        assert_citation_contract(citation)

    def test_citation_contract_rejects_missing_release_field_and_illegal_key(self):
        citation = yaml.safe_load(
            (ROOT / "CITATION.cff").read_text(encoding="utf-8")
        )
        without_release_date = dict(citation)
        without_release_date.pop("date-released")
        with self.assertRaisesRegex(AssertionError, "missing=.*date-released"):
            assert_citation_contract(without_release_date)

        with_illegal_key = dict(citation)
        with_illegal_key["repository"] = REPOSITORY_URL
        with self.assertRaisesRegex(AssertionError, "illegal=.*repository"):
            assert_citation_contract(with_illegal_key)

    def test_contributing_requires_the_complete_admission_contract(self):
        text = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

        for phrase in (
            "canonical, established source or tradition",
            "exact participant map",
            "runnable positive case",
            "close negative or misuse case",
            "standalone sample",
            "Python standard library",
            "controlled claim status",
            "bilingual parity",
            "full repository test suite",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
        for element in ADMISSION_ELEMENTS:
            with self.subTest(element=element):
                self.assertIn(element, text)
        self.assertIn(
            "This contribution does not rename an engineering mechanism as a pattern.",
            text,
        )
        self.assertIn(
            "When ecosystem correspondence is claimed, provide pinned public "
            "correspondence evidence at an immutable revision.",
            text,
        )
        self.assertIn(
            "When no ecosystem correspondence is claimed, use `not observable` "
            "and state the evidentiary limit in the correspondence record.",
            text,
        )
        self.assertIn(
            "The current scope of 10 GoF implementations and 2 implementations "
            "from other established traditions is neither an automatic admission "
            "cap nor a claim that this repository introduces new patterns.",
            text,
        )

    def test_contributing_defines_the_complete_dual_license_boundary(self):
        text = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

        self.assertIn(LICENSE_BOUNDARY_BLOCK, text)
        self.assertIn("Apache License 2.0", text)
        self.assertIn("Creative Commons Attribution 4.0 International", text)
        self.assertIn(
            "LICENSE-CODE and LICENSE-DOCS retain their canonical upstream texts "
            "and are outside repository relicensing.",
            text,
        )
        self.assertIn(
            "Linked third-party artifacts remain under their upstream licenses.",
            text,
        )

    def test_publication_ci_will_use_external_cff_schema_validation(self):
        text = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

        self.assertIn(
            "Publication CI must validate `CITATION.cff` against the CFF 1.2.0 "
            "schema with an external validator.",
            text,
        )
        self.assertIn(
            "The validator is CI tooling and must not be added to runtime "
            "dependencies.",
            text,
        )
        self.assertNotIn("cffconvert", pyproject.lower())

    def test_code_of_conduct_is_contributor_covenant_2_1_with_contact(self):
        text = (ROOT / "CODE_OF_CONDUCT.md").read_text(encoding="utf-8")

        self.assertIn("Contributor Covenant Code of Conduct", text)
        self.assertIn("version 2.1", text)
        self.assertIn("anthonyfan@metainflow.cn", text)
        self.assertNotIn("[INSERT CONTACT METHOD]", text)

    def test_governance_document_links_resolve(self):
        for name in GOVERNANCE_DOCS:
            text = (ROOT / name).read_text(encoding="utf-8")
            for target in local_markdown_links(text):
                clean_target = target.split("#", 1)[0]
                with self.subTest(document=name, target=target):
                    self.assertTrue((ROOT / clean_target).exists())


class LegacyReadmeContractContract:
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

    def assert_readme_pattern_table(
        self,
        text,
        heading,
        expected_names,
        paper_heading,
        paper_width,
        expected_relations=None,
    ):
        rows = markdown_data_rows(readme_section(text, heading))
        assert_exact_pattern_names(rows, expected_names)
        assert_exact_row_widths(rows, 6)
        if expected_relations is not None:
            assert_exact_participant_relations(rows, expected_relations)

        paper_row_list = markdown_data_rows(
            readme_section(self.paper_map, paper_heading)
        )
        assert_exact_pattern_names(paper_row_list, expected_names)
        assert_exact_row_widths(paper_row_list, paper_width)
        paper_rows = dict(paper_row_list)

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
        for text, main_heading, supplement_heading, main_relations, supplement_relations in (
            (
                self.english,
                "Main-text mappings",
                "Repository supplement",
                MAIN_TEXT_RELATIONS_EN,
                SUPPLEMENT_RELATIONS_EN,
            ),
            (
                self.chinese,
                "正文映射",
                "仓库补充实现",
                MAIN_TEXT_RELATIONS_ZH,
                SUPPLEMENT_RELATIONS_ZH,
            ),
        ):
            self.assert_readme_pattern_table(
                text,
                main_heading,
                MAIN_TEXT_PATTERNS,
                "Table 5 traceability",
                8,
                main_relations,
            )
            self.assert_readme_pattern_table(
                text,
                supplement_heading,
                SUPPLEMENT_PATTERNS,
                "Repository supplement",
                7,
                supplement_relations,
            )

    def test_exact_table_guard_rejects_invented_and_duplicate_rows(self):
        section = readme_section(self.english, "Main-text mappings")
        data_lines = [
            line for line in section.splitlines() if line.startswith("| [")
        ]

        with_invented = section + (
            "\n| [Invented](patterns/invented/definition.md) | `invented` / "
            "`invented` | invented relation | unsupported | constructive | "
            "[sample](patterns/invented/sample/) |\n"
        )
        invented_rows = markdown_data_rows(with_invented)
        self.assertEqual(invented_rows[-1][0], "Invented")
        with self.assertRaisesRegex(AssertionError, "expected exactly 6 rows"):
            assert_exact_pattern_names(invented_rows, MAIN_TEXT_PATTERNS)

        with_duplicate = section.replace(data_lines[-1], data_lines[0])
        duplicate_rows = markdown_data_rows(with_duplicate)
        self.assertEqual(duplicate_rows[-1][0], "Facade")
        with self.assertRaisesRegex(AssertionError, "duplicate pattern rows"):
            assert_exact_pattern_names(duplicate_rows, MAIN_TEXT_PATTERNS)

    def test_main_text_relation_guard_rejects_incorrect_facade_mapping(self):
        incorrect = self.english.replace(
            MAIN_TEXT_RELATIONS_EN["Facade"],
            "Facade has an intentionally incorrect participant relation.",
            1,
        )

        rows = markdown_data_rows(readme_section(incorrect, "Main-text mappings"))
        with self.assertRaisesRegex(AssertionError, "participant relations differ"):
            assert_exact_participant_relations(rows, MAIN_TEXT_RELATIONS_EN)

    def test_supplement_relation_guard_rejects_incorrect_decorator_mapping(self):
        incorrect = self.english.replace(
            SUPPLEMENT_RELATIONS_EN["Decorator"],
            "Decorator has an intentionally incorrect participant relation.",
            1,
        )

        rows = markdown_data_rows(readme_section(incorrect, "Repository supplement"))
        with self.assertRaisesRegex(AssertionError, "participant relations differ"):
            assert_exact_participant_relations(rows, SUPPLEMENT_RELATIONS_EN)

    def test_row_width_guard_rejects_extra_trailing_facade_cell(self):
        section = readme_section(self.english, "Main-text mappings")
        facade_line = next(
            line for line in section.splitlines() if line.startswith("| [Facade]")
        )
        with_extra_cell = section.replace(
            facade_line,
            facade_line.removesuffix("|") + "| unexpected trailing cell |",
            1,
        )

        rows = markdown_data_rows(with_extra_cell)
        self.assertEqual(len(rows[0][1]), 7)
        with self.assertRaisesRegex(AssertionError, "expected 6 cells"):
            assert_exact_row_widths(rows, 6)

    def test_facade_walkthrough_links_real_artifacts_and_exact_commands(self):
        required_paths = (
            "patterns/facade/sample/SKILL.md",
            "patterns/facade/participant-map.yaml",
            "patterns/facade/sample/fixtures/valid/incident.json",
            "patterns/facade/sample/expected/incident-result.json",
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
            self.assertEqual(
                set(external_markdown_links(text)),
                {ARXIV_URL, REPOSITORY_URL, RELEASE_URL, WORKFLOW_URL},
            )
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
        self.assertNotIn("not yet public-release ready", self.english)
        self.assertNotIn("尚未达到公开发布就绪状态", self.chinese)
        self.assertNotIn("will be inserted after assignment", self.english)
        self.assertNotIn("分配后补入", self.chinese)

    def test_readme_local_links_resolve(self):
        for name, text in (("README.md", self.english), ("README.zh-CN.md", self.chinese)):
            for target in local_markdown_links(text):
                clean_target = target.split("#", 1)[0]
                with self.subTest(readme=name, target=target):
                    self.assertTrue((ROOT / clean_target).exists())

    def test_governance_sections_are_operational_and_bilingually_aligned(self):
        for citation_heading, contribution_heading, license_heading, text in (
            ("Citation", "Contributing", "Licenses", self.english),
            ("引用", "贡献", "许可证", self.chinese),
        ):
            citation = readme_section(text, citation_heading)
            contributing = readme_section(text, contribution_heading)
            licenses = readme_section(text, license_heading)
            self.assertIn("](CITATION.cff)", citation)
            self.assertIn("](CONTRIBUTING.md)", contributing)
            self.assertIn("](CODE_OF_CONDUCT.md)", contributing)
            self.assertIn("](LICENSE-CODE)", licenses)
            self.assertIn("](LICENSE-DOCS)", licenses)
            self.assertIn(LICENSE_BOUNDARY_BLOCK, licenses)
            self.assertIn("Apache License 2.0", licenses)
            self.assertIn("Creative Commons Attribution 4.0 International", licenses)
            self.assertRegex(text, r"upstream license|上游许可证")
            self.assertIn(f"]({REPOSITORY_URL})", contributing)
            self.assertIn(f"]({ARXIV_URL})", contributing)
            self.assertIn(f"[`{RELEASE_TAG}`]({RELEASE_URL})", contributing)
            self.assertIn(f"]({WORKFLOW_URL})", contributing)
        for stale_phrase in (
            "next task",
            "upcoming publication-governance",
            "planned release boundary",
        ):
            self.assertNotIn(stale_phrase, self.english)
        for stale_phrase in ("下一任务", "后续发布治理文件", "计划中的发布边界"):
            self.assertNotIn(stale_phrase, self.chinese)
        self.assertIn(
            "is configured to run on every push and pull request.", self.english
        )
        self.assertIn("已配置为在每次 push 和 pull request 时运行。", self.chinese)
        self.assertNotIn("CI has passed", self.english)
        self.assertNotIn("CI 已通过", self.chinese)
        self.assertNotIn("remain pending", self.english)
        self.assertNotIn("仍处于待办状态", self.chinese)
        self.assertNotRegex(self.chinese, r"Task\s*\d+|任务\s*\d+")

class CurrentReadmeContractTest(unittest.TestCase):
    """Contract checks for the mature, catalog-first README surface."""

    @classmethod
    def setUpClass(cls):
        cls.english = (ROOT / "README.md").read_text(encoding="utf-8")
        cls.chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")

    @staticmethod
    def section(text: str, *headings: str) -> str:
        for heading in headings:
            marker = f"## {heading}"
            if marker in text:
                return text.split(marker, 1)[1].split("\n## ", 1)[0]
        raise AssertionError(f"none of the headings found: {headings}")

    def test_opening_scope_and_definition(self):
        self.assertEqual(self.english.splitlines()[0], "# Skillware Patterns")
        self.assertEqual(self.chinese.splitlines()[0], "# Skillware Patterns")
        self.assertIn("Executable, bilingual pattern-transfer", self.english)
        self.assertIn("Skillware 论文的双语可执行模式迁移补充材料。", self.chinese)
        for text in (self.english, self.chinese):
            self.assertIn(PAPER_TITLE, text)
            self.assertIn("README.md", text)
            self.assertIn("README.zh-CN.md", text)
        self.assertIn(
            "Skillware is the software abstraction that extends software engineering",
            self.english,
        )
        self.assertIn("Skillware 是将软件工程扩展至持久行为制品的软件抽象", self.chinese)

    def test_runtime_boundary_and_obsolete_terms(self):
        boundary = "Behavioral Source -> Skill Artifact -> Skillware Unit -> Agent Host -> Agent Runtime"
        for text in (self.english, self.chinese):
            self.assertIn(boundary, text)
            self.assertNotIn("Agent Execution Core", text)
            self.assertNotIn("Behavioral Compiler", text)

    def test_catalog_metrics_and_flat_navigation(self):
        for phrase in (
            "23 GoF patterns screened",
            "10 detailed GoF implementations",
            "2 patterns from other established traditions",
        ):
            self.assertIn(phrase, self.english)
        self.assertIn("23 GoF patterns screened", self.chinese)
        self.assertIn("10 detailed GoF implementations", self.chinese)
        self.assertIn("2 patterns from other established traditions", self.chinese)
        for text in (self.english, self.chinese):
            self.assertRegex(text, r"(?is)flat|扁平")
            self.assertNotRegex(text, r"(?i)maturity (?:score|rating)|成熟度(?:评分|分数)")

    def test_english_catalog_is_complete_and_linked(self):
        section = self.section(self.english, "Pattern catalog")
        rows = markdown_data_rows(section)
        expected = (
            "Facade", "Adapter", "Composite", "Observer", "State", "Strategy",
            "Decorator", "Template Method", "Memento", "Mediator",
            "Pipes and Filters", "Specification",
        )
        assert_exact_pattern_names(rows, expected)
        assert_exact_row_widths(rows, 7)
        for name, cells in rows:
            self.assertRegex(cells[0], r"patterns/[a-z0-9-]+/definition\.md")
            self.assertRegex(cells[-1], r"patterns/[a-z0-9-]+/sample/")
            self.assertIn(cells[4], {"constructive", "confirmed correspondence", "candidate correspondence", "not observable"})

    def test_upstream_evidence_is_explicit_and_pinned(self):
        evidence = self.section(self.english, "Upstream examples and evidence")
        for pattern in (
            "Facade", "Adapter", "Composite", "Observer", "State", "Strategy",
            "Decorator", "Template Method", "Memento", "Mediator",
        ):
            self.assertIn(pattern, evidence)
        self.assertIn("2026-07-23", evidence)
        self.assertIn("immutable revision", evidence)
        detail = (DOCS / "upstream-skill-evidence.md").read_text(encoding="utf-8")
        for token in ("896224c4b1879920", "11de390be1be6849", "db91727598d08d", "25d22f864ad68"):
            self.assertIn(token, detail)
        self.assertIn("not observable", (ROOT / "patterns/specification/README.md").read_text(encoding="utf-8").lower())

    def test_every_gof_record_separates_case_skill_from_mock_sample(self):
        pattern_ids = (
            "facade", "adapter", "composite", "observer", "state", "strategy",
            "decorator", "template-method", "memento", "mediator",
        )
        for pattern_id in pattern_ids:
            text = (ROOT / "patterns" / pattern_id / "README.md").read_text(
                encoding="utf-8"
            )
            with self.subTest(pattern=pattern_id):
                headings = (
                    "## 1. 先看场景",
                    "## 2. 先看完整 Skill",
                    "## 3. 这个模式解决了什么",
                    "## 4. 市面上的 Skill 案例",
                    "## 5. 这个例子对应哪些角色",
                    "## 6. 什么时候用",
                    "## 7. 运行",
                    "## 8. 边界",
                )
                positions = []
                for heading in headings:
                    self.assertEqual(text.count(heading), 1)
                    positions.append(text.index(heading))
                self.assertEqual(positions, sorted(positions))
                self.assertIn("**Case Skill", text)
                self.assertIn("Mock Skill", text)
                self.assertIn("| 没有 ", text)
                self.assertIn("| 使用 ", text)
                self.assertIn("| 上游 Case Skill | 本地 Mock Skill |", text)
                self.assertIn("SKILL.md", text)
                self.assertIn("participant-map.yaml", text)
                self.assertIn("python3 sample/scripts/run_demo.py", text)

    def test_every_selected_record_has_practical_start_here_surface(self):
        """Every selected record should teach from evidence before abstraction."""
        pattern_ids = (
            "facade", "adapter", "composite", "observer", "state", "strategy",
            "decorator", "template-method", "memento", "mediator",
            "pipes-and-filters", "specification",
        )
        for pattern_id in pattern_ids:
            text = (ROOT / "patterns" / pattern_id / "README.md").read_text(
                encoding="utf-8"
            )
            with self.subTest(pattern=pattern_id):
                for heading in (
                    "## 1. 先看场景",
                    "## 2. 先看完整 Skill",
                    "## 3. 这个模式解决了什么",
                    "## 4. 市面上的 Skill 案例",
                    "## 5. 这个例子对应哪些角色",
                    "## 6. 什么时候用",
                    "## 7. 运行",
                    "## 8. 边界",
                ):
                    self.assertIn(heading, text)
                self.assertIn("**Case Skill", text)
                self.assertIn("Mock Skill", text)
                self.assertIn("| 没有 ", text)
                self.assertIn("| 使用 ", text)
                self.assertIn("| 上游 Case Skill | 本地 Mock Skill |", text)

                sample = (ROOT / "patterns" / pattern_id / "sample" / "README.md").read_text(
                    encoding="utf-8"
                )
                self.assertIn("> **This directory is the mock sample.**", sample)
                self.assertIn("## Evidence at a glance", sample)
                self.assertIn("Evidence layer", sample)
                self.assertIn("Upstream case", sample)
                self.assertIn("Executable proof", sample)
                self.assertIn("## Mock Skill source", sample)
                self.assertIn("## Learn the pattern", sample)
                self.assertIn("| Before:", sample)
                self.assertIn("| After:", sample)
                self.assertIn("### Use it when", sample)
                self.assertIn("### Skill-author recipe", sample)
                self.assertRegex(sample, r"(?s)```(?:markdown|text)\n.*<!--")

    def test_every_mock_sample_has_visual_evidence_map(self):
        pattern_ids = (
            "facade", "adapter", "composite", "observer", "state", "strategy",
            "decorator", "template-method", "memento", "mediator",
            "pipes-and-filters", "specification",
        )
        for pattern_id in pattern_ids:
            text = (
                ROOT / "patterns" / pattern_id / "sample" / "README.md"
            ).read_text(encoding="utf-8")
            with self.subTest(pattern=pattern_id):
                self.assertIn("> **This directory is the mock sample.**", text)
                self.assertIn("## Evidence at a glance", text)
                self.assertIn("```mermaid", text)
                self.assertIn("Evidence layer", text)
                self.assertIn("Upstream case", text)
                self.assertIn("Executable proof", text)
                self.assertIn("SKILL.md", text)
                self.assertIn("scripts/run_demo.py", text)
                self.assertIn("## Mock Skill source", text)
                self.assertIn("sample/", text)
                self.assertRegex(text, r"(?s)```(?:markdown|text)\n.*<!--")
                self.assertIn("## Learn the pattern", text)
                self.assertIn("| Before:", text)
                self.assertIn("| After:", text)
                self.assertIn("Skill-author recipe", text)
                self.assertIn("Use it when", text)

    def test_facade_demo_and_reproducibility_commands(self):
        required_paths = (
            "patterns/facade/sample/SKILL.md",
            "patterns/facade/participant-map.yaml",
            "patterns/facade/sample/expected/incident-result.json",
            "patterns/facade/sample/tests/test_demo.py",
        )
        commands = SETUP_COMMANDS + FACADE_COMMANDS + VALIDATION_COMMANDS
        for text in (self.english, self.chinese):
            for path in required_paths:
                self.assertIn(f"]({path})", text)
            for command in commands:
                self.assertIn(command, text)

    def test_protocol_statuses_limits_and_governance(self):
        english_protocol = self.section(self.english, "Admission protocol")
        english_status = self.section(self.english, "Research boundary and claim statuses")
        chinese_protocol = self.section(self.chinese, "准入协议", "模式迁移准入协议")
        chinese_status = self.section(self.chinese, "研究边界与主张状态", "主张状态")
        for element in ADMISSION_ELEMENTS:
            self.assertIn(element, english_protocol)
            self.assertIn(element, chinese_protocol)
        for status in STATUS_MEANINGS:
            self.assertIn(status, english_status)
            self.assertIn(status, chinese_status)
        self.assertIn("These statuses are descriptive, not a score", english_status)
        self.assertIn("这些状态是描述性的", chinese_status)
        for heading, text in (("Citation", self.english), ("引用", self.chinese)):
            citation = self.section(text, heading)
            self.assertIn("](" + ARXIV_URL + ")", citation)
        for heading, text in (("License", self.english), ("许可证", self.chinese)):
            license_text = self.section(text, heading)
            self.assertIn(LICENSE_BOUNDARY_BLOCK, license_text)
            self.assertIn("](LICENSE-CODE)", license_text)
            self.assertIn("](LICENSE-DOCS)", license_text)
        self.assertIn("## Security", self.english)
        self.assertTrue(
            "## 社区与项目链接" in self.chinese or "## 贡献" in self.chinese
        )

    def test_local_links_and_public_boundary(self):
        for name, text in (("README.md", self.english), ("README.zh-CN.md", self.chinese)):
            for target in local_markdown_links(text):
                self.assertTrue((ROOT / target.split("#", 1)[0]).exists(), f"{name}: {target}")
            self.assertIn(ARXIV_URL, text)
            self.assertIn(REPOSITORY_URL, text)
            self.assertTrue(
                RELEASE_URL in text
                or f"{REPOSITORY_URL}/tree/{RELEASE_TAG}" in text
            )
            self.assertNotIn("arxiv.org/submit", text)
            self.assertNotRegex(text, rf"\[[^]]*{AUTHORING_REVISION}[^]]*\]\([^)]+\)")


if __name__ == "__main__":
    unittest.main()
