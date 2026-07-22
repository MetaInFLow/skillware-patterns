import hashlib
from pathlib import Path
import subprocess
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
APACHE_ROOT_FILES = {".gitignore", "pyproject.toml"}
CC_BY_ROOT_FILES = {
    "README.md",
    "README.zh-CN.md",
    "CITATION.cff",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
}
CANONICAL_LICENSE_FILES = {"LICENSE-CODE", "LICENSE-DOCS"}


def license_memberships(path: str) -> tuple[str, ...]:
    parts = path.split("/")
    apache = (
        path in APACHE_ROOT_FILES
        or path.startswith(".github/")
        or path.startswith("scripts/")
        or path.startswith("tests/")
        or (len(parts) >= 4 and parts[0] == "patterns" and parts[2] == "sample")
    )
    cc_by = (
        path in CC_BY_ROOT_FILES
        or path.startswith("catalog/")
        or path.startswith("docs/")
        or path == "patterns/.gitkeep"
        or (
            len(parts) >= 3
            and parts[0] == "patterns"
            and parts[2] != "sample"
        )
    )
    canonical = path in CANONICAL_LICENSE_FILES
    return tuple(
        name
        for name, applies in (
            ("Apache-2.0", apache),
            ("CC-BY-4.0", cc_by),
            ("canonical-upstream-text", canonical),
        )
        if applies
    )


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

    def test_every_tracked_path_has_exactly_one_license_classification(self):
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
        tracked_paths = result.stdout.decode("utf-8").rstrip("\0").split("\0")

        self.assertGreater(len(tracked_paths), 0)
        for path in tracked_paths:
            with self.subTest(path=path):
                self.assertEqual(len(license_memberships(path)), 1, path)

    def test_license_classifier_covers_future_ci_and_pattern_boundaries(self):
        expected = {
            ".github/workflows/validate.yml": ("Apache-2.0",),
            ".gitignore": ("Apache-2.0",),
            "patterns/facade/sample/README.md": ("Apache-2.0",),
            "patterns/facade/evidence/frozen-case.md": ("CC-BY-4.0",),
            "patterns/facade/misuse/SKILL.md": ("CC-BY-4.0",),
            "patterns/facade/pattern.yaml": ("CC-BY-4.0",),
            "patterns/.gitkeep": ("CC-BY-4.0",),
            "LICENSE-CODE": ("canonical-upstream-text",),
        }
        for path, membership in expected.items():
            with self.subTest(path=path):
                self.assertEqual(license_memberships(path), membership)


if __name__ == "__main__":
    unittest.main()
