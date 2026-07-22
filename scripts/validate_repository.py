from pathlib import Path
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]

CATALOGS = (
    ("catalog/gof-23-screening.yaml", 23, "GoF"),
    ("catalog/pattern-index.yaml", 12, "detailed"),
)
LOAD_FAILED = object()


def load(path: str):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def _load_for_validation(path: str, errors: list[str]):
    try:
        return load(path)
    except FileNotFoundError:
        errors.append(f"missing catalog file: {path}")
    except yaml.YAMLError as exc:
        problem = getattr(exc, "problem", None) or str(exc).splitlines()[0]
        errors.append(f"invalid YAML in {path}: {problem}")
    except (OSError, UnicodeError) as exc:
        errors.append(f"unable to read {path}: {exc}")
    return LOAD_FAILED


def _validate_rows(
    rows, path: str, expected_count: int, label: str, errors: list[str]
) -> None:
    if not isinstance(rows, list):
        errors.append(f"{path}: expected a list of rows")
        return

    if len(rows) != expected_count:
        errors.append(f"expected {expected_count} {label} rows, found {len(rows)}")

    first_row_by_id = {}
    for row_number, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            errors.append(f"{path}: row {row_number} must be a mapping")
            continue

        pattern_id = row.get("id")
        if pattern_id is None or pattern_id == "":
            errors.append(f"{path}: row {row_number} missing required id")
            continue
        if not isinstance(pattern_id, str) or not pattern_id.strip():
            errors.append(f"{path}: row {row_number} id must be a non-empty string")
            continue

        first_row = first_row_by_id.get(pattern_id)
        if first_row is not None:
            errors.append(
                f"duplicate {label} pattern id '{pattern_id}' "
                f"at rows {first_row} and {row_number}"
            )
        else:
            first_row_by_id[pattern_id] = row_number


def validate() -> list[str]:
    errors = []
    for path, expected_count, label in CATALOGS:
        rows = _load_for_validation(path, errors)
        if rows is not LOAD_FAILED:
            _validate_rows(rows, path, expected_count, label, errors)
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
