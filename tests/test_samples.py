import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]
PATTERNS = ROOT / "patterns"
TIMEOUT_SECONDS = 30


class MaterializedSampleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.materialized = sorted(path for path in PATTERNS.iterdir() if path.is_dir())

    def run_sample_command(self, sample, command):
        environment = os.environ.copy()
        environment.pop("PYTHONPATH", None)
        completed = subprocess.run(
            command,
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

    def test_each_materialized_sample_is_standalone_and_executable(self):
        self.assertIn(PATTERNS / "composite", self.materialized)
        self.assertIn(PATTERNS / "observer", self.materialized)
        self.assertIn(PATTERNS / "state", self.materialized)
        for record in self.materialized:
            with self.subTest(pattern=record.name):
                with TemporaryDirectory() as temp_dir:
                    isolated_record = Path(temp_dir) / record.name
                    shutil.copytree(record, isolated_record)
                    sample = isolated_record / "sample"

                    self.run_sample_command(
                        sample,
                        [sys.executable, "-m", "unittest", "discover", "tests", "-v"],
                    )
                    self.run_sample_command(
                        sample,
                        [sys.executable, "scripts/run_demo.py"],
                    )

if __name__ == "__main__":
    unittest.main()
