from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


SAMPLE = Path(__file__).resolve().parents[1]
DEMO_PATH = SAMPLE / "scripts/run_demo.py"
OBSERVER_IDS = ("audit", "changelog", "team-notification")


class ObserverDemoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not DEMO_PATH.is_file():
            return
        spec = importlib.util.spec_from_file_location("observer_demo", DEMO_PATH)
        cls.demo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.demo)

    def require_demo(self):
        self.assertTrue(DEMO_PATH.is_file(), "Observer demo is not implemented")
        return self.demo

    def load_json(self, relative_path):
        return json.loads((SAMPLE / relative_path).read_text(encoding="utf-8"))

    def test_release_notifies_registered_observers_in_registration_order(self):
        demo = self.require_demo()
        workflow = self.load_json("fixtures/valid/release.json")

        result = demo.run_release_workflow(workflow)

        self.assertEqual(result, self.load_json("expected/release-result.json"))
        self.assertEqual(
            [delivery["observer_id"] for delivery in result["deliveries"]],
            list(OBSERVER_IDS),
        )
        self.assertEqual(
            [delivery["status"] for delivery in result["deliveries"]],
            ["delivered", "delivered", "delivered"],
        )

    def test_unregistration_excludes_observer_from_current_delivery(self):
        demo = self.require_demo()
        workflow = self.load_json("fixtures/valid/release-after-unregistration.json")

        result = demo.run_release_workflow(workflow)

        self.assertEqual(
            result,
            self.load_json("expected/release-after-unregistration-result.json"),
        )
        self.assertEqual(
            [delivery["observer_id"] for delivery in result["deliveries"]],
            ["audit", "team-notification"],
        )

    def test_plan_api_normalizes_v_prefix_and_accepts_none_callbacks(self):
        demo = self.require_demo()
        observed = []

        def audit(event):
            observed.append(("audit", event["type"], event["version"]))

        def changelog(event):
            observed.append(("changelog", event["type"], event["version"]))

        deliveries = demo.publish_release("v1.2.0", [audit, changelog])

        self.assertEqual(deliveries, {"audit": "delivered", "changelog": "delivered"})
        self.assertEqual(
            observed,
            [
                ("audit", "release.published.v1", "1.2.0"),
                ("changelog", "release.published.v1", "1.2.0"),
            ],
        )

    def test_plan_api_isolates_callback_failure(self):
        demo = self.require_demo()
        calls = []

        def audit(event):
            calls.append("audit")

        def broken_notifier(event):
            calls.append("broken_notifier")
            raise RuntimeError("notification unavailable")

        def changelog(event):
            calls.append("changelog")

        deliveries = demo.publish_release(
            "v1.2.0", [audit, broken_notifier, changelog]
        )

        self.assertEqual(
            deliveries,
            {
                "audit": "delivered",
                "broken_notifier": "failed",
                "changelog": "delivered",
            },
        )
        self.assertEqual(calls, ["audit", "broken_notifier", "changelog"])

    def test_semver_accepts_prerelease_and_build_metadata(self):
        demo = self.require_demo()
        workflow = self.load_json("fixtures/valid/release-build-metadata.json")

        result = demo.run_release_workflow(workflow)

        self.assertEqual(
            result,
            self.load_json("expected/release-build-metadata-result.json"),
        )

    def test_semver_rejects_invalid_prerelease_identifiers(self):
        demo = self.require_demo()
        release = self.load_json("fixtures/valid/release.json")["release"]

        for version in ("1.2.0-01", "1.2.0-alpha..1"):
            with self.subTest(version=version):
                invalid = deepcopy(release)
                invalid["version"] = version
                with self.assertRaisesRegex(
                    demo.ValidationError,
                    "release.version must be a semantic version",
                ):
                    demo.validate_release(invalid)

    def test_rfc3339_utc_timestamp_rejects_impossible_date_and_time(self):
        demo = self.require_demo()
        release = self.load_json("fixtures/valid/release.json")["release"]

        for published_at in (
            "2026-02-30T08:00:00Z",
            "2026-07-22T25:00:00Z",
        ):
            with self.subTest(published_at=published_at):
                invalid = deepcopy(release)
                invalid["published_at"] = published_at
                with self.assertRaisesRegex(
                    demo.ValidationError,
                    "release.published_at must be an RFC 3339 UTC timestamp",
                ):
                    demo.validate_release(invalid)

    def test_rfc3339_utc_timestamp_accepts_fractional_seconds(self):
        demo = self.require_demo()
        release = self.load_json("fixtures/valid/release.json")["release"]
        release["published_at"] = "2026-07-22T08:00:00.123Z"

        self.assertIs(demo.validate_release(release), release)

    def test_observer_failure_is_isolated_and_accounted(self):
        demo = self.require_demo()
        workflow = self.load_json("fixtures/valid/release.json")
        calls = []

        def audit(event):
            calls.append("audit")
            return "audit-ok"

        def broken_changelog(event):
            calls.append("changelog")
            raise RuntimeError("changelog storage unavailable")

        def notify(event):
            calls.append("team-notification")
            return "team-ok"

        result = demo.run_release_workflow(
            workflow,
            observer_updates={
                "child-skills/audit/SKILL.md": audit,
                "child-skills/changelog/SKILL.md": broken_changelog,
                "child-skills/team-notification/SKILL.md": notify,
            },
        )

        self.assertEqual(calls, list(OBSERVER_IDS))
        self.assertEqual(
            result,
            self.load_json("expected/release-with-failure-result.json"),
        )
        self.assertEqual(result["summary"], {"attempted": 3, "delivered": 2, "failed": 1})

    def test_nested_publication_is_rejected_without_stopping_later_observers(self):
        demo = self.require_demo()
        release = self.load_json("fixtures/valid/release.json")["release"]
        subject = demo.ReleaseSubject()
        calls = []

        subject.register("audit", "injected:audit", lambda event: calls.append("audit") or "ok")

        def reenter(event):
            calls.append("reentrant")
            subject.publish(release)

        subject.register("reentrant", "injected:reentrant", reenter)
        subject.register("changelog", "injected:changelog", lambda event: calls.append("changelog") or "ok")

        result = subject.publish(release)

        self.assertEqual(calls, ["audit", "reentrant", "changelog"])
        self.assertEqual(
            [delivery["status"] for delivery in result["deliveries"]],
            ["delivered", "failed", "delivered"],
        )
        self.assertEqual(
            result["deliveries"][1]["error"],
            "publication re-entry is not allowed",
        )

        second = subject.publish(release)
        self.assertEqual(
            [delivery["status"] for delivery in second["deliveries"]],
            ["delivered", "failed", "delivered"],
        )
        self.assertEqual(
            calls,
            ["audit", "reentrant", "changelog"] * 2,
        )

    def test_registration_during_delivery_is_isolated_and_state_recovers(self):
        demo = self.require_demo()
        release = self.load_json("fixtures/valid/release.json")["release"]
        subject = demo.ReleaseSubject()
        calls = []

        def register_late(event):
            calls.append("registrar")
            subject.register("late", "injected:late", lambda item: "late")

        subject.register("registrar", "injected:registrar", register_late)
        subject.register("audit", "injected:audit", lambda event: calls.append("audit") or "ok")

        first = subject.publish(release)
        second = subject.publish(release)

        self.assertEqual(subject.registered_observer_ids, ("registrar", "audit"))
        self.assertEqual(
            [delivery["status"] for delivery in first["deliveries"]],
            ["failed", "delivered"],
        )
        self.assertEqual(
            first["deliveries"][0]["error"],
            "subscription changes are not allowed during publication",
        )
        self.assertEqual(
            [delivery["status"] for delivery in second["deliveries"]],
            ["failed", "delivered"],
        )
        self.assertEqual(calls, ["registrar", "audit", "registrar", "audit"])

    def test_unregistration_during_delivery_is_isolated_and_state_recovers(self):
        demo = self.require_demo()
        release = self.load_json("fixtures/valid/release.json")["release"]
        subject = demo.ReleaseSubject()
        calls = []

        def unregister_audit(event):
            calls.append("unsubscriber")
            subject.unregister("audit")

        subject.register("unsubscriber", "injected:unsubscriber", unregister_audit)
        subject.register("audit", "injected:audit", lambda event: calls.append("audit") or "ok")

        first = subject.publish(release)
        second = subject.publish(release)

        self.assertEqual(subject.registered_observer_ids, ("unsubscriber", "audit"))
        self.assertEqual(
            [delivery["status"] for delivery in first["deliveries"]],
            ["failed", "delivered"],
        )
        self.assertEqual(
            first["deliveries"][0]["error"],
            "subscription changes are not allowed during publication",
        )
        self.assertEqual(
            [delivery["status"] for delivery in second["deliveries"]],
            ["failed", "delivered"],
        )
        self.assertEqual(calls, ["unsubscriber", "audit", "unsubscriber", "audit"])

    def test_each_observer_receives_an_isolated_event_copy(self):
        demo = self.require_demo()
        release = self.load_json("fixtures/valid/release.json")["release"]
        subject = demo.ReleaseSubject()
        observed = []

        def mutating_observer(event):
            event["version"] = "tampered"
            event["notes"].append("tampered")
            return "mutated-local-copy"

        def recording_observer(event):
            observed.append(event)
            return "recorded"

        subject.register("mutator", "injected:mutator", mutating_observer)
        subject.register("recorder", "injected:recorder", recording_observer)

        result = subject.publish(release)

        self.assertEqual(observed, [result["event"]])
        self.assertEqual(result["event"]["version"], "1.2.0")
        self.assertEqual(len(result["event"]["notes"]), 2)

    def test_workflow_and_release_input_are_not_mutated(self):
        demo = self.require_demo()
        workflow = self.load_json("fixtures/valid/release.json")
        original = deepcopy(workflow)

        first = demo.run_release_workflow(workflow)
        second = demo.run_release_workflow(workflow)

        self.assertEqual(workflow, original)
        self.assertEqual(first, second)

    def test_registration_rejects_duplicate_and_unknown_unregistration(self):
        demo = self.require_demo()
        subject = demo.ReleaseSubject()
        subject.register("audit", "injected:audit", lambda event: "ok")

        with self.assertRaisesRegex(
            demo.ValidationError, "observer 'audit' is already registered"
        ):
            subject.register("audit", "injected:other", lambda event: "other")
        with self.assertRaisesRegex(
            demo.ValidationError, "observer 'missing' is not registered"
        ):
            subject.unregister("missing")

    def test_invalid_fixtures_match_exact_cli_errors(self):
        self.require_demo()
        cases = (
            ("fixtures/invalid/invalid-json.json", "expected/invalid-json-error.txt"),
            ("fixtures/invalid/wrong-event-type.json", "expected/wrong-event-type-error.txt"),
            ("fixtures/invalid/duplicate-registration.json", "expected/duplicate-registration-error.txt"),
            ("fixtures/invalid/unknown-observer-skill.json", "expected/unknown-observer-skill-error.txt"),
            ("fixtures/invalid/unregistered-observer.json", "expected/unregistered-observer-error.txt"),
            ("fixtures/invalid/malformed-release.json", "expected/malformed-release-error.txt"),
            ("fixtures/invalid/invalid-prerelease-zero.json", "expected/invalid-semver-error.txt"),
            ("fixtures/invalid/invalid-prerelease-empty.json", "expected/invalid-semver-error.txt"),
            ("fixtures/invalid/impossible-published-date.json", "expected/invalid-published-at-error.txt"),
            ("fixtures/invalid/impossible-published-time.json", "expected/invalid-published-at-error.txt"),
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
