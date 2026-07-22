from copy import deepcopy
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock
import subprocess
import sys
import unittest


SAMPLE = Path(__file__).resolve().parents[1]
DEMO_PATH = SAMPLE / "scripts/run_demo.py"


class StateDemoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not DEMO_PATH.is_file():
            return
        spec = importlib.util.spec_from_file_location("state_demo", DEMO_PATH)
        cls.demo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.demo)

    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.state_path = Path(self.temp_dir.name) / "vendor-state.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def require_demo(self):
        self.assertTrue(DEMO_PATH.is_file(), "State demo is not implemented")
        return self.demo

    def load_json(self, relative_path):
        return json.loads((SAMPLE / relative_path).read_text(encoding="utf-8"))

    def test_new_workflow_persists_draft_state(self):
        demo = self.require_demo()

        workflow = demo.VendorWorkflow(self.state_path, vendor_id="vendor-acme")

        self.assertEqual(workflow.state, "draft")
        self.assertEqual(workflow.revision, 0)
        self.assertEqual(workflow.available_actions, ("verify",))
        self.assertEqual(
            json.loads(self.state_path.read_text(encoding="utf-8")),
            {
                "schema": "vendor-onboarding-state-v1",
                "vendor_id": "vendor-acme",
                "state": "draft",
                "revision": 0,
            },
        )

    def test_valid_vendor_transitions_are_persisted_and_recovered(self):
        demo = self.require_demo()
        workflow = demo.VendorWorkflow(self.state_path, vendor_id="vendor-acme")

        self.assertEqual(workflow.transition("verify")["to"], "verified")
        self.assertEqual(
            demo.VendorWorkflow(self.state_path, vendor_id="vendor-acme").state,
            "verified",
        )
        workflow = demo.VendorWorkflow(self.state_path, vendor_id="vendor-acme")
        self.assertEqual(workflow.transition("approve")["to"], "approved")
        workflow = demo.VendorWorkflow(self.state_path, vendor_id="vendor-acme")
        self.assertEqual(workflow.transition("activate")["to"], "activated")

        recovered = demo.VendorWorkflow(self.state_path, vendor_id="vendor-acme")
        self.assertEqual(recovered.state, "activated")
        self.assertEqual(recovered.revision, 3)
        self.assertEqual(recovered.available_actions, ())

    def test_concrete_states_own_distinct_transition_behavior(self):
        demo = self.require_demo()

        self.assertEqual(demo.DraftState.allowed_actions, ("verify",))
        self.assertEqual(demo.VerifiedState.allowed_actions, ("approve",))
        self.assertEqual(demo.ApprovedState.allowed_actions, ("activate",))
        self.assertEqual(demo.ActivatedState.allowed_actions, ())
        handlers = {
            state_type.handle
            for state_type in (
                demo.DraftState,
                demo.VerifiedState,
                demo.ApprovedState,
                demo.ActivatedState,
            )
        }
        self.assertEqual(len(handlers), 4)

    def test_illegal_transition_is_rejected_without_write(self):
        demo = self.require_demo()
        workflow = demo.VendorWorkflow(self.state_path, vendor_id="vendor-acme")
        original = self.state_path.read_bytes()
        original_stat = self.state_path.stat()

        with mock.patch.object(workflow, "_commit", wraps=workflow._commit) as commit:
            with self.assertRaisesRegex(
                demo.IllegalTransitionError,
                r"^illegal transition: draft -> activate; allowed actions: verify$",
            ):
                workflow.transition("activate")

        commit.assert_not_called()
        self.assertEqual(self.state_path.read_bytes(), original)
        self.assertEqual(self.state_path.stat().st_mtime_ns, original_stat.st_mtime_ns)
        self.assertEqual(workflow.state, "draft")

    def test_failed_atomic_replace_does_not_advance_memory_or_disk(self):
        demo = self.require_demo()
        workflow = demo.VendorWorkflow(self.state_path, vendor_id="vendor-acme")
        original = self.state_path.read_bytes()

        with mock.patch.object(demo.os, "replace", side_effect=OSError("disk unavailable")):
            with self.assertRaisesRegex(OSError, "disk unavailable"):
                workflow.transition("verify")

        self.assertEqual(workflow.state, "draft")
        self.assertEqual(workflow.revision, 0)
        self.assertEqual(self.state_path.read_bytes(), original)
        self.assertEqual(list(self.state_path.parent.glob(".vendor-state.json.*.tmp")), [])

    def test_corrupted_state_is_rejected_without_overwrite(self):
        demo = self.require_demo()
        corrupted = b'{"schema": "vendor-onboarding-state-v1", "state": '
        self.state_path.write_bytes(corrupted)

        with self.assertRaisesRegex(
            demo.CorruptedStateError,
            r"^corrupted state: invalid JSON$",
        ):
            demo.VendorWorkflow(self.state_path, vendor_id="vendor-acme")

        self.assertEqual(self.state_path.read_bytes(), corrupted)

    def test_non_utf8_state_is_rejected_with_stable_error(self):
        demo = self.require_demo()
        corrupted = b"\xff\xfe"
        self.state_path.write_bytes(corrupted)

        with self.assertRaisesRegex(
            demo.CorruptedStateError,
            r"^corrupted state: invalid UTF-8$",
        ):
            demo.VendorWorkflow(self.state_path, vendor_id="vendor-acme")

        self.assertEqual(self.state_path.read_bytes(), corrupted)

    def test_deleted_initialized_state_is_not_silently_recreated(self):
        demo = self.require_demo()
        workflow = demo.VendorWorkflow(self.state_path, vendor_id="vendor-acme")
        self.state_path.unlink()

        with self.assertRaisesRegex(
            demo.CorruptedStateError,
            r"^corrupted state: state record is missing$",
        ):
            workflow.transition("verify")

        self.assertFalse(self.state_path.exists())
        self.assertEqual(workflow.state, "draft")
        self.assertEqual(workflow.revision, 0)

    def test_vendor_identity_mismatch_is_rejected_on_reload(self):
        demo = self.require_demo()
        demo.VendorWorkflow(self.state_path, vendor_id="vendor-acme")

        with self.assertRaisesRegex(
            demo.CorruptedStateError,
            r"^corrupted state: vendor_id mismatch; expected 'vendor-other', found 'vendor-acme'$",
        ):
            demo.VendorWorkflow(self.state_path, vendor_id="vendor-other")

    def test_workflow_fixture_is_deterministic_and_not_mutated(self):
        demo = self.require_demo()
        fixture = self.load_json("fixtures/valid/vendor-onboarding.json")
        original = deepcopy(fixture)

        first = demo.run_vendor_workflow(fixture)
        second = demo.run_vendor_workflow(fixture)

        self.assertEqual(fixture, original)
        self.assertEqual(first, second)
        self.assertEqual(first, self.load_json("expected/vendor-onboarding-result.json"))

    def test_recovery_fixture_uses_persisted_approved_state(self):
        demo = self.require_demo()
        fixture = self.load_json("fixtures/valid/recover-approved.json")

        result = demo.run_vendor_workflow(fixture)

        self.assertEqual(result, self.load_json("expected/recover-approved-result.json"))
        self.assertEqual(result["initial_state"], "approved")
        self.assertEqual(result["recovered_state"], "activated")

    def test_invalid_fixtures_match_exact_cli_errors(self):
        self.require_demo()
        cases = (
            ("fixtures/invalid/illegal-transition.json", "expected/illegal-transition-error.txt"),
            ("fixtures/invalid/corrupted-state.json", "expected/corrupted-state-error.txt"),
            ("fixtures/invalid/malformed-workflow.json", "expected/malformed-workflow-error.txt"),
            ("fixtures/invalid/state-list.json", "expected/invalid-state-type-error.txt"),
            ("fixtures/invalid/state-object.json", "expected/invalid-state-type-error.txt"),
            ("fixtures/invalid/state-null.json", "expected/invalid-state-type-error.txt"),
            ("fixtures/invalid/unsupported-schema.json", "expected/unsupported-schema-error.txt"),
        )

        for fixture_path, expected_path in cases:
            with self.subTest(fixture=fixture_path):
                completed = subprocess.run(
                    [sys.executable, str(DEMO_PATH), fixture_path],
                    cwd=SAMPLE,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(completed.returncode, 2)
                self.assertEqual(completed.stdout, "")
                self.assertEqual(
                    completed.stderr,
                    (SAMPLE / expected_path).read_text(encoding="utf-8"),
                )

    def test_non_utf8_workflow_fixture_matches_stable_cli_error(self):
        self.require_demo()
        fixture_path = Path(self.temp_dir.name) / "non-utf8-workflow.json"
        fixture_path.write_bytes(b"\xff\xfe")

        completed = subprocess.run(
            [sys.executable, str(DEMO_PATH), str(fixture_path)],
            cwd=SAMPLE,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(
            completed.stderr,
            (SAMPLE / "expected/non-utf8-workflow-error.txt").read_text(
                encoding="utf-8"
            ),
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
            (SAMPLE / "expected/vendor-onboarding-result.json").read_text(
                encoding="utf-8"
            ),
        )


if __name__ == "__main__":
    unittest.main()
