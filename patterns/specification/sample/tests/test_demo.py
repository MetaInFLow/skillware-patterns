from copy import deepcopy
from dataclasses import FrozenInstanceError
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


SAMPLE = Path(__file__).resolve().parents[1]
DEMO_PATH = SAMPLE / "scripts/run_demo.py"


class SpecificationDemoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not DEMO_PATH.is_file():
            return
        spec = importlib.util.spec_from_file_location("specification_demo", DEMO_PATH)
        cls.demo = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.demo
        spec.loader.exec_module(cls.demo)

    def require_demo(self):
        self.assertTrue(DEMO_PATH.is_file(), "Specification demo is not implemented")
        return self.demo

    def load_text(self, relative_path):
        return (SAMPLE / relative_path).read_text(encoding="utf-8")

    def test_expense_requires_receipt_budget_and_authority(self):
        demo = self.require_demo()
        policy = demo.HasReceipt() & demo.WithinBudget() & demo.AuthorizedAmount(1000)

        self.assertTrue(
            policy.is_satisfied_by(
                {"receipt": True, "budget": 500, "amount": 400}
            )
        )
        self.assertFalse(
            policy.is_satisfied_by(
                {"receipt": False, "budget": 500, "amount": 400}
            )
        )

    def test_not_operator_is_composable(self):
        demo = self.require_demo()

        self.assertTrue(
            (~demo.Department("restricted")).is_satisfied_by(
                {"department": "sales"}
            )
        )

    def test_or_operator_short_circuits_after_complete_candidate_validation(self):
        demo = self.require_demo()
        policy = demo.HasReceipt() | demo.AuthorizedAmount(100)

        self.assertTrue(
            policy.is_satisfied_by({"receipt": True, "amount": 900})
        )
        self.assertTrue(
            policy.is_satisfied_by({"receipt": False, "amount": 100})
        )
        self.assertFalse(
            policy.is_satisfied_by({"receipt": False, "amount": 101})
        )
        with self.assertRaisesRegex(
            demo.CandidateValidationError,
            "^candidate.amount must be an integer$",
        ):
            policy.is_satisfied_by({"receipt": True, "amount": float("nan")})

    def test_default_policy_is_reusable_deterministic_and_pure(self):
        demo = self.require_demo()
        candidate = {
            "receipt": True,
            "budget": 500,
            "amount": 400,
            "department": "sales",
        }
        original = deepcopy(candidate)

        first = demo.DEFAULT_EXPENSE_POLICY.is_satisfied_by(candidate)
        first_trace = demo.DEFAULT_EXPENSE_POLICY.explain(
            candidate, evaluate_all=True
        )
        second = demo.DEFAULT_EXPENSE_POLICY.is_satisfied_by(candidate)
        second_trace = demo.DEFAULT_EXPENSE_POLICY.explain(
            candidate, evaluate_all=True
        )

        self.assertTrue(first)
        self.assertTrue(second)
        self.assertEqual(first_trace, second_trace)
        self.assertEqual(candidate, original)

    def test_named_leaf_and_composite_specifications_are_immutable(self):
        demo = self.require_demo()
        leaf = demo.AuthorizedAmount(1000)
        composite = demo.HasReceipt() & demo.WithinBudget()

        self.assertEqual(leaf.name, "AuthorizedAmount(1000)")
        self.assertEqual(composite.name, "HasReceipt AND WithinBudget")
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            leaf.maximum = 2
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            composite.specifications = ()

    def test_direct_composite_construction_snapshots_children(self):
        demo = self.require_demo()
        children = [demo.HasReceipt(), demo.AuthorizedAmount(1000)]
        policy = demo.AndSpecification(children)

        children.append(demo.Department("restricted"))

        self.assertIsInstance(policy.specifications, tuple)
        self.assertEqual(policy.name, "HasReceipt AND AuthorizedAmount(1000)")

    def test_mixed_composite_names_preserve_grouping(self):
        demo = self.require_demo()
        policy = (
            (demo.HasReceipt() | demo.AuthorizedAmount(1000))
            & ~demo.Department("restricted")
        )

        self.assertEqual(
            policy.name,
            "(HasReceipt OR AuthorizedAmount(1000)) AND NOT Department('restricted')",
        )

    def test_predicate_is_the_validated_extension_path_for_custom_fields(self):
        demo = self.require_demo()
        required_fields = ["memo"]
        observed = []
        explanation_calls = []

        def evaluate(candidate):
            observed.append(candidate["memo"])
            return candidate["memo"]["text"] == "client dinner"

        def explain(candidate, result):
            explanation_calls.append(result)
            return f"memo text was {candidate['memo']['text']!r}"

        memo = demo.Predicate("MemoIsClientDinner", required_fields, evaluate, explain)
        policy = memo & demo.HasReceipt()
        required_fields.append("amount")
        candidate = {
            "memo": {"text": "client dinner", "tags": ["sales"]},
            "receipt": True,
        }
        original = deepcopy(candidate)

        self.assertEqual(memo.required_fields, ("memo",))
        self.assertEqual(policy.required_fields, ("memo", "receipt"))
        self.assertEqual(policy.name, "MemoIsClientDinner AND HasReceipt")
        self.assertTrue(policy.is_satisfied_by(candidate))
        self.assertEqual(explanation_calls, [])
        trace = policy.explain(candidate, evaluate_all=True)

        self.assertTrue(trace["result"])
        self.assertEqual(
            trace["evaluations"][0],
            {
                "specification": "MemoIsClientDinner",
                "result": True,
                "explanation": "memo text was 'client dinner'",
            },
        )
        self.assertEqual(explanation_calls, [True])
        self.assertEqual(candidate, original)
        self.assertIsNot(observed[0], candidate["memo"])
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            memo.required_fields = ("amount",)

    def test_predicate_configuration_and_results_are_strict(self):
        demo = self.require_demo()
        valid_evaluator = lambda candidate: True
        valid_explanation = lambda candidate, result: "accepted"
        invalid_configurations = (
            ("", ("memo",), valid_evaluator, valid_explanation),
            ("Memo", "memo", valid_evaluator, valid_explanation),
            ("Memo", {"memo"}, valid_evaluator, valid_explanation),
            ("Memo", (), valid_evaluator, valid_explanation),
            ("Memo", ("memo", "memo"), valid_evaluator, valid_explanation),
            ("Memo", ("memo", 1), valid_evaluator, valid_explanation),
            ("Memo", ("memo",), None, valid_explanation),
            ("Memo", ("memo",), valid_evaluator, None),
        )
        for arguments in invalid_configurations:
            with self.subTest(arguments=repr(arguments[:2])):
                with self.assertRaises(demo.SpecificationConfigurationError):
                    demo.Predicate(*arguments)

        bad_result = demo.Predicate(
            "BadResult",
            ("memo",),
            lambda candidate: 1,
            valid_explanation,
        )
        bad_explanation = demo.Predicate(
            "BadExplanation",
            ("memo",),
            valid_evaluator,
            lambda candidate, result: 1,
        )
        with self.assertRaisesRegex(
            demo.SpecificationEvaluationError,
            "^Predicate 'BadResult' evaluator must return a boolean$",
        ):
            bad_result.is_satisfied_by({"memo": "x"})
        with self.assertRaisesRegex(
            demo.SpecificationEvaluationError,
            "^Predicate 'BadExplanation' explanation must return a string$",
        ):
            bad_explanation.explain({"memo": "x"})

    def test_bare_and_unregistered_specification_subclasses_are_rejected(self):
        demo = self.require_demo()

        class MutableSpecification(demo.Specification):
            def __init__(self):
                self.enabled = True

            @property
            def name(self):
                return "Mutable"

            @property
            def required_fields(self):
                return ("receipt",)

            def _evaluate_boolean(self, candidate):
                return self.enabled

            def _evaluate_with_trace(self, candidate, evaluate_all):
                return True, [], [], "mutable"

        base = demo.Specification()
        mutable = MutableSpecification()
        for specification in (base, mutable):
            with self.subTest(specification=type(specification).__name__):
                with self.assertRaisesRegex(
                    demo.SpecificationConfigurationError,
                    "^unsupported Specification implementation: ",
                ):
                    specification.is_satisfied_by({})
                with self.assertRaisesRegex(
                    demo.SpecificationConfigurationError,
                    "^unsupported Specification implementation: ",
                ):
                    demo.HasReceipt() & specification
                with self.assertRaisesRegex(
                    demo.SpecificationConfigurationError,
                    "^unsupported Specification implementation: ",
                ):
                    demo.AndSpecification((demo.HasReceipt(), specification))

    def test_custom_candidate_values_are_bounded_json_data(self):
        demo = self.require_demo()
        predicate = demo.Predicate(
            "MemoPresent",
            ("memo",),
            lambda candidate: candidate["memo"] is not None,
            lambda candidate, result: "memo checked",
        )
        invalid_values = (
            (object(), "candidate.memo must be JSON-compatible"),
            (("tuple",), "candidate.memo must be JSON-compatible"),
            (float("nan"), "candidate.memo must be a finite number"),
            (
                demo.MAX_CUSTOM_INTEGER + 1,
                "candidate.memo integer exceeds absolute bound of 1000000000",
            ),
            (
                "x" * (demo.MAX_CUSTOM_STRING_BYTES + 1),
                "candidate.memo exceeds 4096 UTF-8 bytes",
            ),
        )
        for value, message in invalid_values:
            with self.subTest(value_type=type(value).__name__):
                with self.assertRaisesRegex(
                    demo.CandidateValidationError,
                    f"^{message}$",
                ):
                    predicate.is_satisfied_by({"memo": value})

    def test_explanations_are_structured_and_support_both_evaluation_modes(self):
        demo = self.require_demo()
        policy = demo.HasReceipt() & demo.WithinBudget() & demo.AuthorizedAmount(1000)
        candidate = {"receipt": False, "budget": 500, "amount": 400}

        short = policy.explain(candidate)
        complete = policy.explain(candidate, evaluate_all=True)

        self.assertEqual(
            short,
            {
                "specification": (
                    "HasReceipt AND WithinBudget AND AuthorizedAmount(1000)"
                ),
                "result": False,
                "evaluation": "short-circuit",
                "explanation": "AND failed because HasReceipt was false.",
                "evaluations": [
                    {
                        "specification": "HasReceipt",
                        "result": False,
                        "explanation": "receipt must be true; observed false",
                    }
                ],
                "skipped": ["WithinBudget", "AuthorizedAmount(1000)"],
            },
        )
        self.assertFalse(complete["result"])
        self.assertEqual(complete["evaluation"], "all")
        self.assertEqual(
            [item["specification"] for item in complete["evaluations"]],
            ["HasReceipt", "WithinBudget", "AuthorizedAmount(1000)"],
        )
        self.assertEqual(complete["skipped"], [])

    def test_candidate_fields_are_exact_for_each_composed_policy(self):
        demo = self.require_demo()
        policy = demo.HasReceipt() & demo.WithinBudget() & demo.AuthorizedAmount(1000)

        cases = (
            (
                {"receipt": True, "budget": 500},
                "candidate fields must be exactly: receipt, budget, amount; missing: amount",
            ),
            (
                {"receipt": True, "budget": 500, "amount": 400, "memo": "x"},
                "candidate fields must be exactly: receipt, budget, amount; unexpected: memo",
            ),
        )
        for candidate, message in cases:
            with self.subTest(candidate=candidate):
                with self.assertRaisesRegex(
                    demo.CandidateValidationError,
                    f"^{message}$",
                ):
                    policy.is_satisfied_by(candidate)

    def test_candidate_types_and_bounded_integer_amounts_are_strict(self):
        demo = self.require_demo()
        policy = demo.HasReceipt() & demo.WithinBudget() & demo.AuthorizedAmount(1000)
        base = {"receipt": True, "budget": 500, "amount": 400}
        cases = (
            ("receipt", 1, "candidate.receipt must be a boolean"),
            ("budget", True, "candidate.budget must be an integer"),
            ("budget", -1, "candidate.budget must be between 0 and 1000000000"),
            ("amount", 400.0, "candidate.amount must be an integer"),
            (
                "amount",
                demo.MAX_AMOUNT + 1,
                "candidate.amount must be between 0 and 1000000000",
            ),
        )
        for field, value, message in cases:
            with self.subTest(field=field, value=value):
                candidate = dict(base)
                candidate[field] = value
                with self.assertRaisesRegex(
                    demo.CandidateValidationError,
                    f"^{message}$",
                ):
                    policy.is_satisfied_by(candidate)

    def test_department_requires_valid_bounded_unicode(self):
        demo = self.require_demo()
        with self.assertRaisesRegex(
            demo.CandidateValidationError,
            "^candidate.department must contain valid Unicode$",
        ):
            demo.Department("restricted").is_satisfied_by(
                {"department": "\ud800"}
            )
        with self.assertRaisesRegex(
            demo.CandidateValidationError,
            "^candidate.department exceeds 128 UTF-8 bytes$",
        ):
            demo.Department("restricted").is_satisfied_by(
                {"department": "x" * 129}
            )

    def test_candidate_field_names_must_be_valid_unicode(self):
        demo = self.require_demo()

        with self.assertRaisesRegex(
            demo.CandidateValidationError,
            "^candidate field names must contain valid Unicode$",
        ):
            demo.HasReceipt().is_satisfied_by({"\ud800": True})

    def test_authority_and_department_configuration_are_validated(self):
        demo = self.require_demo()
        for invalid in (True, 1.0, -1, demo.MAX_AMOUNT + 1):
            with self.subTest(maximum=invalid):
                with self.assertRaises(demo.SpecificationConfigurationError):
                    demo.AuthorizedAmount(invalid)
        for invalid in ("", "   ", "x" * 129, "\ud800"):
            with self.subTest(department=repr(invalid)):
                with self.assertRaises(demo.SpecificationConfigurationError):
                    demo.Department(invalid)

    def test_only_specifications_can_be_composed(self):
        demo = self.require_demo()
        for operation in (
            lambda: demo.HasReceipt() & object(),
            lambda: demo.HasReceipt() | object(),
        ):
            with self.assertRaisesRegex(
                TypeError, "^can only compose Specification instances$"
            ):
                operation()

    def test_default_cli_output_is_exact(self):
        self.require_demo()

        completed = subprocess.run(
            [sys.executable, str(DEMO_PATH)],
            cwd=SAMPLE,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stderr, "")
        self.assertEqual(
            completed.stdout,
            self.load_text("expected/approved-expense-result.json"),
        )

    def test_cli_supports_explicit_short_circuit_trace(self):
        self.require_demo()

        completed = subprocess.run(
            [
                sys.executable,
                str(DEMO_PATH),
                "fixtures/valid/missing-receipt.json",
                "--evaluation",
                "short-circuit",
            ],
            cwd=SAMPLE,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 1, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertFalse(result["result"])
        self.assertEqual(result["evaluation"], "short-circuit")
        self.assertEqual(
            [item["specification"] for item in result["evaluations"]],
            ["HasReceipt"],
        )
        self.assertEqual(completed.stderr, "")

    def test_cli_rejects_duplicate_unicode_depth_and_contract_errors_exactly(self):
        self.require_demo()
        cases = (
            ("duplicate-root-member.json", "duplicate-root-member-error.txt"),
            ("duplicate-nested-member.json", "duplicate-nested-member-error.txt"),
            ("lone-surrogate.json", "lone-surrogate-error.txt"),
            ("excessive-depth.json", "excessive-depth-error.txt"),
            ("missing-amount.json", "missing-amount-error.txt"),
            ("extra-field.json", "extra-field-error.txt"),
            ("bool-budget.json", "bool-budget-error.txt"),
            ("float-amount.json", "float-amount-error.txt"),
            ("nan-amount.json", "nan-amount-error.txt"),
            ("invalid-json.json", "invalid-json-error.txt"),
        )
        for fixture, expected in cases:
            with self.subTest(fixture=fixture):
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(DEMO_PATH),
                        f"fixtures/invalid/{fixture}",
                    ],
                    cwd=SAMPLE,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(completed.returncode, 2)
                self.assertEqual(completed.stdout, "")
                self.assertEqual(completed.stderr, self.load_text(f"expected/{expected}"))

    def test_cli_rejects_non_utf8_and_oversized_files(self):
        demo = self.require_demo()
        with TemporaryDirectory() as temp_dir:
            non_utf8 = Path(temp_dir) / "non-utf8.json"
            non_utf8.write_bytes(b'{"receipt":true,"department":"\xff"}')
            oversized = Path(temp_dir) / "oversized.json"
            oversized.write_bytes(b" " * (demo.MAX_INPUT_BYTES + 1))

            non_utf8_run = subprocess.run(
                [sys.executable, str(DEMO_PATH), str(non_utf8)],
                cwd=SAMPLE,
                capture_output=True,
                text=True,
                check=False,
            )
            oversized_run = subprocess.run(
                [sys.executable, str(DEMO_PATH), str(oversized)],
                cwd=SAMPLE,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(non_utf8_run.returncode, 2)
        self.assertEqual(non_utf8_run.stdout, "")
        self.assertEqual(
            non_utf8_run.stderr,
            "ERROR: candidate input must be valid UTF-8\n",
        )
        self.assertEqual(oversized_run.returncode, 2)
        self.assertEqual(oversized_run.stdout, "")
        self.assertEqual(
            oversized_run.stderr,
            "ERROR: candidate input exceeds 65536 bytes\n",
        )

    def test_candidate_loader_reads_only_one_byte_past_the_cap(self):
        demo = self.require_demo()
        payload = json.dumps(
            {
                "receipt": True,
                "budget": 500,
                "amount": 400,
                "department": "sales",
            }
        ).encode("utf-8")
        read_sizes = []

        class ReadSpy(io.BytesIO):
            def read(self, size=-1):
                read_sizes.append(size)
                return super().read(size)

        with patch.object(Path, "open", return_value=ReadSpy(payload)):
            candidate = demo.load_candidate(Path("sentinel.json"))

        self.assertEqual(candidate["amount"], 400)
        self.assertEqual(read_sizes, [demo.MAX_INPUT_BYTES + 1])

    def test_cli_stdout_is_ascii_safe_under_an_ascii_locale(self):
        self.require_demo()
        environment = os.environ.copy()
        environment["PYTHONIOENCODING"] = "ascii:strict"

        completed = subprocess.run(
            [
                sys.executable,
                str(DEMO_PATH),
                "fixtures/valid/unicode-department.json",
            ],
            cwd=SAMPLE,
            capture_output=True,
            env=environment,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stderr, b"")
        completed.stdout.decode("ascii")
        self.assertIn(b"\\u9500\\u552e", completed.stdout)
        self.assertEqual(
            json.loads(completed.stdout)["evaluations"][-1]["result"],
            False,
        )


if __name__ == "__main__":
    unittest.main()
