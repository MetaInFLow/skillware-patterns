import ast
from pathlib import Path
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]

CATALOGS = (
    ("catalog/gof-23-screening.yaml", 23, "GoF"),
    ("catalog/pattern-index.yaml", 12, "detailed"),
)
LOAD_FAILED = object()

INDEX_FIELDS = {
    "id",
    "name",
    "name_zh",
    "source_tradition",
    "source_category",
    "paper_role",
    "implementation_status",
    "scenario",
    "scenario_zh",
}
SCREEN_FIELDS = {
    "id",
    "name",
    "name_zh",
    "category",
    "source_intent",
    "skillware_carriers",
    "screening_result",
    "reasoning",
    "false_positive_risk",
    "detailed_sample",
}
ALLOWED_TRADITIONS = {
    "gang-of-four",
    "pattern-oriented-software-architecture",
    "domain-driven-design",
}
ALLOWED_PAPER_ROLES = {"main-text", "repository-supplement"}
ALLOWED_SOURCE_CATEGORIES = {
    "creational",
    "structural",
    "behavioral",
    "architectural",
    "domain",
}
MAIN_TEXT_IDS = {
    "facade",
    "adapter",
    "composite",
    "observer",
    "state",
    "strategy",
}
NON_GOF_RECORDS = {
    "pipes-and-filters": (
        "pattern-oriented-software-architecture",
        "architectural",
    ),
    "specification": ("domain-driven-design", "domain"),
}
PARTICIPANT_TRADITION_LABELS = {
    "pipes-and-filters": "Pattern-Oriented Software Architecture",
    "specification": "Domain-Driven Design (Eric Evans)",
}

REQUIRED_RECORD_FILES = (
    "README.md",
    "pattern.yaml",
    "definition.md",
    "definition.zh-CN.md",
    "participant-map.yaml",
    "correspondence.md",
    "sample/SKILL.md",
    "sample/README.md",
    "sample/README.zh-CN.md",
    "sample/skillware.yaml",
    "sample/scripts/run_demo.py",
    "sample/tests/test_demo.py",
    "misuse/SKILL.md",
    "misuse/explanation.md",
)
REQUIRED_SAMPLE_DIRECTORIES = (
    "sample/fixtures",
    "sample/expected",
)
ENGLISH_DEFINITION_HEADINGS = (
    "Intent",
    "Forces",
    "Participants",
    "Collaboration",
    "Consequences",
    "Skillware Mapping",
    "False Positives",
    "Open-Source Correspondence",
    "Limitations",
)
CHINESE_DEFINITION_HEADINGS = (
    ("意图（Intent）",),
    ("作用力（Forces）",),
    ("参与者（Participants）",),
    ("协作（Collaboration）",),
    ("后果（Consequences）", "结果（Consequences）"),
    ("Skillware 映射（Skillware Mapping）",),
    ("误判（False Positives）", "假阳性（False Positives）"),
    ("开源对应（Open-Source Correspondence）",),
    ("局限（Limitations）",),
)
FINAL_ONTOLOGY = " -> ".join(
    (
        "Behavioral Source",
        "Skill Artifact",
        "Skillware Unit",
        "Agent Host",
        "Agent Runtime",
        "Execution Trace",
        "Task Outcome",
    )
)
OBSOLETE_ONTOLOGY_TERM = "Agent Execution Core"


def load(path: str):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


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


def _load_yaml_file(path: Path, errors: list[str]):
    display = _display_path(path)
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing file: {display}")
    except yaml.YAMLError as exc:
        problem = getattr(exc, "problem", None) or str(exc).splitlines()[0]
        errors.append(f"invalid YAML in {display}: {problem}")
    except (OSError, UnicodeError) as exc:
        errors.append(f"unable to read {display}: {exc}")
    return LOAD_FAILED


def _read_text_file(path: Path, errors: list[str]):
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing file: {_display_path(path)}")
    except (OSError, UnicodeError) as exc:
        errors.append(f"unable to read {_display_path(path)}: {exc}")
    return None


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


def _validate_catalog_contract(screen: list[dict], index: list[dict]) -> list[str]:
    errors = []

    for row_number, row in enumerate(screen, start=1):
        if set(row) != SCREEN_FIELDS:
            errors.append(
                f"catalog/gof-23-screening.yaml: row {row_number} has invalid fields"
            )
        for field in SCREEN_FIELDS - {"skillware_carriers", "detailed_sample"}:
            if not isinstance(row.get(field), str) or not row[field].strip():
                errors.append(
                    f"catalog/gof-23-screening.yaml: row {row_number} "
                    f"field '{field}' must be a non-empty string"
                )
        if not isinstance(row.get("skillware_carriers"), list):
            errors.append(
                f"catalog/gof-23-screening.yaml: row {row_number} "
                "field 'skillware_carriers' must be a list"
            )
        if not isinstance(row.get("detailed_sample"), bool):
            errors.append(
                f"catalog/gof-23-screening.yaml: row {row_number} "
                "field 'detailed_sample' must be a boolean"
            )

    for row_number, row in enumerate(index, start=1):
        pattern_id = row["id"]
        if set(row) != INDEX_FIELDS:
            errors.append(
                f"catalog/pattern-index.yaml: row {row_number} has invalid fields"
            )
        for field in INDEX_FIELDS:
            if not isinstance(row.get(field), str) or not row[field].strip():
                errors.append(
                    f"catalog/pattern-index.yaml: row {row_number} "
                    f"field '{field}' must be a non-empty string"
                )
        if row.get("source_tradition") not in ALLOWED_TRADITIONS:
            errors.append(f"{pattern_id}: invalid source_tradition")
        if row.get("source_category") not in ALLOWED_SOURCE_CATEGORIES:
            errors.append(f"{pattern_id}: invalid source_category")
        if row.get("paper_role") not in ALLOWED_PAPER_ROLES:
            errors.append(f"{pattern_id}: invalid paper_role")
        if row.get("implementation_status") != "detailed":
            errors.append(f"{pattern_id}: implementation_status must be 'detailed'")

    gof_index = {
        row["id"]: row
        for row in index
        if row.get("source_tradition") == "gang-of-four"
    }
    if len(gof_index) != 10:
        errors.append(
            "detailed catalog must contain exactly 10 gang-of-four records, "
            f"found {len(gof_index)}"
        )

    for pattern_id, (tradition, category) in NON_GOF_RECORDS.items():
        row = next((item for item in index if item["id"] == pattern_id), None)
        if row is None:
            errors.append(f"detailed catalog missing required record '{pattern_id}'")
            continue
        if row.get("source_tradition") != tradition:
            errors.append(
                f"{pattern_id} must use source_tradition '{tradition}'"
            )
        if row.get("source_category") != category:
            errors.append(f"{pattern_id} must use source_category '{category}'")

    actual_main_text = {
        row["id"] for row in index if row.get("paper_role") == "main-text"
    }
    if actual_main_text != MAIN_TEXT_IDS:
        errors.append(
            "main-text pattern ids must be exactly "
            + ", ".join(sorted(MAIN_TEXT_IDS))
        )

    detailed_screen = {
        row["id"]: row for row in screen if row.get("detailed_sample") is True
    }
    if len(detailed_screen) != 10:
        errors.append(
            "GoF screen must mark exactly 10 detailed samples, "
            f"found {len(detailed_screen)}"
        )
    if set(detailed_screen) != set(gof_index):
        errors.append(
            "GoF detailed_sample ids do not match detailed gang-of-four records"
        )

    for pattern_id in sorted(set(detailed_screen).intersection(gof_index)):
        screen_row = detailed_screen[pattern_id]
        index_row = gof_index[pattern_id]
        if (
            screen_row.get("name"),
            screen_row.get("name_zh"),
            screen_row.get("category"),
        ) != (
            index_row.get("name"),
            index_row.get("name_zh"),
            index_row.get("source_category"),
        ):
            errors.append(
                f"{pattern_id}: GoF screen name/category metadata does not match "
                "detailed catalog"
            )

    return errors


def _participant_paths(value, key=""):
    if isinstance(value, dict):
        for child_key, child_value in value.items():
            yield from _participant_paths(child_value, child_key)
    elif isinstance(value, list):
        if key == "paths" or key.endswith("_paths"):
            for child in value:
                yield child
        else:
            for child in value:
                yield from _participant_paths(child, key)
    elif key == "path" or key.endswith("_path"):
        yield value


def _validate_participant_map(
    map_path: Path, record: Path, errors: list[str]
) -> None:
    participant_map = _load_yaml_file(map_path, errors)
    if participant_map is LOAD_FAILED:
        return
    display = _display_path(map_path)
    if not isinstance(participant_map, dict):
        errors.append(f"{display}: expected a mapping")
        return

    paths = list(_participant_paths(participant_map))
    if not paths:
        errors.append(f"{display}: no participant artifact paths declared")
        return

    record_root = record.resolve()
    for declared_path in paths:
        if not isinstance(declared_path, str) or not declared_path.strip():
            errors.append(f"{display}: participant paths must be non-empty strings")
            continue
        relative_path = Path(declared_path)
        if relative_path.is_absolute():
            errors.append(
                f"{display}: participant path escapes pattern record "
                f"'{declared_path}'"
            )
            continue
        if relative_path.parts and relative_path.parts[0] == "patterns":
            resolved = (ROOT / relative_path).resolve()
        else:
            resolved = (map_path.parent / relative_path).resolve()
        try:
            resolved.relative_to(record_root)
        except ValueError:
            errors.append(
                f"{display}: participant path escapes pattern record "
                f"'{declared_path}'"
            )
            continue
        if not resolved.is_file():
            errors.append(
                f"{display}: missing participant path '{declared_path}'"
            )


def _validate_definition_headings(
    pattern_id: str, record: Path, errors: list[str]
) -> None:
    english = _read_text_file(record / "definition.md", errors)
    chinese = _read_text_file(record / "definition.zh-CN.md", errors)
    if english is not None:
        headings = {
            line.removeprefix("## ")
            for line in english.splitlines()
            if line.startswith("## ")
        }
        for heading in ENGLISH_DEFINITION_HEADINGS:
            if heading not in headings:
                errors.append(
                    f"{pattern_id}: definition.md missing heading {heading}"
                )
    if chinese is not None:
        headings = {
            line.removeprefix("## ")
            for line in chinese.splitlines()
            if line.startswith("## ")
        }
        for alternatives in CHINESE_DEFINITION_HEADINGS:
            if not headings.intersection(alternatives):
                errors.append(
                    f"{pattern_id}: definition.zh-CN.md missing heading "
                    f"{alternatives[0]}"
                )


def _validate_demo_imports(pattern_id: str, demo_path: Path, errors: list[str]) -> None:
    source = _read_text_file(demo_path, errors)
    if source is None:
        return
    try:
        tree = ast.parse(source, filename=str(demo_path))
    except SyntaxError as exc:
        errors.append(f"{pattern_id}: sample demo has invalid Python: {exc.msg}")
        return
    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(
                alias.name.partition(".")[0] for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                imported_modules.add("relative import")
            elif node.module:
                imported_modules.add(node.module.partition(".")[0])
    external = sorted(imported_modules - sys.stdlib_module_names)
    if external:
        errors.append(
            f"{pattern_id}: sample demo imports non-stdlib modules: "
            + ", ".join(external)
        )


def _validate_record(row: dict, errors: list[str]) -> None:
    pattern_id = row["id"]
    record = ROOT / "patterns" / pattern_id
    if not record.is_dir():
        return

    for relative_path in REQUIRED_RECORD_FILES:
        if not (record / relative_path).is_file():
            errors.append(f"{pattern_id}: missing required file {relative_path}")
    for relative_path in REQUIRED_SAMPLE_DIRECTORIES:
        directory = record / relative_path
        if not directory.is_dir() or not any(
            path.is_file() for path in directory.rglob("*")
        ):
            errors.append(
                f"{pattern_id}: missing or empty required directory {relative_path}"
            )

    metadata = _load_yaml_file(record / "pattern.yaml", errors)
    if metadata is not LOAD_FAILED and metadata != row:
        errors.append(
            f"{pattern_id}: pattern.yaml metadata does not exactly match catalog row"
        )

    manifest = _load_yaml_file(record / "sample/skillware.yaml", errors)
    if manifest is not LOAD_FAILED:
        if not isinstance(manifest, dict):
            errors.append(f"{pattern_id}: sample/skillware.yaml must be a mapping")
        else:
            if manifest.get("name") != row["scenario"]:
                errors.append(
                    f"{pattern_id}: sample manifest name does not match catalog scenario"
                )
            if manifest.get("name_zh") != row["scenario_zh"]:
                errors.append(
                    f"{pattern_id}: sample manifest name_zh does not match catalog "
                    "scenario_zh"
                )
            if "pattern" in manifest and manifest["pattern"] != pattern_id:
                errors.append(
                    f"{pattern_id}: sample manifest pattern does not match catalog id"
                )

    for filename, expected_heading in (
        ("sample/README.md", f"# {row['scenario']}\n"),
        ("sample/README.zh-CN.md", f"# {row['scenario_zh']}\n"),
    ):
        text = _read_text_file(record / filename, errors)
        if text is not None and not text.startswith(expected_heading):
            errors.append(
                f"{pattern_id}: {filename} heading does not match catalog scenario"
            )

    _validate_definition_headings(pattern_id, record, errors)

    skill_text = _read_text_file(record / "sample/SKILL.md", errors)
    if skill_text is not None:
        if FINAL_ONTOLOGY not in skill_text:
            errors.append(f"{pattern_id}: sample/SKILL.md missing final ontology")
        if OBSOLETE_ONTOLOGY_TERM in skill_text:
            errors.append(
                f"{pattern_id}: sample/SKILL.md contains obsolete term "
                f"'{OBSOLETE_ONTOLOGY_TERM}'"
            )

    root_participant_map = _load_yaml_file(record / "participant-map.yaml", errors)
    if root_participant_map is not LOAD_FAILED and isinstance(root_participant_map, dict):
        if root_participant_map.get("pattern_id") != pattern_id:
            errors.append(f"{pattern_id}: participant-map pattern_id mismatch")
        if root_participant_map.get("pattern") != row["name"]:
            errors.append(f"{pattern_id}: participant-map pattern name mismatch")
        expected_tradition = PARTICIPANT_TRADITION_LABELS.get(pattern_id)
        if expected_tradition is not None and (
            root_participant_map.get("source_tradition") != expected_tradition
        ):
            errors.append(
                f"{pattern_id}: participant-map source tradition mismatch"
            )

    for map_path in sorted(record.rglob("participant-map.yaml")):
        _validate_participant_map(map_path, record, errors)

    _validate_demo_imports(
        pattern_id, record / "sample/scripts/run_demo.py", errors
    )


def _validate_records(index: list[dict]) -> list[str]:
    errors = []
    patterns_root = ROOT / "patterns"
    expected_ids = {row["id"] for row in index}
    if not patterns_root.is_dir():
        return ["missing patterns directory"]

    actual_ids = {path.name for path in patterns_root.iterdir() if path.is_dir()}
    for pattern_id in sorted(expected_ids - actual_ids):
        errors.append(f"missing pattern record directory: patterns/{pattern_id}")
    for pattern_id in sorted(actual_ids - expected_ids):
        errors.append(
            f"pattern directory is not declared in catalog: patterns/{pattern_id}"
        )
    for row in index:
        _validate_record(row, errors)
    return errors


def validate() -> list[str]:
    errors = []
    loaded = {}
    for path, expected_count, label in CATALOGS:
        rows = _load_for_validation(path, errors)
        loaded[path] = rows
        if rows is not LOAD_FAILED:
            _validate_rows(rows, path, expected_count, label, errors)

    # A malformed catalog cannot be used as the authority for cross-record checks.
    if errors:
        return errors

    screen = loaded["catalog/gof-23-screening.yaml"]
    index = loaded["catalog/pattern-index.yaml"]
    errors.extend(_validate_catalog_contract(screen, index))
    if errors:
        return errors

    errors.extend(_validate_records(index))
    return errors


def main() -> int:
    failures = validate()
    for failure in failures:
        print(f"ERROR: {failure}")
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
