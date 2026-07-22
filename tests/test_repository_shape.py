from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class RepositoryShapeTest(unittest.TestCase):
    def test_required_roots_exist(self):
        for name in ("catalog", "docs", "patterns", "scripts", "tests"):
            self.assertTrue((ROOT / name).is_dir(), name)


if __name__ == "__main__":
    unittest.main()
