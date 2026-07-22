from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import yaml

from scripts import validate_repository


ROOT = Path(__file__).resolve().parents[1]

DETAILED_METADATA = {
    "facade": (
        "Facade",
        "外观模式",
        "gang-of-four",
        "structural",
        "main-text",
        "detailed",
        "Production Incident Response",
        "生产事故响应",
    ),
    "adapter": (
        "Adapter",
        "适配器模式",
        "gang-of-four",
        "structural",
        "main-text",
        "detailed",
        "Multi-Tracker Issue Publisher",
        "多问题追踪器发布",
    ),
    "composite": (
        "Composite",
        "组合模式",
        "gang-of-four",
        "structural",
        "main-text",
        "detailed",
        "Investment Memo Builder",
        "投资备忘录生成",
    ),
    "observer": (
        "Observer",
        "观察者模式",
        "gang-of-four",
        "behavioral",
        "main-text",
        "detailed",
        "Software Release Notification",
        "软件发布通知",
    ),
    "state": (
        "State",
        "状态模式",
        "gang-of-four",
        "behavioral",
        "main-text",
        "detailed",
        "Vendor Onboarding Workflow",
        "供应商准入流程",
    ),
    "strategy": (
        "Strategy",
        "策略模式",
        "gang-of-four",
        "behavioral",
        "main-text",
        "detailed",
        "Risk-Aware Code Review",
        "风险感知代码审查",
    ),
    "decorator": (
        "Decorator",
        "装饰模式",
        "gang-of-four",
        "structural",
        "repository-supplement",
        "detailed",
        "Contract Review Enhancers",
        "合同审查增强",
    ),
    "template-method": (
        "Template Method",
        "模板方法模式",
        "gang-of-four",
        "behavioral",
        "repository-supplement",
        "detailed",
        "Enterprise RFP Response",
        "企业 RFP 响应",
    ),
    "memento": (
        "Memento",
        "备忘录模式",
        "gang-of-four",
        "behavioral",
        "repository-supplement",
        "detailed",
        "Configuration Migration",
        "配置迁移回滚",
    ),
    "mediator": (
        "Mediator",
        "中介者模式",
        "gang-of-four",
        "behavioral",
        "repository-supplement",
        "detailed",
        "Deployment Coordinator",
        "部署协调",
    ),
    "pipes-and-filters": (
        "Pipes and Filters",
        "管道-过滤器模式",
        "pattern-oriented-software-architecture",
        "architectural",
        "repository-supplement",
        "detailed",
        "Support Ticket Triage",
        "客服工单分流",
    ),
    "specification": (
        "Specification",
        "规约模式",
        "domain-driven-design",
        "domain",
        "repository-supplement",
        "detailed",
        "Expense Approval Policy",
        "费用审批规则",
    ),
}

GOF_SCREENING = {
    "abstract-factory": (
        "Abstract Factory",
        "抽象工厂模式",
        "creational",
        "plausible",
        False,
    ),
    "builder": ("Builder", "建造者模式", "creational", "strong", False),
    "factory-method": (
        "Factory Method",
        "工厂方法模式",
        "creational",
        "plausible",
        False,
    ),
    "prototype": ("Prototype", "原型模式", "creational", "plausible", False),
    "singleton": ("Singleton", "单例模式", "creational", "weak", False),
    "adapter": ("Adapter", "适配器模式", "structural", "strong", True),
    "bridge": ("Bridge", "桥接模式", "structural", "plausible", False),
    "composite": ("Composite", "组合模式", "structural", "strong", True),
    "decorator": ("Decorator", "装饰模式", "structural", "strong", True),
    "facade": ("Facade", "外观模式", "structural", "strong", True),
    "flyweight": ("Flyweight", "享元模式", "structural", "weak", False),
    "proxy": ("Proxy", "代理模式", "structural", "plausible", False),
    "chain-of-responsibility": (
        "Chain of Responsibility",
        "职责链模式",
        "behavioral",
        "plausible",
        False,
    ),
    "command": ("Command", "命令模式", "behavioral", "plausible", False),
    "interpreter": (
        "Interpreter",
        "解释器模式",
        "behavioral",
        "plausible",
        False,
    ),
    "iterator": ("Iterator", "迭代器模式", "behavioral", "weak", False),
    "mediator": ("Mediator", "中介者模式", "behavioral", "strong", True),
    "memento": ("Memento", "备忘录模式", "behavioral", "strong", True),
    "observer": ("Observer", "观察者模式", "behavioral", "strong", True),
    "state": ("State", "状态模式", "behavioral", "strong", True),
    "strategy": ("Strategy", "策略模式", "behavioral", "strong", True),
    "template-method": (
        "Template Method",
        "模板方法模式",
        "behavioral",
        "strong",
        True,
    ),
    "visitor": ("Visitor", "访问者模式", "behavioral", "plausible", False),
}

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

    def test_detailed_index_has_exact_canonical_metadata(self):
        actual = {
            row["id"]: (
                row["name"],
                row["name_zh"],
                row["source_tradition"],
                row["source_category"],
                row["paper_role"],
                row["implementation_status"],
                row["scenario"],
                row["scenario_zh"],
            )
            for row in self.index
        }
        self.assertEqual(len(self.index), len(DETAILED_METADATA))
        self.assertEqual(actual, DETAILED_METADATA)
        self.assertTrue(all(set(row) == INDEX_FIELDS for row in self.index))

    def test_gof_screen_has_exact_canonical_decisions(self):
        actual = {
            row["id"]: (
                row["name"],
                row["name_zh"],
                row["category"],
                row["screening_result"],
                row["detailed_sample"],
            )
            for row in self.screen
        }
        self.assertEqual(len(self.screen), len(GOF_SCREENING))
        self.assertEqual(actual, GOF_SCREENING)
        self.assertTrue(all(set(row) == SCREEN_FIELDS for row in self.screen))

    def test_memento_screening_uses_only_pinned_skillopt_candidate(self):
        memento = next(row for row in self.screen if row["id"] == "memento")
        reasoning = memento["reasoning"]

        self.assertNotIn("EvoZeus", reasoning)
        self.assertIn("b860a5cf88ce75e2bd02ca981ac21fb28cffba83", reasoning)
        self.assertIn("skillopt_sleep/staging.py", reasoning)
        self.assertIn("backs up live files before adoption", reasoning)
        self.assertIn("partial candidate", reasoning)
        self.assertIn("no owned restore path", reasoning)
        self.assertIn("full Memento is unverified", reasoning)

        markdown_row = next(
            line
            for line in (ROOT / "catalog/gof-23-screening.md")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.startswith("| Memento |")
        )
        self.assertNotIn("EvoZeus", markdown_row)

    def test_mediator_screening_uses_only_pinned_financial_services_candidate(self):
        mediator = next(row for row in self.screen if row["id"] == "mediator")
        reasoning = mediator["reasoning"]

        self.assertNotIn("EvoZeus", reasoning)
        self.assertIn("4aa51ed3d379731f8f9beff498d749580372699c", reasoning)
        self.assertIn("managed-agent-cookbooks/gl-reconciler/agent.yaml", reasoning)
        self.assertIn(
            "managed-agent-cookbooks/gl-reconciler/subagents/reader.yaml",
            reasoning,
        )
        self.assertIn(
            "managed-agent-cookbooks/gl-reconciler/subagents/critic.yaml",
            reasoning,
        )
        self.assertIn(
            "managed-agent-cookbooks/gl-reconciler/subagents/resolver.yaml",
            reasoning,
        )
        self.assertIn("scripts/test-cookbooks.sh", reasoning)
        self.assertIn("candidate", reasoning)
        self.assertIn("central orchestration", reasoning)
        self.assertIn("common Colleague contract", reasoning)
        self.assertIn("runtime decision behavior", reasoning)

        markdown_row = next(
            line
            for line in (ROOT / "catalog/gof-23-screening.md")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.startswith("| Mediator |")
        )
        self.assertNotIn("EvoZeus", markdown_row)
        self.assertIn("4aa51ed3d379731f8f9beff498d749580372699c", markdown_row)

    def test_markdown_catalogs_are_generated_from_yaml(self):
        from scripts.render_catalog import render_gof_screen, render_pattern_index

        self.assertEqual(
            render_pattern_index(self.index),
            (ROOT / "catalog/pattern-index.md").read_text(encoding="utf-8"),
        )
        self.assertEqual(
            render_gof_screen(self.screen),
            (ROOT / "catalog/gof-23-screening.md").read_text(encoding="utf-8"),
        )


class ValidatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.valid_screen = yaml.safe_load(
            (ROOT / "catalog/gof-23-screening.yaml").read_text(encoding="utf-8")
        )
        cls.valid_index = yaml.safe_load(
            (ROOT / "catalog/pattern-index.yaml").read_text(encoding="utf-8")
        )

    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "catalog").mkdir()
        self.original_root = validate_repository.ROOT
        validate_repository.ROOT = self.root
        self.write_yaml("gof-23-screening.yaml", self.valid_screen)
        self.write_yaml("pattern-index.yaml", self.valid_index)

    def tearDown(self):
        validate_repository.ROOT = self.original_root
        self.temp_dir.cleanup()

    def write_yaml(self, name, value):
        (self.root / "catalog" / name).write_text(
            yaml.safe_dump(value, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    def test_valid_catalogs_have_no_errors(self):
        self.assertEqual(validate_repository.validate(), [])

    def test_missing_catalog_file_is_actionable(self):
        (self.root / "catalog/gof-23-screening.yaml").unlink()

        self.assertEqual(
            validate_repository.validate(),
            ["missing catalog file: catalog/gof-23-screening.yaml"],
        )

    def test_yaml_parse_error_is_actionable(self):
        (self.root / "catalog/gof-23-screening.yaml").write_text(
            "- [unterminated", encoding="utf-8"
        )

        errors = validate_repository.validate()

        self.assertEqual(len(errors), 1)
        self.assertTrue(
            errors[0].startswith("invalid YAML in catalog/gof-23-screening.yaml:"),
            errors[0],
        )

    def test_non_list_document_is_rejected(self):
        self.write_yaml("gof-23-screening.yaml", {"patterns": self.valid_screen})

        self.assertEqual(
            validate_repository.validate(),
            ["catalog/gof-23-screening.yaml: expected a list of rows"],
        )

    def test_empty_document_is_rejected(self):
        (self.root / "catalog/gof-23-screening.yaml").write_text(
            "", encoding="utf-8"
        )

        self.assertEqual(
            validate_repository.validate(),
            ["catalog/gof-23-screening.yaml: expected a list of rows"],
        )

    def test_non_mapping_row_and_missing_id_are_rejected(self):
        screen = deepcopy(self.valid_screen)
        index = deepcopy(self.valid_index)
        screen[0] = "not a mapping"
        index[0].pop("id")
        self.write_yaml("gof-23-screening.yaml", screen)
        self.write_yaml("pattern-index.yaml", index)

        self.assertEqual(
            validate_repository.validate(),
            [
                "catalog/gof-23-screening.yaml: row 1 must be a mapping",
                "catalog/pattern-index.yaml: row 1 missing required id",
            ],
        )

    def test_wrong_counts_and_duplicate_ids_are_rejected(self):
        screen = deepcopy(self.valid_screen)
        index = deepcopy(self.valid_index)
        screen.append(deepcopy(screen[0]))
        index.append(deepcopy(index[0]))
        self.write_yaml("gof-23-screening.yaml", screen)
        self.write_yaml("pattern-index.yaml", index)

        self.assertEqual(
            validate_repository.validate(),
            [
                "expected 23 GoF rows, found 24",
                "duplicate GoF pattern id 'abstract-factory' at rows 1 and 24",
                "expected 12 detailed rows, found 13",
                "duplicate detailed pattern id 'facade' at rows 1 and 13",
            ],
        )

    def test_main_prints_errors_and_returns_failure(self):
        (self.root / "catalog/pattern-index.yaml").unlink()
        output = StringIO()

        with redirect_stdout(output):
            status = validate_repository.main()

        self.assertEqual(status, 1)
        self.assertEqual(
            output.getvalue(),
            "ERROR: missing catalog file: catalog/pattern-index.yaml\n",
        )


if __name__ == "__main__":
    unittest.main()
