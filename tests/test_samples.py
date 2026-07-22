import ast
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import textwrap
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
PATTERNS = ROOT / "patterns"
TIMEOUT_SECONDS = 30

NETWORK_GUARD = """
import os
import socket


class NetworkDisabledError(RuntimeError):
    pass


class NetworkDisabledSocket(socket.socket):
    def connect(self, *args, **kwargs):
        raise NetworkDisabledError("sample tests must not access the network")

    def connect_ex(self, *args, **kwargs):
        raise NetworkDisabledError("sample tests must not access the network")


def network_disabled(*args, **kwargs):
    raise NetworkDisabledError("sample tests must not access the network")


socket.socket = NetworkDisabledSocket
socket.create_connection = network_disabled
socket.getaddrinfo = network_disabled
os.environ["SKILLWARE_NETWORK_DISABLED"] = "1"
"""

RUN_TESTS = """
import os
import unittest

assert os.environ.get("SKILLWARE_NETWORK_DISABLED") == "1"
suite = unittest.defaultTestLoader.discover("tests")
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
"""

RUN_DEMO = """
import os
import runpy

assert os.environ.get("SKILLWARE_NETWORK_DISABLED") == "1"
runpy.run_path("scripts/run_demo.py", run_name="__main__")
"""


class CatalogSampleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows = yaml.safe_load(
            (ROOT / "catalog/pattern-index.yaml").read_text(encoding="utf-8")
        )
        cls.pattern_ids = [row["id"] for row in rows]

    def run_sample_command(self, sample, source):
        environment = os.environ.copy()
        for name in ("PYTHONHOME", "PYTHONSTARTUP"):
            environment.pop(name, None)
        environment.update(
            {
                "HOME": str(sample / ".isolated-home"),
                "PYTHONNOUSERSITE": "1",
                "PYTHONPATH": str(sample),
            }
        )
        completed = subprocess.run(
            [sys.executable, "-c", textwrap.dedent(source)],
            cwd=sample,
            capture_output=True,
            env=environment,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )
        return completed

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
                    isolated_record = Path(temp_dir) / pattern_id
                    shutil.copytree(PATTERNS / pattern_id, isolated_record)
                    sample = isolated_record / "sample"
                    (sample / "sitecustomize.py").write_text(
                        textwrap.dedent(NETWORK_GUARD), encoding="utf-8"
                    )

                    self.run_sample_command(sample, RUN_TESTS)
                    first = self.run_sample_command(sample, RUN_DEMO)
                    second = self.run_sample_command(sample, RUN_DEMO)

                    self.assertEqual(first.stdout, second.stdout)
                    self.assertEqual(first.stderr, second.stderr)
                    self.assertTrue(first.stdout.strip())
                    self.assertEqual(first.stderr, "")


if __name__ == "__main__":
    unittest.main()
