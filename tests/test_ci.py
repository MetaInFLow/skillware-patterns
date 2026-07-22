from pathlib import Path
import re
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / ".github/workflows/validate.yml"
CHECKOUT_PIN = "actions/checkout@11d5960a326750d5838078e36cf38b85af677262"
SETUP_PYTHON_PIN = (
    "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065"
)
CFFCONVERT_PIN = (
    "citation-file-format/cffconvert-github-action@"
    "4cf11baa70a673bfdf9dad0acc7ee33b3f4b6084"
)


class ContinuousIntegrationContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW_PATH.read_text(encoding="utf-8")
        cls.workflow = yaml.safe_load(cls.text)

    def test_workflow_name_triggers_permissions_and_concurrency(self):
        self.assertEqual(self.workflow["name"], "validate")
        self.assertIn("'on':", self.text)
        self.assertEqual(set(self.workflow["on"]), {"push", "pull_request"})
        self.assertEqual(self.workflow["permissions"], {"contents": "read"})
        self.assertEqual(
            self.workflow["concurrency"],
            {
                "group": "${{ github.workflow }}-${{ github.ref }}",
                "cancel-in-progress": True,
            },
        )

    def test_python_test_job_has_supported_matrix_and_commands(self):
        test_job = self.workflow["jobs"]["test"]
        self.assertGreater(test_job["timeout-minutes"], 0)
        self.assertEqual(test_job["strategy"]["fail-fast"], False)
        self.assertEqual(
            test_job["strategy"]["matrix"]["python-version"],
            ["3.10", "3.12"],
        )
        self.assertEqual(
            test_job["steps"][1]["with"]["python-version"],
            "${{ matrix.python-version }}",
        )

        run_commands = [
            line.strip()
            for step in test_job["steps"]
            for line in step.get("run", "").splitlines()
            if line.strip()
        ]
        self.assertEqual(
            run_commands,
            [
                "python -m pip install --upgrade pip",
                "python -m pip install -e .",
                "python -m unittest discover -v",
                "python scripts/validate_repository.py",
            ],
        )

    def test_cff_job_is_bounded_and_validates_citation_file(self):
        cff_job = self.workflow["jobs"]["cff"]
        self.assertGreater(cff_job["timeout-minutes"], 0)
        self.assertEqual(
            [step.get("uses") for step in cff_job["steps"]],
            [CHECKOUT_PIN, CFFCONVERT_PIN],
        )
        self.assertEqual(cff_job["steps"][1]["with"], {"args": "--validate"})

    def test_all_actions_use_reviewed_immutable_pins(self):
        uses = [
            step["uses"]
            for job in self.workflow["jobs"].values()
            for step in job["steps"]
            if "uses" in step
        ]
        self.assertEqual(
            uses,
            [CHECKOUT_PIN, SETUP_PYTHON_PIN, CHECKOUT_PIN, CFFCONVERT_PIN],
        )
        for action in uses:
            with self.subTest(action=action):
                self.assertRegex(action, r"@[0-9a-f]{40}$")

        self.assertEqual(
            re.findall(r"^\s*uses:\s*([^\s]+)\s+#\s*(\S+)\s*$", self.text, re.M),
            [
                (CHECKOUT_PIN, "v4"),
                (SETUP_PYTHON_PIN, "v5"),
                (CHECKOUT_PIN, "v4"),
                (CFFCONVERT_PIN, "2.0.0"),
            ],
        )

    def test_workflow_does_not_request_secrets_or_write_permissions(self):
        self.assertNotRegex(self.text, r"\bsecrets\s*\.")
        self.assertNotRegex(self.text, r"(?m)^\s*[a-z-]+:\s*write\s*$")


if __name__ == "__main__":
    unittest.main()
