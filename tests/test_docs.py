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
    "constructive": "repository sample demonstrates mapping can be built",
    "confirmed correspondence": (
        "fixed-revision source evidence satisfies participant relation"
    ),
    "candidate correspondence": (
        "partial source evidence exists but participant/behavior unverified"
    ),
    "unsupported": "evidence contradicts or fails source pattern contract",
    "not observable": "relation cannot be evaluated from available artifacts",
}

MAIN_TEXT_PATTERNS = (
    "Facade",
    "Adapter",
    "Composite",
    "Observer",
    "State",
    "Strategy",
)

DETAILED_PATTERN_PATHS = (
    "patterns/facade/",
    "patterns/adapter/",
    "patterns/composite/",
    "patterns/observer/",
    "patterns/state/",
    "patterns/strategy/",
    "patterns/decorator/",
    "patterns/template-method/",
    "patterns/memento/",
    "patterns/mediator/",
    "patterns/pipes-and-filters/",
    "patterns/specification/",
)


def read_doc(name: str) -> str:
    return (DOCS / name).read_text(encoding="utf-8")


class MethodologyDocsTest(unittest.TestCase):
    def test_required_methodology_documents_exist(self):
        for name in REQUIRED_DOCS:
            with self.subTest(name=name):
                self.assertTrue((DOCS / name).is_file(), name)

    def test_skillware_definition_uses_final_ontology_and_conditions(self):
        text = read_doc("skillware-definition.md")
        chain = " -> ".join(ONTOLOGY)

        self.assertIn(chain, text)
        for heading in (
            "C1: Skill-centered behavioral primacy",
            "C2: Independent software identity",
            "C3: Agent Host execution relationship",
            "Lifecycle Continuity",
        ):
            with self.subTest(heading=heading):
                self.assertIn(heading, text)
        self.assertIn(
            "Skillware is the software abstraction extending software engineering "
            "to persistent Behavioral Artifacts.",
            text,
        )
        self.assertNotRegex(text, r"(?i)\bA Skill is\b|\bSkill means\b")

    def test_methodology_docs_exclude_outdated_terms(self):
        for name in REQUIRED_DOCS:
            text = read_doc(name)
            with self.subTest(name=name):
                self.assertNotIn("Agent Execution Core", text)
                self.assertNotIn("Behavioral Compiler", text)

    def test_transfer_protocol_has_exact_standalone_admission_elements(self):
        text = read_doc("pattern-transfer-protocol.md")
        lines = text.splitlines()

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
                    rf"(?m)^{re.escape(status)} = {re.escape(meaning)}$",
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

    def test_paper_map_covers_claims_roles_and_repository_paths(self):
        text = read_doc("paper-map.md")

        self.assertIn("Section 5.3", text)
        self.assertIn("Table 5", text)
        for pattern in MAIN_TEXT_PATTERNS:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)
        self.assertIn("ten detailed GoF implementations", text)
        self.assertIn("Pipes and Filters", text)
        self.assertIn("Specification", text)
        self.assertIn("no circular evidence", text.lower())
        for path in DETAILED_PATTERN_PATHS:
            with self.subTest(path=path):
                self.assertIn(path, text)

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
