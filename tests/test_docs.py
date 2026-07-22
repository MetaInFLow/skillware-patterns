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
        "Strong structural candidate.",
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


if __name__ == "__main__":
    unittest.main()
