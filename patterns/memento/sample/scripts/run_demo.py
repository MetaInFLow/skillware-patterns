#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile


SAMPLE = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = SAMPLE / "fixtures/valid/service-config.json"
CONFIG_FIELDS = ("version", "endpoint")
MAX_CONFIG_BYTES = 65_536
MAX_ENDPOINT_CHARACTERS = 4_096
MAX_VERSION = 2_147_483_647


class ConfigurationError(ValueError):
    pass


class MementoLifecycleError(RuntimeError):
    pass


class MementoTargetError(RuntimeError):
    pass


class MementoIntegrityError(RuntimeError):
    pass


class RestorationError(RuntimeError):
    def __init__(self, failure):
        self.failure = failure
        super().__init__(f"configuration restoration failed: {failure}")


class MigrationRollbackError(RuntimeError):
    def __init__(self, migration_error, restore_error):
        self.migration_error = migration_error
        self.restore_error = restore_error
        super().__init__(
            f"{migration_error} and restoration failed: {restore_error.failure}"
        )


class DuplicateMemberError(ValueError):
    pass


def reject_duplicate_members(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateMemberError(key)
        result[key] = value
    return result


def reject_non_finite(_value):
    raise ValueError("non-finite number")


def target_key(path):
    return os.path.normcase(os.path.abspath(os.fspath(path)))


def read_bounded_file(path):
    path = Path(path)
    if path.is_symlink():
        raise ConfigurationError("configuration path must not be a symbolic link")
    try:
        metadata = path.stat()
    except FileNotFoundError as exc:
        raise ConfigurationError("configuration file is missing") from exc
    except OSError as exc:
        raise ConfigurationError(f"unable to inspect configuration: {exc}") from exc
    if not stat.S_ISREG(metadata.st_mode):
        raise ConfigurationError("configuration path must be a regular file")
    try:
        with path.open("rb") as stream:
            raw = stream.read(MAX_CONFIG_BYTES + 1)
    except OSError as exc:
        raise ConfigurationError(f"unable to read configuration: {exc}") from exc
    if len(raw) > MAX_CONFIG_BYTES:
        raise ConfigurationError(
            f"configuration exceeds maximum size of {MAX_CONFIG_BYTES} bytes"
        )
    return raw, stat.S_IMODE(metadata.st_mode)


def validate_configuration(raw):
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ConfigurationError("configuration must be valid UTF-8") from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=reject_duplicate_members,
            parse_constant=reject_non_finite,
        )
    except DuplicateMemberError as exc:
        raise ConfigurationError(
            f"configuration contains duplicate JSON object member: {exc.args[0]}"
        ) from exc
    except (json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise ConfigurationError("configuration must be valid JSON") from exc
    if not isinstance(value, dict):
        raise ConfigurationError("configuration must be a JSON object")

    expected = set(CONFIG_FIELDS)
    actual = set(value)
    missing = [field for field in CONFIG_FIELDS if field not in actual]
    unexpected = sorted(actual - expected)
    if missing or unexpected:
        details = []
        if missing:
            details.append("missing: " + ", ".join(missing))
        if unexpected:
            details.append("unexpected: " + ", ".join(unexpected))
        raise ConfigurationError(
            f"configuration fields must be exactly: {', '.join(CONFIG_FIELDS)}; "
            + "; ".join(details)
        )

    version = value["version"]
    if isinstance(version, bool) or not isinstance(version, int):
        raise ConfigurationError("configuration.version must be an integer")
    if version < 0:
        raise ConfigurationError("configuration.version must be at least 0")
    if version >= MAX_VERSION:
        raise ConfigurationError(
            f"configuration.version cannot be incremented beyond {MAX_VERSION}"
        )

    endpoint = value["endpoint"]
    if not isinstance(endpoint, str):
        raise ConfigurationError("configuration.endpoint must be a string")
    if not endpoint.strip():
        raise ConfigurationError("configuration.endpoint must be non-empty")
    if len(endpoint) > MAX_ENDPOINT_CHARACTERS:
        raise ConfigurationError(
            "configuration.endpoint must contain at most "
            f"{MAX_ENDPOINT_CHARACTERS} characters"
        )
    if any(0xD800 <= ord(character) <= 0xDFFF for character in endpoint):
        raise ConfigurationError(
            "configuration must not contain lone Unicode surrogates"
        )
    return {"version": version, "endpoint": endpoint}


def render_configuration(configuration):
    raw = (
        json.dumps(configuration, ensure_ascii=False, sort_keys=True, indent=2)
        + "\n"
    ).encode("utf-8")
    if len(raw) > MAX_CONFIG_BYTES:
        raise ConfigurationError(
            f"migrated configuration exceeds maximum size of {MAX_CONFIG_BYTES} bytes"
        )
    return raw


def atomic_replace(path, raw, mode):
    path = Path(path)
    descriptor = None
    temporary_path = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = None
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary_path, mode)
        os.replace(temporary_path, path)
        temporary_path = None
        if hasattr(os, "O_DIRECTORY"):
            directory_descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(directory_descriptor)
            finally:
                os.close(directory_descriptor)
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass


class ConfigurationMemento:
    __slots__ = (
        "_target_key",
        "_raw",
        "_mode",
        "_digest",
        "_owner_token",
        "_active",
    )

    def __init__(self, path, raw, mode, owner_token):
        self._target_key = target_key(path)
        self._raw = bytes(raw)
        self._mode = mode
        self._digest = hashlib.sha256(self._raw).digest()
        self._owner_token = owner_token
        self._active = True

    def __repr__(self):
        return "ConfigurationMemento(<opaque>)"

    def _snapshot_for(self, path):
        if self._target_key != target_key(path):
            raise MementoTargetError("memento target does not match originator")
        if hashlib.sha256(self._raw).digest() != self._digest:
            raise MementoIntegrityError("memento checksum does not match captured bytes")
        return self._raw, self._mode

    def _retire(self):
        self._active = False


class ConfigurationOriginator:
    def __init__(self, path):
        self._path = Path(path)
        self._configuration = None

    @property
    def path(self):
        return self._path

    def create_memento(self, owner_token):
        raw, mode = read_bounded_file(self._path)
        self._configuration = validate_configuration(raw)
        return ConfigurationMemento(self._path, raw, mode, owner_token)

    def migrate_from(self, memento):
        prior_raw, prior_mode = memento._snapshot_for(self._path)
        current_raw, _current_mode = read_bounded_file(self._path)
        if current_raw != prior_raw:
            raise ConfigurationError(
                "configuration changed after checkpoint capture"
            )
        current = validate_configuration(current_raw)
        migrated = {
            "version": current["version"] + 1,
            "endpoint": current["endpoint"],
        }
        migrated_raw = render_configuration(migrated)
        atomic_replace(self._path, migrated_raw, prior_mode)
        self._configuration = migrated
        return current, migrated, migrated_raw

    def validate_committed(self, expected_configuration, expected_raw):
        raw, _mode = read_bounded_file(self._path)
        current = validate_configuration(raw)
        if current != expected_configuration or raw != expected_raw:
            raise ConfigurationError("post-write configuration mismatch")

    def restore(self, memento):
        raw, mode = memento._snapshot_for(self._path)
        atomic_replace(self._path, raw, mode)
        restored_raw, restored_mode = read_bounded_file(self._path)
        if restored_raw != raw:
            raise ConfigurationError("restored bytes do not match memento")
        if os.name == "posix" and restored_mode != mode:
            raise ConfigurationError("restored permissions do not match memento")
        self._configuration = validate_configuration(restored_raw)


class MigrationCaretaker:
    def __init__(self, originator):
        self._originator = originator
        self._owner_token = object()
        self._checkpoint = None

    @property
    def has_checkpoint(self):
        return self._checkpoint is not None

    def capture(self):
        if self._checkpoint is not None:
            raise MementoLifecycleError(
                "caretaker already owns an active memento"
            )
        self._checkpoint = self._originator.create_memento(self._owner_token)
        return self._checkpoint

    def _require_owned_active(self, memento):
        if memento._owner_token is not self._owner_token:
            raise MementoLifecycleError(
                "memento does not belong to this caretaker"
            )
        if not memento._active or self._checkpoint is not memento:
            raise MementoLifecycleError("memento is no longer active")

    def restore(self, memento):
        self._require_owned_active(memento)
        try:
            self._originator.restore(memento)
        except Exception as exc:
            raise RestorationError(exc) from exc
        memento._retire()
        self._checkpoint = None

    def commit(self, memento):
        self._require_owned_active(memento)
        memento._retire()
        self._checkpoint = None


def migrate(path, fail=False):
    originator = ConfigurationOriginator(path)
    caretaker = MigrationCaretaker(originator)
    checkpoint = caretaker.capture()
    try:
        prior, migrated, migrated_raw = originator.migrate_from(checkpoint)
        originator.validate_committed(migrated, migrated_raw)
        if fail:
            raise RuntimeError("migration failed")
    except Exception as migration_error:
        try:
            caretaker.restore(checkpoint)
        except RestorationError as restore_error:
            raise MigrationRollbackError(
                migration_error,
                restore_error,
            ) from restore_error
        raise
    caretaker.commit(checkpoint)
    return {
        "status": "migrated",
        "from_version": prior["version"],
        "to_version": migrated["version"],
        "endpoint": migrated["endpoint"],
        "restored": False,
    }


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Run Configuration Migration")
    parser.add_argument("configuration", nargs="?", type=Path)
    parser.add_argument("--fail", action="store_true")
    return parser.parse_args(argv)


def run_cli(configuration, fail):
    if configuration is not None:
        return migrate(configuration, fail=fail)
    with tempfile.TemporaryDirectory() as temporary_directory:
        temporary_config = Path(temporary_directory) / DEFAULT_CONFIG.name
        shutil.copyfile(DEFAULT_CONFIG, temporary_config)
        return migrate(temporary_config, fail=fail)


def main(argv=None):
    args = parse_args(argv)
    try:
        result = run_cli(args.configuration, args.fail)
    except (ConfigurationError, MementoLifecycleError, MementoTargetError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except (MigrationRollbackError, RuntimeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
