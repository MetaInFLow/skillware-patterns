from pathlib import Path
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def validate() -> list[str]:
    errors = []
    screen = load("catalog/gof-23-screening.yaml")
    index = load("catalog/pattern-index.yaml")

    if len(screen) != 23:
        errors.append(f"expected 23 GoF rows, found {len(screen)}")
    if len(index) != 12:
        errors.append(f"expected 12 detailed rows, found {len(index)}")
    if len({row["id"] for row in screen}) != len(screen):
        errors.append("duplicate GoF pattern id")
    if len({row["id"] for row in index}) != len(index):
        errors.append("duplicate detailed pattern id")

    return errors


def main() -> int:
    failures = validate()
    for failure in failures:
        print(f"ERROR: {failure}")
    if not failures:
        print("Catalog validation passed.")
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
