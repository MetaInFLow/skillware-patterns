import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest import mock
import unittest


SAMPLE = Path(__file__).resolve().parents[1]
RECORD = SAMPLE.parent
DEMO_PATH = SAMPLE / "scripts/run_demo.py"


class MementoDemoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not DEMO_PATH.is_file():
            return
        spec = importlib.util.spec_from_file_location("memento_demo", DEMO_PATH)
        cls.demo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.demo)

    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.config = Path(self.temp_dir.name) / "service.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def require_demo(self):
        self.assertTrue(DEMO_PATH.is_file(), "Memento demo is not implemented")
        return self.demo

    def write_config(self, raw=b'{"version":1,"endpoint":"stable"}'):
        self.config.write_bytes(raw)
        return raw

    def test_failed_migration_restores_exact_prior_configuration(self):
        demo = self.require_demo()
        original = {"version": 1, "endpoint": "stable"}
        self.config.write_text(json.dumps(original))

        with self.assertRaises(RuntimeError):
            demo.migrate(self.config, fail=True)

        self.assertEqual(json.loads(self.config.read_text()), original)

    def test_failed_migration_restores_exact_bytes_and_permissions(self):
        demo = self.require_demo()
        original = b'{\n  "endpoint": "stable",  "version": 1\n}\n'
        self.write_config(original)
        os.chmod(self.config, 0o640)

        with self.assertRaisesRegex(RuntimeError, r"^migration failed$"):
            demo.migrate(self.config, fail=True)

        self.assertEqual(self.config.read_bytes(), original)
        if os.name == "posix":
            self.assertEqual(stat.S_IMODE(self.config.stat().st_mode), 0o640)
        self.assertEqual(list(self.config.parent.glob(".service.json.*.tmp")), [])

    def test_success_increments_version_once_and_never_restores(self):
        demo = self.require_demo()
        self.write_config()

        with mock.patch.object(
            demo.ConfigurationOriginator,
            "restore",
            autospec=True,
        ) as restore:
            result = demo.migrate(self.config)

        restore.assert_not_called()
        self.assertEqual(
            result,
            {
                "status": "migrated",
                "from_version": 1,
                "to_version": 2,
                "endpoint": "stable",
                "restored": False,
            },
        )
        self.assertEqual(
            self.config.read_bytes(),
            b'{\n  "endpoint": "stable",\n  "version": 2\n}\n',
        )

    def test_originator_encapsulates_state_and_memento_is_opaque(self):
        demo = self.require_demo()
        self.write_config()
        originator = demo.ConfigurationOriginator(self.config)
        caretaker = demo.MigrationCaretaker(originator)

        checkpoint = caretaker.capture()

        self.assertIsInstance(checkpoint, demo.ConfigurationMemento)
        self.assertNotIn("state", vars(originator))
        for public_name in ("bytes", "content", "payload", "state", "checksum"):
            self.assertFalse(hasattr(checkpoint, public_name))
        self.assertNotIn("stable", repr(checkpoint))
        self.assertTrue(caretaker.has_checkpoint)

    def test_preparation_returns_only_an_opaque_token(self):
        demo = self.require_demo()
        self.write_config()
        originator = demo.ConfigurationOriginator(self.config)
        caretaker = demo.MigrationCaretaker(originator)
        checkpoint = caretaker.capture()

        prepared = caretaker.prepare_migration(checkpoint)

        self.assertIsInstance(prepared, demo.PreparedMigration)
        self.assertNotIsInstance(prepared, tuple)
        self.assertEqual(repr(prepared), "PreparedMigration(<opaque>)")
        for public_name in (
            "configuration",
            "payload",
            "bytes",
            "mode",
            "target",
            "memento",
            "owner",
        ):
            self.assertFalse(hasattr(prepared, public_name))
        with self.assertRaises(AttributeError):
            prepared.payload = b"tampered"

    def test_tuple_and_forged_prepared_tokens_cannot_mutate_originator(self):
        demo = self.require_demo()
        original = self.write_config()
        os.chmod(self.config, 0o640)
        originator = demo.ConfigurationOriginator(self.config)
        caretaker = demo.MigrationCaretaker(originator)
        checkpoint = caretaker.capture()
        owner = caretaker._owner_token
        forged = object.__new__(demo.PreparedMigration)
        attempts = (
            (
                ({"version": 1}, {"version": 99}, b"malicious", 0o777),
                "prepared migration token is invalid",
            ),
            (forged, "prepared migration token is unknown or already consumed"),
        )

        for token, message in attempts:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    demo.PreparedMigrationError,
                    f"^{re.escape(message)}$",
                ):
                    originator.write_prepared(token, checkpoint, owner)
                self.assertEqual(self.config.read_bytes(), original)
                if os.name == "posix":
                    self.assertEqual(stat.S_IMODE(self.config.stat().st_mode), 0o640)
                self.assertEqual(
                    originator._configuration,
                    {"version": 1, "endpoint": "stable"},
                )

    def test_tampered_prepared_token_cannot_mutate_originator(self):
        demo = self.require_demo()
        original = self.write_config()
        os.chmod(self.config, 0o640)
        originator = demo.ConfigurationOriginator(self.config)
        caretaker = demo.MigrationCaretaker(originator)
        checkpoint = caretaker.capture()
        prepared = caretaker.prepare_migration(checkpoint)
        object.__setattr__(
            prepared,
            "_PreparedMigration__seal",
            object(),
        )

        with self.assertRaisesRegex(
            demo.PreparedMigrationError,
            r"^prepared migration token integrity check failed$",
        ):
            originator.write_prepared(
                prepared,
                checkpoint,
                caretaker._owner_token,
            )

        self.assertEqual(self.config.read_bytes(), original)
        if os.name == "posix":
            self.assertEqual(stat.S_IMODE(self.config.stat().st_mode), 0o640)
        self.assertEqual(
            originator._configuration,
            {"version": 1, "endpoint": "stable"},
        )

    def test_prepared_token_is_consumed_before_first_write_attempt(self):
        demo = self.require_demo()
        self.write_config()
        originator = demo.ConfigurationOriginator(self.config)
        caretaker = demo.MigrationCaretaker(originator)
        checkpoint = caretaker.capture()
        prepared = caretaker.prepare_migration(checkpoint)

        first = originator.write_prepared(
            prepared,
            checkpoint,
            caretaker._owner_token,
        )
        first_bytes = self.config.read_bytes()
        with mock.patch.object(demo, "atomic_replace") as replace:
            with self.assertRaisesRegex(
                demo.PreparedMigrationError,
                r"^prepared migration token is unknown or already consumed$",
            ):
                originator.write_prepared(
                    prepared,
                    checkpoint,
                    caretaker._owner_token,
                )

        replace.assert_not_called()
        self.assertEqual(first[0]["version"], 1)
        self.assertEqual(first[1]["version"], 2)
        self.assertEqual(self.config.read_bytes(), first_bytes)
        self.assertEqual(
            json.loads(first_bytes.decode("utf-8")),
            {"endpoint": "stable", "version": 2},
        )

    def test_caretaker_rejects_stale_and_cross_target_mementos(self):
        demo = self.require_demo()
        self.write_config()
        other_path = Path(self.temp_dir.name) / "other.json"
        other_path.write_bytes(b'{"version":7,"endpoint":"other"}')
        first = demo.MigrationCaretaker(demo.ConfigurationOriginator(self.config))
        other = demo.MigrationCaretaker(demo.ConfigurationOriginator(other_path))
        checkpoint = first.capture()

        with self.assertRaisesRegex(
            demo.MementoLifecycleError,
            r"^memento does not belong to this caretaker$",
        ):
            other.restore(checkpoint)

        first.commit(checkpoint)
        self.assertFalse(first.has_checkpoint)
        with self.assertRaisesRegex(
            demo.MementoLifecycleError,
            r"^memento is no longer active$",
        ):
            first.restore(checkpoint)
        with self.assertRaisesRegex(
            demo.MementoLifecycleError,
            r"^memento is no longer active$",
        ):
            first.commit(checkpoint)

    def test_caretaker_allows_only_one_live_checkpoint(self):
        demo = self.require_demo()
        self.write_config()
        caretaker = demo.MigrationCaretaker(
            demo.ConfigurationOriginator(self.config)
        )
        caretaker.capture()

        with self.assertRaisesRegex(
            demo.MementoLifecycleError,
            r"^caretaker already owns an active memento$",
        ):
            caretaker.capture()

    def test_caretaker_commit_and_discard_reject_corrupted_memento(self):
        demo = self.require_demo()

        for operation_name in ("commit", "discard"):
            with self.subTest(operation=operation_name):
                path = Path(self.temp_dir.name) / f"{operation_name}.json"
                original = b'{"version":1,"endpoint":"stable"}'
                path.write_bytes(original)
                os.chmod(path, 0o640)
                originator = demo.ConfigurationOriginator(path)
                caretaker = demo.MigrationCaretaker(originator)
                checkpoint = caretaker.capture()
                checkpoint._raw = b'{"version":9,"endpoint":"tampered"}'

                with self.assertRaisesRegex(
                    demo.MementoIntegrityError,
                    r"^memento checksum does not match captured bytes$",
                ):
                    getattr(caretaker, operation_name)(checkpoint)

                self.assertTrue(caretaker.has_checkpoint)
                self.assertTrue(checkpoint._active)
                self.assertEqual(path.read_bytes(), original)
                if os.name == "posix":
                    self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o640)
                self.assertEqual(
                    originator._configuration,
                    {"version": 1, "endpoint": "stable"},
                )

    def test_cross_target_restore_is_rejected_even_inside_originator(self):
        demo = self.require_demo()
        self.write_config()
        other_path = Path(self.temp_dir.name) / "other.json"
        other_path.write_bytes(b'{"version":7,"endpoint":"other"}')
        first_originator = demo.ConfigurationOriginator(self.config)
        caretaker = demo.MigrationCaretaker(first_originator)
        checkpoint = caretaker.capture()

        with self.assertRaisesRegex(
            demo.MementoTargetError,
            r"^memento target does not match originator$",
        ):
            demo.ConfigurationOriginator(other_path).restore(
                checkpoint,
                caretaker._owner_token,
            )

        self.assertEqual(other_path.read_bytes(), b'{"version":7,"endpoint":"other"}')

    def test_originator_rejects_direct_stale_memento_bypass(self):
        demo = self.require_demo()
        self.write_config()
        originator = demo.ConfigurationOriginator(self.config)
        caretaker = demo.MigrationCaretaker(originator)
        checkpoint = caretaker.capture()
        owner_capability = caretaker._owner_token
        prepared = originator.prepare_migration(checkpoint, owner_capability)
        caretaker.commit(checkpoint)

        operations = (
            lambda: originator.prepare_migration(checkpoint, owner_capability),
            lambda: originator.write_prepared(
                prepared,
                checkpoint,
                owner_capability,
            ),
            lambda: originator.restore(checkpoint, owner_capability),
        )
        for operation in operations:
            with self.subTest(operation=operation):
                with self.assertRaisesRegex(
                    demo.MementoLifecycleError,
                    r"^memento is no longer active$",
                ):
                    operation()

    def test_originator_rejects_direct_foreign_owner_bypass(self):
        demo = self.require_demo()
        self.write_config()
        originator = demo.ConfigurationOriginator(self.config)
        caretaker = demo.MigrationCaretaker(originator)
        checkpoint = caretaker.capture()
        prepared = originator.prepare_migration(
            checkpoint,
            caretaker._owner_token,
        )
        foreign_capability = object()

        operations = (
            lambda: originator.prepare_migration(checkpoint, foreign_capability),
            lambda: originator.write_prepared(
                prepared,
                checkpoint,
                foreign_capability,
            ),
            lambda: originator.restore(checkpoint, foreign_capability),
        )
        for operation in operations:
            with self.subTest(operation=operation):
                with self.assertRaisesRegex(
                    demo.MementoLifecycleError,
                    r"^memento does not belong to this caretaker$",
                ):
                    operation()

    def test_originator_rejects_corrupted_snapshot_before_migration_or_restore(self):
        demo = self.require_demo()

        for operation_name in ("prepare_migration", "write_prepared", "restore"):
            with self.subTest(operation=operation_name):
                path = Path(self.temp_dir.name) / f"{operation_name}.json"
                original = b'{"version":1,"endpoint":"stable"}'
                path.write_bytes(original)
                originator = demo.ConfigurationOriginator(path)
                caretaker = demo.MigrationCaretaker(originator)
                checkpoint = caretaker.capture()
                prepared = originator.prepare_migration(
                    checkpoint,
                    caretaker._owner_token,
                )
                checkpoint._raw = b'{"version":9,"endpoint":"tampered"}'

                with self.assertRaisesRegex(
                    demo.MementoIntegrityError,
                    r"^memento checksum does not match captured bytes$",
                ):
                    if operation_name == "write_prepared":
                        originator.write_prepared(
                            prepared,
                            checkpoint,
                            caretaker._owner_token,
                        )
                    else:
                        getattr(originator, operation_name)(
                            checkpoint,
                            caretaker._owner_token,
                        )

                self.assertEqual(path.read_bytes(), original)

    def test_external_change_before_write_is_preserved_without_restore(self):
        demo = self.require_demo()
        self.write_config()
        external = b'{"version":8,"endpoint":"newer"}'
        captured = []
        real_capture = demo.MigrationCaretaker.capture

        def capture_then_change(caretaker):
            checkpoint = real_capture(caretaker)
            captured.append(checkpoint)
            self.config.write_bytes(external)
            return checkpoint

        with mock.patch.object(
            demo.MigrationCaretaker,
            "capture",
            autospec=True,
            side_effect=capture_then_change,
        ):
            with mock.patch.object(
                demo.ConfigurationOriginator,
                "restore",
                autospec=True,
            ) as restore:
                with self.assertRaisesRegex(
                    demo.ConfigurationError,
                    r"^configuration changed after checkpoint capture$",
                ):
                    demo.migrate(self.config)

        restore.assert_not_called()
        self.assertEqual(self.config.read_bytes(), external)
        self.assertFalse(captured[0]._active)

    def test_other_pre_write_error_discards_without_restore(self):
        demo = self.require_demo()
        original = self.write_config()
        captured = []
        real_capture = demo.MigrationCaretaker.capture

        def record_capture(caretaker):
            checkpoint = real_capture(caretaker)
            captured.append(checkpoint)
            return checkpoint

        with mock.patch.object(
            demo.MigrationCaretaker,
            "capture",
            autospec=True,
            side_effect=record_capture,
        ):
            with mock.patch.object(
                demo,
                "render_configuration",
                side_effect=demo.ConfigurationError("unable to prepare migration"),
            ):
                with mock.patch.object(
                    demo.ConfigurationOriginator,
                    "restore",
                    autospec=True,
                ) as restore:
                    with self.assertRaisesRegex(
                        demo.ConfigurationError,
                        r"^unable to prepare migration$",
                    ):
                        demo.migrate(self.config)

        restore.assert_not_called()
        self.assertEqual(self.config.read_bytes(), original)
        self.assertFalse(captured[0]._active)

    def test_initial_write_failure_rolls_back_without_partial_state(self):
        demo = self.require_demo()
        original = self.write_config()
        real_replace = demo.os.replace
        calls = []

        def fail_first_replace(source, destination):
            calls.append((source, destination))
            if len(calls) == 1:
                raise OSError("write unavailable")
            return real_replace(source, destination)

        with mock.patch.object(demo.os, "replace", side_effect=fail_first_replace):
            with self.assertRaisesRegex(OSError, r"^write unavailable$"):
                demo.migrate(self.config)

        self.assertGreaterEqual(len(calls), 2)
        self.assertEqual(self.config.read_bytes(), original)
        self.assertEqual(list(self.config.parent.glob(".service.json.*.tmp")), [])

    def test_post_rename_durability_failure_is_rolled_back_conservatively(self):
        demo = self.require_demo()
        original = self.write_config()
        real_fsync = demo.os.fsync
        calls = []

        def fail_first_directory_fsync(descriptor):
            calls.append(descriptor)
            if len(calls) == 2:
                raise OSError("directory fsync unavailable")
            return real_fsync(descriptor)

        with mock.patch.object(
            demo.os,
            "fsync",
            side_effect=fail_first_directory_fsync,
        ):
            with self.assertRaisesRegex(
                OSError,
                r"^directory fsync unavailable$",
            ):
                demo.migrate(self.config)

        self.assertGreaterEqual(len(calls), 4)
        self.assertEqual(self.config.read_bytes(), original)
        self.assertEqual(list(self.config.parent.glob(".service.json.*.tmp")), [])

    @unittest.skipUnless(hasattr(os, "fchmod"), "file-descriptor chmod unavailable")
    def test_mode_is_applied_before_file_fsync_then_rename_and_directory_fsync(self):
        demo = self.require_demo()
        self.write_config()
        events = []
        real_fchmod = demo.os.fchmod
        real_fsync = demo.os.fsync
        real_replace = demo.os.replace

        def record_fchmod(descriptor, mode):
            events.append("fchmod")
            return real_fchmod(descriptor, mode)

        def record_fsync(descriptor):
            events.append("fsync")
            return real_fsync(descriptor)

        def record_replace(source, destination):
            events.append("replace")
            return real_replace(source, destination)

        with mock.patch.object(demo.os, "fchmod", side_effect=record_fchmod):
            with mock.patch.object(demo.os, "fsync", side_effect=record_fsync):
                with mock.patch.object(
                    demo.os,
                    "replace",
                    side_effect=record_replace,
                ):
                    demo.migrate(self.config)

        self.assertEqual(events, ["fchmod", "fsync", "replace", "fsync"])

    def test_post_write_validation_failure_restores_exact_bytes(self):
        demo = self.require_demo()
        original = self.write_config(b'{ "version": 1, "endpoint": "stable" }')

        with mock.patch.object(
            demo.ConfigurationOriginator,
            "validate_committed",
            autospec=True,
            side_effect=demo.ConfigurationError("post-write mismatch"),
        ):
            with self.assertRaisesRegex(
                demo.ConfigurationError,
                r"^post-write mismatch$",
            ):
                demo.migrate(self.config)

        self.assertEqual(self.config.read_bytes(), original)

    def test_restore_failure_reports_both_errors_and_leaves_complete_file(self):
        demo = self.require_demo()
        self.write_config()

        with mock.patch.object(
            demo.ConfigurationOriginator,
            "restore",
            autospec=True,
            side_effect=OSError("restore unavailable"),
        ):
            with self.assertRaisesRegex(
                demo.MigrationRollbackError,
                r"^migration failed and restoration failed: restore unavailable$",
            ) as caught:
                demo.migrate(self.config, fail=True)

        self.assertIsInstance(caught.exception.migration_error, RuntimeError)
        self.assertEqual(str(caught.exception.migration_error), "migration failed")
        self.assertIsInstance(caught.exception.restore_error, demo.RestorationError)
        self.assertEqual(
            json.loads(self.config.read_text(encoding="utf-8")),
            {"endpoint": "stable", "version": 2},
        )
        self.assertEqual(list(self.config.parent.glob(".service.json.*.tmp")), [])

    def test_failed_restore_keeps_checkpoint_active_for_retry(self):
        demo = self.require_demo()
        original = self.write_config()
        originator = demo.ConfigurationOriginator(self.config)
        caretaker = demo.MigrationCaretaker(originator)
        checkpoint = caretaker.capture()
        self.config.write_bytes(b'{"endpoint":"changed","version":2}')

        with mock.patch.object(
            originator,
            "restore",
            side_effect=OSError("temporary failure"),
        ):
            with self.assertRaisesRegex(
                demo.RestorationError,
                r"^configuration restoration failed: temporary failure$",
            ):
                caretaker.restore(checkpoint)

        self.assertTrue(caretaker.has_checkpoint)
        caretaker.restore(checkpoint)
        self.assertFalse(caretaker.has_checkpoint)
        self.assertEqual(self.config.read_bytes(), original)

    def test_missing_corrupt_and_non_utf8_inputs_are_never_modified(self):
        demo = self.require_demo()
        cases = (
            (None, demo.ConfigurationError, "configuration file is missing"),
            (b'{"version":', demo.ConfigurationError, "configuration must be valid JSON"),
            (b"\xff\xfe", demo.ConfigurationError, "configuration must be valid UTF-8"),
        )

        for raw, error_type, message in cases:
            with self.subTest(message=message):
                if self.config.exists():
                    self.config.unlink()
                if raw is not None:
                    self.config.write_bytes(raw)
                before = raw
                with self.assertRaisesRegex(error_type, f"^{re.escape(message)}$"):
                    demo.migrate(self.config)
                if raw is None:
                    self.assertFalse(self.config.exists())
                else:
                    self.assertEqual(self.config.read_bytes(), before)

    def test_strict_configuration_contract_rejects_invalid_values_unchanged(self):
        demo = self.require_demo()
        cases = (
            (b'{"version":1,"version":2,"endpoint":"stable"}', "configuration contains duplicate JSON object member: version"),
            (b'{"version":true,"endpoint":"stable"}', "configuration.version must be an integer"),
            (b'{"version":-1,"endpoint":"stable"}', "configuration.version must be at least 0"),
            (b'{"version":2147483647,"endpoint":"stable"}', "configuration.version cannot be incremented beyond 2147483647"),
            (b'{"version":1,"endpoint":""}', "configuration.endpoint must be non-empty"),
            (b'{"version":1,"endpoint":"stable","extra":1}', "configuration fields must be exactly: version, endpoint; unexpected: extra"),
            (b'[1,2]', "configuration must be a JSON object"),
            (b'{"version":NaN,"endpoint":"stable"}', "configuration must be valid JSON"),
            (b'{"version":1,"endpoint":"\\ud800"}', "configuration must not contain lone Unicode surrogates"),
        )

        for raw, message in cases:
            with self.subTest(message=message):
                self.write_config(raw)
                with self.assertRaisesRegex(
                    demo.ConfigurationError,
                    f"^{re.escape(message)}$",
                ):
                    demo.migrate(self.config)
                self.assertEqual(self.config.read_bytes(), raw)

    def test_input_and_output_bounds_are_controlled_without_partial_state(self):
        demo = self.require_demo()
        oversized = b" " * (demo.MAX_CONFIG_BYTES + 1)
        self.write_config(oversized)

        with self.assertRaisesRegex(
            demo.ConfigurationError,
            rf"^configuration exceeds maximum size of {demo.MAX_CONFIG_BYTES} bytes$",
        ):
            demo.migrate(self.config)
        self.assertEqual(self.config.read_bytes(), oversized)

        endpoint = "x" * (demo.MAX_ENDPOINT_CHARACTERS + 1)
        raw = json.dumps({"version": 1, "endpoint": endpoint}).encode("utf-8")
        self.write_config(raw)
        with self.assertRaisesRegex(
            demo.ConfigurationError,
            rf"^configuration.endpoint must contain at most {demo.MAX_ENDPOINT_CHARACTERS} characters$",
        ):
            demo.migrate(self.config)
        self.assertEqual(self.config.read_bytes(), raw)

    def test_symlink_target_is_rejected_without_touching_referent(self):
        demo = self.require_demo()
        referent = Path(self.temp_dir.name) / "referent.json"
        original = b'{"version":1,"endpoint":"stable"}'
        referent.write_bytes(original)
        try:
            self.config.symlink_to(referent)
        except (NotImplementedError, OSError):
            self.skipTest("symbolic links are unavailable")

        with self.assertRaisesRegex(
            demo.ConfigurationError,
            r"^configuration path must not be a symbolic link$",
        ):
            demo.migrate(self.config)

        self.assertTrue(self.config.is_symlink())
        self.assertEqual(referent.read_bytes(), original)

    def test_deterministic_runs_match_expected_result_and_bytes(self):
        demo = self.require_demo()
        first_path = self.config
        second_path = Path(self.temp_dir.name) / "second.json"
        source = (SAMPLE / "fixtures/valid/service-config.json").read_bytes()
        first_path.write_bytes(source)
        second_path.write_bytes(source)

        first = demo.migrate(first_path)
        second = demo.migrate(second_path)

        expected_result = json.loads(
            (SAMPLE / "expected/migration-result.json").read_text(encoding="utf-8")
        )
        expected_config = (SAMPLE / "expected/migrated-config.json").read_bytes()
        self.assertEqual(first, expected_result)
        self.assertEqual(second, expected_result)
        self.assertEqual(first_path.read_bytes(), expected_config)
        self.assertEqual(second_path.read_bytes(), expected_config)

    def test_invalid_cli_fixtures_have_exact_stable_errors_and_no_writes(self):
        self.require_demo()
        cases = (
            ("missing-config.json", "expected/missing-config-error.txt", False),
            ("fixtures/invalid/corrupt-config.json", "expected/corrupt-config-error.txt", True),
            ("fixtures/invalid/duplicate-version.json", "expected/duplicate-version-error.txt", True),
            ("fixtures/invalid/wrong-version-type.json", "expected/wrong-version-type-error.txt", True),
            ("fixtures/invalid/unknown-field.json", "expected/unknown-field-error.txt", True),
        )

        for fixture, expected_error, exists in cases:
            with self.subTest(fixture=fixture):
                source = SAMPLE / fixture
                test_path = Path(self.temp_dir.name) / Path(fixture).name
                if exists:
                    test_path.write_bytes(source.read_bytes())
                    before = test_path.read_bytes()
                completed = subprocess.run(
                    [sys.executable, str(DEMO_PATH), str(test_path)],
                    cwd=SAMPLE,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(completed.returncode, 2)
                self.assertEqual(completed.stdout, b"")
                self.assertEqual(
                    completed.stderr.decode("utf-8"),
                    (SAMPLE / expected_error).read_text(encoding="utf-8"),
                )
                if exists:
                    self.assertEqual(test_path.read_bytes(), before)
                else:
                    self.assertFalse(test_path.exists())

    def test_non_utf8_cli_error_is_stable_and_input_is_unchanged(self):
        self.require_demo()
        raw = b"\xff\xfe"
        self.config.write_bytes(raw)

        completed = subprocess.run(
            [sys.executable, str(DEMO_PATH), str(self.config)],
            cwd=SAMPLE,
            capture_output=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, b"")
        self.assertEqual(
            completed.stderr.decode("utf-8"),
            (SAMPLE / "expected/non-utf8-config-error.txt").read_text(
                encoding="utf-8"
            ),
        )
        self.assertEqual(self.config.read_bytes(), raw)

    def test_default_cli_is_deterministic_and_does_not_modify_fixture(self):
        self.require_demo()
        fixture = SAMPLE / "fixtures/valid/service-config.json"
        original = fixture.read_bytes()

        first = subprocess.run(
            [sys.executable, str(DEMO_PATH)],
            cwd=SAMPLE,
            capture_output=True,
            text=True,
            check=False,
        )
        second = subprocess.run(
            [sys.executable, str(DEMO_PATH)],
            cwd=SAMPLE,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(first.stderr, "")
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(json.loads(first.stdout), json.loads((SAMPLE / "expected/migration-result.json").read_text(encoding="utf-8")))
        self.assertEqual(fixture.read_bytes(), original)

    def test_manifest_and_skills_declare_canonical_roles_and_harness(self):
        self.require_demo()
        manifest = (SAMPLE / "skillware.yaml").read_text(encoding="utf-8")
        root = (SAMPLE / "SKILL.md").read_text(encoding="utf-8")
        participant_map = (RECORD / "participant-map.yaml").read_text(
            encoding="utf-8"
        )
        participant_section = participant_map.split("participants:\n", 1)[1].split(
            "execution_context:\n", 1
        )[0]
        context_section = participant_map.split("execution_context:\n", 1)[1].split(
            "implementation_paths:\n", 1
        )[0]

        self.assertEqual(
            set(re.findall(r"^  ([A-Za-z]+):$", participant_section, re.MULTILINE)),
            {"Originator", "Memento", "Caretaker"},
        )
        self.assertEqual(
            set(re.findall(r"^  ([^:\n]+):$", context_section, re.MULTILINE)),
            {"Agent Host", "Agent Runtime"},
        )
        for phrase in (
            "Originator",
            "Memento",
            "Caretaker",
            "Agent Host and Agent Runtime are execution context",
            "python3 scripts/run_demo.py",
            "python3 -m unittest discover tests -v",
            "root harness automatically",
            "Preparation and conflict failures discard without restoration",
            "write-attempt or post-write validation failures restore",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, root)
        for phrase in (
            "memento_contract: configuration-memento-v1",
            "capture: exact-bytes-plus-metadata",
            "preparation: originator-private-immutable-payload",
            "prepared_token: opaque-originator-issued-one-use",
            "restore: atomic-replace",
            "successful_commit: discard-without-restore",
            "retirement_integrity: checksum-owner-active-identity",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, manifest)
        for relative_path in (
            "references/configuration-memento-contract.md",
            "child-skills/configuration-originator/SKILL.md",
            "child-skills/migration-caretaker/SKILL.md",
        ):
            with self.subTest(path=relative_path):
                self.assertTrue((SAMPLE / relative_path).is_file())

    def test_evidence_is_exact_pinned_candidate_without_owned_restore(self):
        self.require_demo()
        evidence = (RECORD / "evidence/skillopt-frozen-case.md").read_text(
            encoding="utf-8"
        )
        correspondence = (RECORD / "correspondence.md").read_text(
            encoding="utf-8"
        )

        for phrase in (
            "b860a5cf88ce75e2bd02ca981ac21fb28cffba83",
            "skillopt_sleep/staging.py",
            "**Claim status:** candidate correspondence",
            "backs up before adoption",
            "no owned restore path",
            "full Memento is unverified",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, evidence)
        self.assertIn("**Status:** candidate correspondence", correspondence)
        self.assertNotIn("confirmed correspondence", correspondence)


if __name__ == "__main__":
    unittest.main()
