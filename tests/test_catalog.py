from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]

GOF_23 = {
    "abstract-factory",
    "builder",
    "factory-method",
    "prototype",
    "singleton",
    "adapter",
    "bridge",
    "composite",
    "decorator",
    "facade",
    "flyweight",
    "proxy",
    "chain-of-responsibility",
    "command",
    "interpreter",
    "iterator",
    "mediator",
    "memento",
    "observer",
    "state",
    "strategy",
    "template-method",
    "visitor",
}

DETAILED = {
    "facade",
    "adapter",
    "composite",
    "observer",
    "state",
    "strategy",
    "decorator",
    "template-method",
    "memento",
    "mediator",
    "pipes-and-filters",
    "specification",
}

DETAILED_GOF = DETAILED - {"pipes-and-filters", "specification"}

INDEX_FIELDS = {
    "id",
    "name",
    "name_zh",
    "source_tradition",
    "source_category",
    "paper_role",
    "implementation_status",
    "scenario",
    "scenario_zh",
}

SCREEN_FIELDS = {
    "id",
    "name",
    "name_zh",
    "category",
    "source_intent",
    "skillware_carriers",
    "screening_result",
    "reasoning",
    "false_positive_risk",
    "detailed_sample",
}


class CatalogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.screen = yaml.safe_load(
            (ROOT / "catalog/gof-23-screening.yaml").read_text(encoding="utf-8")
        )
        cls.index = yaml.safe_load(
            (ROOT / "catalog/pattern-index.yaml").read_text(encoding="utf-8")
        )

    def test_gof_screen_has_exactly_23_canonical_patterns(self):
        self.assertEqual(len(self.screen), 23)
        self.assertEqual({row["id"] for row in self.screen}, GOF_23)
        self.assertTrue(all(set(row) == SCREEN_FIELDS for row in self.screen))

    def test_detailed_index_matches_paper_claim(self):
        self.assertEqual(len(self.index), 12)
        self.assertEqual({row["id"] for row in self.index}, DETAILED)
        self.assertTrue(all(set(row) == INDEX_FIELDS for row in self.index))

    def test_source_and_paper_role_are_independent(self):
        for row in self.index:
            self.assertIn(
                row["paper_role"], {"main-text", "repository-supplement"}
            )
            self.assertIn(
                row["source_tradition"],
                {
                    "gang-of-four",
                    "pattern-oriented-software-architecture",
                    "domain-driven-design",
                },
            )

    def test_only_constructive_gof_catalog_entries_claim_detailed_samples(self):
        detailed = {row["id"] for row in self.screen if row["detailed_sample"]}
        self.assertEqual(detailed, DETAILED_GOF)


if __name__ == "__main__":
    unittest.main()
