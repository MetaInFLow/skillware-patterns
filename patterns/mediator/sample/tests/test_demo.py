from copy import deepcopy
import importlib.util
import inspect
import json
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


SAMPLE = Path(__file__).resolve().parents[1]
RECORD = SAMPLE.parent
DEMO_PATH = SAMPLE / "scripts/run_demo.py"
PARTICIPANT_IDS = ("build", "security", "docs", "approval")


class MediatorDemoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not DEMO_PATH.is_file():
            return
        spec = importlib.util.spec_from_file_location("mediator_demo", DEMO_PATH)
        cls.demo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.demo)

    def require_demo(self):
        self.assertTrue(DEMO_PATH.is_file(), "Mediator demo is not implemented")
        return self.demo

    def load_json(self, relative_path):
        return json.loads((SAMPLE / relative_path).read_text(encoding="utf-8"))

    def default_statuses(self):
        return {
            "build": "pass",
            "security": "pass",
            "docs": "pass",
            "approval": "pass",
        }

    def test_release_occurs_only_after_all_colleagues_report_to_mediator(self):
        demo = self.require_demo()

        result = demo.coordinate(self.default_statuses())

        self.assertEqual(result, self.load_json("expected/release-result.json"))
        self.assertEqual(result["decision"], "release")
        self.assertEqual(
            result["communication_path"],
            "participants->mediator->release",
        )

    def test_any_failure_blocks_release(self):
        demo = self.require_demo()

        for participant_id in PARTICIPANT_IDS:
            with self.subTest(participant=participant_id):
                statuses = self.default_statuses()
                statuses[participant_id] = "fail"

                result = demo.coordinate(statuses)

                self.assertEqual(result["decision"], "blocked")
                self.assertEqual(result["statuses"], statuses)

    def test_security_failure_matches_deterministic_fixture(self):
        demo = self.require_demo()

        result = demo.run_workflow(
            self.load_json("fixtures/valid/security-failure.json")
        )

        self.assertEqual(
            result,
            self.load_json("expected/security-failure-result.json"),
        )

    def test_coordinate_copies_statuses_without_mutating_input(self):
        demo = self.require_demo()
        statuses = {
            "approval": "pass",
            "docs": "pass",
            "security": "pass",
            "build": "pass",
        }
        original = deepcopy(statuses)

        first = demo.coordinate(statuses)
        second = demo.coordinate(statuses)

        self.assertEqual(statuses, original)
        self.assertIsNot(first["statuses"], statuses)
        self.assertEqual(list(first["statuses"]), list(PARTICIPANT_IDS))
        self.assertEqual(first, second)

    def test_injected_colleagues_are_addressed_once_in_canonical_order(self):
        demo = self.require_demo()
        calls = []

        def specialist(participant_id):
            def assess(status):
                calls.append((participant_id, status))
                return status

            return assess

        colleagues = [
            demo.Colleague(
                participant_id,
                f"injected:{participant_id}",
                specialist(participant_id),
            )
            for participant_id in reversed(PARTICIPANT_IDS)
        ]

        result = demo.coordinate(self.default_statuses(), colleagues=colleagues)

        self.assertEqual(
            calls,
            [(participant_id, "pass") for participant_id in PARTICIPANT_IDS],
        )
        self.assertEqual(result["decision"], "release")
        for colleague in colleagues:
            self.assertEqual(colleague.mediator_address, "deployment-coordinator")
            self.assertFalse(hasattr(colleague, "peers"))
        self.assertEqual(
            list(inspect.signature(demo.Colleague.report).parameters),
            ["self", "status"],
        )

    def test_callable_colleague_failure_is_isolated_and_fails_closed(self):
        demo = self.require_demo()
        calls = []

        def assess(participant_id):
            def run(status):
                calls.append(participant_id)
                if participant_id == "security":
                    raise RuntimeError("scanner unavailable")
                return status

            return run

        colleagues = [
            demo.Colleague(participant_id, f"injected:{participant_id}", assess(participant_id))
            for participant_id in PARTICIPANT_IDS
        ]

        result = demo.coordinate(self.default_statuses(), colleagues=colleagues)

        self.assertEqual(calls, list(PARTICIPANT_IDS))
        self.assertEqual(result["decision"], "blocked")
        self.assertEqual(
            result["statuses"],
            {
                "build": "pass",
                "security": "fail",
                "docs": "pass",
                "approval": "pass",
            },
        )

    def test_invalid_callable_report_is_isolated_and_fails_closed(self):
        demo = self.require_demo()
        calls = []
        colleagues = []
        for participant_id in PARTICIPANT_IDS:
            value = "unknown" if participant_id == "docs" else "pass"
            colleagues.append(
                demo.Colleague(
                    participant_id,
                    f"injected:{participant_id}",
                    lambda status, item=participant_id, result=value: (
                        calls.append(item) or result
                    ),
                )
            )

        result = demo.coordinate(self.default_statuses(), colleagues=colleagues)

        self.assertEqual(calls, list(PARTICIPANT_IDS))
        self.assertEqual(result["decision"], "blocked")
        self.assertEqual(result["statuses"]["docs"], "fail")

    def test_missing_extra_and_invalid_statuses_are_rejected_before_dispatch(self):
        demo = self.require_demo()
        cases = (
            (
                {"build": "pass", "security": "pass", "docs": "pass"},
                "statuses fields must be exactly: build, security, docs, approval; missing: approval",
            ),
            (
                {**self.default_statuses(), "operations": "pass"},
                "statuses fields must be exactly: build, security, docs, approval; unexpected: operations",
            ),
            (
                {**self.default_statuses(), "security": "PASS"},
                "statuses.security must be 'pass' or 'fail'",
            ),
            (
                {**self.default_statuses(), "approval": True},
                "statuses.approval must be 'pass' or 'fail'",
            ),
        )

        for statuses, message in cases:
            with self.subTest(message=message):
                calls = []
                colleagues = [
                    demo.Colleague(
                        participant_id,
                        f"injected:{participant_id}",
                        lambda status, item=participant_id: calls.append(item) or status,
                    )
                    for participant_id in PARTICIPANT_IDS
                ]
                with self.assertRaisesRegex(
                    demo.CoordinationError,
                    f"^{re.escape(message)}$",
                ):
                    demo.coordinate(statuses, colleagues=colleagues)
                self.assertEqual(calls, [])

    def test_non_mapping_statuses_are_rejected(self):
        demo = self.require_demo()

        for statuses in (None, [], "pass"):
            with self.subTest(statuses=statuses):
                with self.assertRaisesRegex(
                    demo.CoordinationError,
                    "^statuses must be a mapping$",
                ):
                    demo.coordinate(statuses)

    def test_duplicate_missing_extra_and_invalid_colleagues_are_rejected(self):
        demo = self.require_demo()

        def colleague(participant_id):
            return demo.Colleague(participant_id, f"injected:{participant_id}")

        cases = (
            (
                [colleague("build"), colleague("build"), colleague("docs"), colleague("approval")],
                "duplicate colleague participant: build",
            ),
            (
                [colleague("build"), colleague("security"), colleague("docs")],
                "colleague participants must be exactly: build, security, docs, approval; missing: approval",
            ),
            (
                [
                    colleague("build"),
                    colleague("security"),
                    colleague("docs"),
                    colleague("approval"),
                    colleague("operations"),
                ],
                "colleague participants must be exactly: build, security, docs, approval; unexpected: operations",
            ),
            (
                [colleague("build"), colleague("security"), object(), colleague("approval")],
                "colleagues must contain only Colleague instances",
            ),
        )

        for colleagues, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    demo.CoordinationError,
                    f"^{re.escape(message)}$",
                ):
                    demo.coordinate(self.default_statuses(), colleagues=colleagues)

    def test_colleague_cannot_be_shared_between_mediators(self):
        demo = self.require_demo()
        colleague = demo.Colleague("build", "injected:build")
        first = demo.DeploymentCoordinator(
            [
                colleague,
                demo.Colleague("security", "injected:security"),
                demo.Colleague("docs", "injected:docs"),
                demo.Colleague("approval", "injected:approval"),
            ]
        )

        with self.assertRaisesRegex(
            demo.CoordinationError,
            "^colleague build is already bound to another mediator$",
        ):
            demo.DeploymentCoordinator(
                [
                    colleague,
                    demo.Colleague("security", "other:security"),
                    demo.Colleague("docs", "other:docs"),
                    demo.Colleague("approval", "other:approval"),
                ]
            )
        self.assertEqual(first.address, "deployment-coordinator")

    def test_child_skills_report_only_to_mediator(self):
        for participant_id in PARTICIPANT_IDS:
            text = (
                SAMPLE / f"child-skills/{participant_id}/SKILL.md"
            ).read_text(encoding="utf-8")
            with self.subTest(participant=participant_id):
                self.assertIn("Deployment Coordinator", text)
                self.assertIn("Never invoke another participant", text)
                for peer_id in set(PARTICIPANT_IDS) - {participant_id}:
                    self.assertNotIn(f"child-skills/{peer_id}/SKILL.md", text)

    def test_invalid_fixtures_match_exact_cli_errors(self):
        self.require_demo()
        cases = (
            ("missing-approval.json", "missing-approval-error.txt"),
            ("extra-status.json", "extra-status-error.txt"),
            ("invalid-status.json", "invalid-status-error.txt"),
            ("wrong-statuses-type.json", "wrong-statuses-type-error.txt"),
            ("duplicate-build.json", "duplicate-build-error.txt"),
            ("invalid-json.json", "invalid-json-error.txt"),
        )

        for fixture, expected in cases:
            with self.subTest(fixture=fixture):
                completed = subprocess.run(
                    [sys.executable, str(DEMO_PATH), str(SAMPLE / "fixtures/invalid" / fixture)],
                    cwd=SAMPLE,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(completed.returncode, 2)
                self.assertEqual(completed.stdout, "")
                self.assertEqual(
                    completed.stderr,
                    (SAMPLE / "expected" / expected).read_text(encoding="utf-8"),
                )

    def test_non_utf8_cli_error_is_stable(self):
        self.require_demo()
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "statuses.json"
            path.write_bytes(b"\xff")

            completed = subprocess.run(
                [sys.executable, str(DEMO_PATH), str(path)],
                cwd=SAMPLE,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(
            completed.stderr,
            (SAMPLE / "expected/non-utf8-statuses-error.txt").read_text(encoding="utf-8"),
        )

    def test_default_cli_matches_expected_output(self):
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
            (SAMPLE / "expected/release-result.json").read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
