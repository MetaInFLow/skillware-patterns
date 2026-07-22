import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
PATTERNS = ROOT / "patterns"
RUNNER = ROOT / "tests/isolated_sample_runner.py"
TIMEOUT_SECONDS = 30
BYTECODE_IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc")


class SampleProcessTimeout(RuntimeError):
    pass


def run_process(command, *, cwd, env=None, timeout=TIMEOUT_SECONDS):
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        stdout, stderr = process.communicate()
        process.wait()
        raise SampleProcessTimeout(
            f"sample process group timed out after {timeout}s\n"
            f"stdout:\n{stdout}\nstderr:\n{stderr}"
        ) from None
    process.wait()
    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


def tree_snapshot(root: Path):
    entries = []
    for path in sorted((root, *root.rglob("*")), key=lambda item: str(item)):
        relative = "." if path == root else path.relative_to(root).as_posix()
        metadata = path.lstat()
        mode = stat.S_IMODE(metadata.st_mode)
        if path.name == "__pycache__" or path.suffix == ".pyc":
            raise AssertionError(f"bytecode artifact created: {relative}")
        if stat.S_ISREG(metadata.st_mode):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            kind = "file"
            detail = digest
        elif stat.S_ISDIR(metadata.st_mode):
            kind = "directory"
            detail = ""
        elif stat.S_ISLNK(metadata.st_mode):
            kind = "symlink"
            detail = os.readlink(path)
        else:
            kind = "other"
            detail = ""
        entries.append((relative, kind, mode, detail))
    return tuple(entries)


class CatalogSampleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows = yaml.safe_load(
            (ROOT / "catalog/pattern-index.yaml").read_text(encoding="utf-8")
        )
        cls.pattern_ids = [row["id"] for row in rows]

    def isolated_environment(self, sample):
        environment = os.environ.copy()
        for name in tuple(environment):
            if name == "PYTHONHOME" or name == "PYTHONSTARTUP" or name.startswith(
                "PYTHONPATH"
            ):
                environment.pop(name, None)
        environment.update(
            {
                "HOME": str(sample.parent / ".isolated-home"),
                "PYTHONNOUSERSITE": "1",
            }
        )
        return environment

    def run_sample_command(self, sample, mode, *, timeout=TIMEOUT_SECONDS):
        completed = run_process(
            [
                sys.executable,
                "-I",
                "-S",
                "-B",
                str(RUNNER),
                mode,
                str(sample),
            ],
            cwd=sample,
            env=self.isolated_environment(sample),
            timeout=timeout,
        )
        return completed

    def assert_success(self, completed):
        self.assertEqual(
            completed.returncode,
            0,
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )

    def run_read_only(self, sample, mode, *, snapshot_root=None):
        checked_root = sample if snapshot_root is None else snapshot_root
        before = tree_snapshot(checked_root)
        completed = self.run_sample_command(sample, mode)
        after = tree_snapshot(checked_root)
        self.assert_success(completed)
        self.assertEqual(before, after, f"{mode} modified its copied record tree")
        return completed, after

    def test_catalog_has_exactly_twelve_materialized_samples(self):
        materialized = sorted(path.name for path in PATTERNS.iterdir() if path.is_dir())

        self.assertEqual(len(self.pattern_ids), 12)
        self.assertEqual(materialized, sorted(self.pattern_ids))
        for pattern_id in self.pattern_ids:
            with self.subTest(pattern=pattern_id):
                self.assertTrue((PATTERNS / pattern_id / "sample").is_dir())

    def test_sample_runtime_imports_only_the_standard_library(self):
        for pattern_id in self.pattern_ids:
            demo = PATTERNS / pattern_id / "sample/scripts/run_demo.py"
            tree = ast.parse(demo.read_text(encoding="utf-8"), filename=str(demo))
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(alias.name.partition(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module.partition(".")[0])
            with self.subTest(pattern=pattern_id):
                self.assertEqual(imports - sys.stdlib_module_names, set())

    def test_every_catalog_sample_is_standalone_deterministic_and_network_isolated(self):
        for pattern_id in self.pattern_ids:
            with self.subTest(pattern=pattern_id):
                with TemporaryDirectory() as temp_dir:
                    temporary_root = Path(temp_dir)

                    test_record = temporary_root / "focused" / pattern_id
                    shutil.copytree(
                        PATTERNS / pattern_id,
                        test_record,
                        ignore=BYTECODE_IGNORE,
                    )
                    self.run_read_only(
                        test_record / "sample",
                        "tests",
                        snapshot_root=test_record,
                    )

                    demo_results = []
                    for copy_name in ("demo-a", "demo-b"):
                        demo_record = temporary_root / copy_name / pattern_id
                        shutil.copytree(
                            PATTERNS / pattern_id,
                            demo_record,
                            ignore=BYTECODE_IGNORE,
                        )
                        completed, snapshot = self.run_read_only(
                            demo_record / "sample",
                            "demo",
                            snapshot_root=demo_record,
                        )
                        demo_results.append(
                            (
                                completed.returncode,
                                completed.stdout,
                                completed.stderr,
                                snapshot,
                            )
                        )

                    self.assertEqual(demo_results[0], demo_results[1])
                    self.assertTrue(demo_results[0][1].strip())
                    self.assertEqual(demo_results[0][2], "")

    def make_adversarial_sample(self, directory, source):
        sample = Path(directory) / "sample"
        (sample / "scripts").mkdir(parents=True)
        (sample / "scripts/run_demo.py").write_text(source, encoding="utf-8")
        return sample

    def test_runner_uses_isolated_no_site_no_bytecode_mode(self):
        with TemporaryDirectory() as temp_dir:
            sample = self.make_adversarial_sample(
                temp_dir,
                "import json, sys\n"
                "print(json.dumps({'flags': [sys.flags.isolated, "
                "sys.flags.no_site, sys.dont_write_bytecode], "
                "'sys_path': sys.path}))\n",
            )

            completed = self.run_sample_command(sample, "demo")

            self.assert_success(completed)
            report = json.loads(completed.stdout)
            self.assertEqual(report["flags"], [1, 1, True])
            for entry in report["sys_path"]:
                path = Path(entry).resolve()
                if "site-packages" in path.parts or "dist-packages" in path.parts:
                    self.fail(f"site package path leaked into runner: {path}")
                if not (
                    path == sample.resolve()
                    or sample.resolve() in path.parents
                    or Path(sys.base_prefix).resolve() in path.parents
                ):
                    self.fail(f"non-isolated import path leaked into runner: {path}")
            self.assertNotIn(str(ROOT), completed.stderr)
            tree_snapshot(sample)

    def test_guard_blocks_udp_send(self):
        with TemporaryDirectory() as temp_dir:
            sample = self.make_adversarial_sample(
                temp_dir,
                "import socket\n"
                "sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)\n"
                "sock.sendto(b'probe', ('127.0.0.1', 9))\n",
            )

            completed = self.run_sample_command(sample, "demo")

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("trusted-sample isolation guard blocked", completed.stderr)

    def test_guard_blocks_subprocess_creation(self):
        with TemporaryDirectory() as temp_dir:
            marker = Path(temp_dir) / "spawned.txt"
            sample = self.make_adversarial_sample(
                temp_dir,
                "import subprocess, sys\n"
                f"subprocess.run([sys.executable, '-c', "
                f"\"from pathlib import Path; Path({str(marker)!r}).write_text('bad')\"], check=True)\n",
            )

            completed = self.run_sample_command(sample, "demo")

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("trusted-sample isolation guard blocked", completed.stderr)
            self.assertFalse(marker.exists())

    def test_demo_must_not_mutate_its_copied_sample_tree(self):
        with TemporaryDirectory() as temp_dir:
            sample = self.make_adversarial_sample(
                temp_dir,
                "from pathlib import Path\n"
                "Path('mutation.txt').write_text('mutated', encoding='utf-8')\n"
                "print('stable')\n",
            )

            with self.assertRaisesRegex(AssertionError, "modified its copied record"):
                self.run_read_only(sample, "demo")

    def test_timeout_kills_and_waits_for_the_entire_process_group(self):
        with TemporaryDirectory() as temp_dir:
            marker = Path(temp_dir) / "child-survived.txt"
            source = (
                "import subprocess, sys, time\n"
                "subprocess.Popen([sys.executable, '-c', "
                f"\"import time; from pathlib import Path; time.sleep(0.8); "
                f"Path({str(marker)!r}).write_text('survived')\"])\n"
                "time.sleep(30)\n"
            )

            with self.assertRaises(SampleProcessTimeout):
                run_process(
                    [sys.executable, "-I", "-S", "-B", "-c", source],
                    cwd=temp_dir,
                    timeout=0.2,
                )
            time.sleep(1.0)

            self.assertFalse(marker.exists(), "timed-out child process survived")


if __name__ == "__main__":
    unittest.main()
