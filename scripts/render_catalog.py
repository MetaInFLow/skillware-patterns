from collections import Counter
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]

SOURCE_TRADITION_LABELS = {
    "gang-of-four": "Gang of Four",
    "pattern-oriented-software-architecture": (
        "Pattern-Oriented Software Architecture"
    ),
    "domain-driven-design": "Domain-Driven Design",
}


def _cell(value) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _table(headers, rows) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend(
        "| " + " | ".join(_cell(value) for value in row) + " |" for row in rows
    )
    return "\n".join(lines)


def render_pattern_index(rows) -> str:
    table_rows = []
    for row in rows:
        if row["source_tradition"] == "gang-of-four":
            category = row["source_category"].title()
        else:
            category = f"Not GoF ({row['source_category']})"
        table_rows.append(
            (
                row["name"],
                row["name_zh"],
                SOURCE_TRADITION_LABELS[row["source_tradition"]],
                category,
                row["paper_role"].replace("-", " ").capitalize(),
                f"{row['scenario']} / {row['scenario_zh']}",
                row["implementation_status"].title(),
            )
        )

    table = _table(
        (
            "Pattern",
            "中文名",
            "Source Tradition",
            "GoF Category",
            "Paper Role",
            "Scenario",
            "Status",
        ),
        table_rows,
    )
    return (
        "# Detailed Pattern Index\n\n"
        "This index lists the twelve pattern transfers selected for detailed "
        "constructive implementations. Source tradition and paper role are "
        "independent metadata dimensions.\n\n"
        f"{table}\n"
    )


def render_gof_screen(rows) -> str:
    table_rows = [
        (
            row["name"],
            row["name_zh"],
            row["category"].title(),
            row["source_intent"],
            "; ".join(row["skillware_carriers"]),
            row["screening_result"].title(),
            row["reasoning"],
            row["false_positive_risk"],
            "Yes" if row["detailed_sample"] else "No",
        )
        for row in rows
    ]
    table = _table(
        (
            "Pattern",
            "中文名",
            "Category",
            "Source Intent",
            "Skillware Carriers",
            "Result",
            "Screening Reasoning",
            "False-Positive Risk",
            "Detailed Sample",
        ),
        table_rows,
    )
    counts = Counter(row["screening_result"] for row in rows)
    detailed_count = sum(row["detailed_sample"] for row in rows)
    return (
        "# Gang of Four 23-Pattern Screen\n\n"
        "This screen evaluates whether each canonical Gang of Four pattern has "
        "a coherent Skillware mapping and records the strongest correspondence "
        "in the reviewed source set. **Screening does not imply detailed "
        "implementation, ecosystem frequency, or quality.** A candidate "
        "correspondence remains subject to fixed-path, participant-level "
        "evidence and a focused misuse discriminator.\n\n"
        f"{table}\n\n"
        f"The current screening distribution is {counts['strong']} Strong, "
        f"{counts['plausible']} Plausible, and {counts['weak']} Weak. Only the "
        f"{detailed_count} rows marked **Yes** have detailed GoF samples in "
        f"this repository plan; the other {len(rows) - detailed_count} do not "
        "claim one.\n"
    )


def main() -> int:
    index = yaml.safe_load(
        (ROOT / "catalog/pattern-index.yaml").read_text(encoding="utf-8")
    )
    screen = yaml.safe_load(
        (ROOT / "catalog/gof-23-screening.yaml").read_text(encoding="utf-8")
    )
    (ROOT / "catalog/pattern-index.md").write_text(
        render_pattern_index(index), encoding="utf-8"
    )
    (ROOT / "catalog/gof-23-screening.md").write_text(
        render_gof_screen(screen), encoding="utf-8"
    )
    print("Rendered catalog Markdown from YAML.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
