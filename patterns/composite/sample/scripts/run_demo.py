#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import sys


SAMPLE = Path(__file__).resolve().parents[1]
DEFAULT_WORKFLOW = SAMPLE / "fixtures/valid/investment-memo.json"
COMPONENT_CONTRACT = "memo-section-v1"
WORKFLOW_FIELDS = ("component_contract", "root", "nodes")
NODE_FIELDS = ("id", "kind", "title", "content", "evidence", "children")
SECTION_FIELDS = ("id", "title", "content", "evidence", "children")
NODE_KINDS = ("leaf", "composite")


class ValidationError(ValueError):
    pass


def validate_exact_fields(value, expected_fields, label):
    expected = set(expected_fields)
    actual = set(value)
    missing = [field for field in expected_fields if field not in actual]
    unexpected = sorted(actual - expected)
    if not missing and not unexpected:
        return

    details = []
    if missing:
        details.append("missing: " + ", ".join(missing))
    if unexpected:
        details.append("unexpected: " + ", ".join(unexpected))
    raise ValidationError(
        f"{label} fields must be exactly: {', '.join(expected_fields)}; "
        + "; ".join(details)
    )


def validate_node(node, index):
    label = f"nodes[{index}]"
    if not isinstance(node, dict):
        raise ValidationError(f"{label} must be a JSON object")
    validate_exact_fields(node, NODE_FIELDS, label)

    for field in ("id", "title", "content"):
        if not isinstance(node[field], str) or not node[field].strip():
            raise ValidationError(f"{label}.{field} must be a non-empty string")
    if node["kind"] not in NODE_KINDS:
        raise ValidationError(f"{label}.kind must be one of: leaf, composite")
    if not isinstance(node["evidence"], list) or any(
        not isinstance(item, str) or not item.strip() for item in node["evidence"]
    ):
        raise ValidationError(
            f"{label}.evidence must be a list of non-empty strings"
        )
    if not isinstance(node["children"], list) or any(
        not isinstance(item, str) or not item.strip() for item in node["children"]
    ):
        raise ValidationError(
            f"{label}.children must be a list of non-empty node ids"
        )
    if node["kind"] == "leaf" and node["children"]:
        raise ValidationError(
            f"leaf node '{node['id']}' must declare children as []"
        )


def build_registry(workflow):
    if not isinstance(workflow, dict):
        raise ValidationError("workflow must be a JSON object")
    validate_exact_fields(workflow, WORKFLOW_FIELDS, "workflow")
    if workflow["component_contract"] != COMPONENT_CONTRACT:
        raise ValidationError(
            f"component_contract must be '{COMPONENT_CONTRACT}'"
        )
    if not isinstance(workflow["root"], str) or not workflow["root"].strip():
        raise ValidationError("root must be a non-empty node id")
    if not isinstance(workflow["nodes"], list) or not workflow["nodes"]:
        raise ValidationError("nodes must be a non-empty list")

    registry = {}
    first_index = {}
    for index, node in enumerate(workflow["nodes"]):
        validate_node(node, index)
        node_id = node["id"]
        if node_id in registry:
            raise ValidationError(
                f"duplicate node id '{node_id}' at nodes[{first_index[node_id]}] "
                f"and nodes[{index}]"
            )
        registry[node_id] = node
        first_index[node_id] = index
    return registry


def validate_section_record(section):
    if not isinstance(section, dict):
        raise ValidationError("section must be a JSON object")
    section_id = section.get("id", "<unknown>")
    validate_exact_fields(section, SECTION_FIELDS, f"section '{section_id}'")
    for field in ("id", "title", "content"):
        if not isinstance(section[field], str):
            raise ValidationError(
                f"section '{section_id}'.{field} must be a string"
            )
    if not isinstance(section["evidence"], list) or any(
        not isinstance(item, str) for item in section["evidence"]
    ):
        raise ValidationError(
            f"section '{section_id}'.evidence must be a list of strings"
        )
    if not isinstance(section["children"], list):
        raise ValidationError(
            f"section '{section_id}'.children must be a list of section records"
        )
    for child in section["children"]:
        validate_section_record(child)
    return section


def build_section(node_id, registry, path=()):
    if node_id in path:
        raise ValidationError("cycle detected: " + " -> ".join((*path, node_id)))
    node = registry[node_id]
    next_path = (*path, node_id)
    children = []
    if node["kind"] == "composite":
        for child_id in node["children"]:
            if child_id not in registry:
                raise ValidationError(
                    f"node '{node_id}' references missing child '{child_id}'"
                )
            children.append(build_section(child_id, registry, next_path))

    section = {
        "id": node["id"],
        "title": node["title"],
        "content": node["content"],
        "evidence": list(node["evidence"]),
        "children": children,
    }
    return validate_section_record(section)


def build_component(workflow, node_id):
    if not isinstance(node_id, str) or not node_id.strip():
        raise ValidationError("component node_id must be a non-empty string")
    registry = build_registry(workflow)
    if node_id not in registry:
        raise ValidationError(f"component references missing node '{node_id}'")
    return build_section(node_id, registry)


def build_memo(workflow):
    registry = build_registry(workflow)
    root = workflow["root"]
    if root not in registry:
        raise ValidationError(f"root references missing node '{root}'")
    return build_section(root, registry)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Assemble an investment memo from a Composite workflow."
    )
    parser.add_argument(
        "workflow",
        nargs="?",
        type=Path,
        default=DEFAULT_WORKFLOW,
        help="JSON workflow path (defaults to the valid investment memo)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        workflow = json.loads(args.workflow.read_text(encoding="utf-8"))
        result = build_memo(workflow)
    except json.JSONDecodeError:
        print("error: workflow must contain valid JSON", file=sys.stderr)
        return 2
    except (OSError, ValidationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
