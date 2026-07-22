import hashlib
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_FILES = (
    "CITATION.cff",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "LICENSE-CODE",
    "LICENSE-DOCS",
)
LICENSE_CONTRACTS = {
    "LICENSE-CODE": (
        "https://www.apache.org/licenses/LICENSE-2.0.txt",
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
        b"Apache License\n                           Version 2.0, January 2004",
    ),
    "LICENSE-DOCS": (
        "https://creativecommons.org/licenses/by/4.0/legalcode.txt",
        "9ba9550ad48438d0836ddab3da480b3b69ffa0aac7b7878b5a0039e7ab429411",
        b"Attribution 4.0 International",
    ),
}


class RepositoryShapeTest(unittest.TestCase):
    def test_required_roots_exist(self):
        for name in ("catalog", "docs", "patterns", "scripts", "tests"):
            self.assertTrue((ROOT / name).is_dir(), name)

    def test_public_governance_files_exist(self):
        for name in GOVERNANCE_FILES:
            with self.subTest(name=name):
                self.assertTrue((ROOT / name).is_file(), name)

    def test_license_files_match_official_canonical_bytes(self):
        for name, contract in LICENSE_CONTRACTS.items():
            source_url, expected_sha256, canonical_title = contract
            with self.subTest(name=name, canonical_source=source_url):
                content = (ROOT / name).read_bytes()
                self.assertIn(canonical_title, content)
                self.assertEqual(hashlib.sha256(content).hexdigest(), expected_sha256)


if __name__ == "__main__":
    unittest.main()
