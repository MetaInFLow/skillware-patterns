#!/usr/bin/env python3
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys


SAMPLE = Path(__file__).resolve().parents[1]
DEFAULT_WORKFLOW = SAMPLE / "fixtures/valid/investment-memo.json"
COMPONENT_CONTRACT = "memo-section-v1"
WORKFLOW_FIELDS = ("component_contract", "root", "nodes")
COMPOSITE_NODE_FIELDS = (
    "id",
    "kind",
    "title",
    "content",
    "evidence",
    "children",
)
LEAF_NODE_FIELDS = ("id", "kind", "title", "skill", "input", "children")
LEAF_REQUEST_FIELDS = ("id", "title", "skill", "input")
SECTION_FIELDS = ("id", "title", "content", "evidence", "children")
NODE_KINDS = ("leaf", "composite")
MARKET_SKILL = "child-skills/market-analysis/SKILL.md"
FINANCIAL_SKILL = "child-skills/financial-analysis/SKILL.md"
COMPETITION_SKILL = "child-skills/competition-analysis/SKILL.md"
RISK_SKILL = "child-skills/risk-analysis/SKILL.md"


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


def require_non_empty_strings(value, fields, label):
    if any(
        not isinstance(value[field], str) or not value[field].strip()
        for field in fields
    ):
        raise ValidationError(
            f"{label} requires non-empty string fields: {', '.join(fields)}"
        )


def validate_leaf_request(request, expected_skill, input_fields):
    if not isinstance(request, dict):
        raise ValidationError("leaf request must be a JSON object")
    validate_exact_fields(request, LEAF_REQUEST_FIELDS, "leaf request")
    require_non_empty_strings(request, ("id", "title", "skill"), "leaf request")
    if request["skill"] != expected_skill:
        raise ValidationError(f"leaf request skill must be '{expected_skill}'")
    inputs = request["input"]
    if not isinstance(inputs, dict):
        raise ValidationError(f"leaf input for '{request['id']}' must be a JSON object")
    validate_exact_fields(inputs, input_fields, f"leaf input for '{request['id']}'")
    sources = inputs["sources"]
    if not isinstance(sources, list) or any(
        not isinstance(source, str) or not source.strip() for source in sources
    ):
        raise ValidationError(
            f"leaf input for '{request['id']}'.sources must be a list of "
            "non-empty strings"
        )
    return inputs


def leaf_result(request, content, sources):
    return {
        "id": request["id"],
        "title": request["title"],
        "content": content,
        "evidence": [f"fixture:{source}" for source in sources],
        "children": [],
    }


def execute_market_analysis(request):
    fields = ("customer_segment", "workflow_problem", "market_wedge", "sources")
    inputs = validate_leaf_request(request, MARKET_SKILL, fields)
    require_non_empty_strings(inputs, fields[:-1], f"leaf input for '{request['id']}'")
    content = (
        f"{inputs['customer_segment']} face {inputs['workflow_problem']}; "
        f"{inputs['market_wedge']} has credible demand."
    )
    return leaf_result(request, content, inputs["sources"])


def execute_financial_analysis(request):
    fields = ("growth_signal", "burn_profile", "financing_condition", "sources")
    inputs = validate_leaf_request(request, FINANCIAL_SKILL, fields)
    require_non_empty_strings(inputs, fields[:-1], f"leaf input for '{request['id']}'")
    content = (
        f"{inputs['growth_signal']}, but {inputs['burn_profile']} requires "
        f"{inputs['financing_condition']}."
    )
    return leaf_result(request, content, inputs["sources"])


def execute_competition_analysis(request):
    fields = ("differentiator", "alternatives", "sources")
    inputs = validate_leaf_request(request, COMPETITION_SKILL, fields)
    require_non_empty_strings(inputs, fields[:-1], f"leaf input for '{request['id']}'")
    content = (
        f"The company differentiates through {inputs['differentiator']} while "
        f"competing with {inputs['alternatives']}."
    )
    return leaf_result(request, content, inputs["sources"])


def execute_risk_analysis(request):
    fields = ("risks", "gate_policy", "sources")
    inputs = validate_leaf_request(request, RISK_SKILL, fields)
    if not isinstance(inputs["risks"], list) or len(inputs["risks"]) < 2 or any(
        not isinstance(risk, str) or not risk.strip() for risk in inputs["risks"]
    ):
        raise ValidationError(
            f"leaf input for '{request['id']}'.risks must contain at least two "
            "non-empty strings"
        )
    require_non_empty_strings(inputs, ("gate_policy",), f"leaf input for '{request['id']}'")
    risk_text = ", ".join(inputs["risks"][:-1]) + f", and {inputs['risks'][-1]}"
    content = f"Primary risks are {risk_text}; {inputs['gate_policy']}."
    return leaf_result(request, content, inputs["sources"])


DEFAULT_LEAF_EXECUTORS = {
    MARKET_SKILL: execute_market_analysis,
    FINANCIAL_SKILL: execute_financial_analysis,
    COMPETITION_SKILL: execute_competition_analysis,
    RISK_SKILL: execute_risk_analysis,
}


def validate_node(node, index):
    label = f"nodes[{index}]"
    if not isinstance(node, dict):
        raise ValidationError(f"{label} must be a JSON object")
    kind = node.get("kind")
    if kind not in NODE_KINDS:
        raise ValidationError(f"{label}.kind must be one of: leaf, composite")

    expected_fields = LEAF_NODE_FIELDS if kind == "leaf" else COMPOSITE_NODE_FIELDS
    validate_exact_fields(node, expected_fields, label)
    require_non_empty_strings(node, ("id", "title"), label)
    if not isinstance(node["children"], list) or any(
        not isinstance(item, str) or not item.strip() for item in node["children"]
    ):
        raise ValidationError(f"{label}.children must be a list of non-empty node ids")

    if kind == "leaf":
        if not isinstance(node["skill"], str) or not node["skill"].strip():
            raise ValidationError(f"{label}.skill must be a non-empty string")
        if not isinstance(node["input"], dict):
            raise ValidationError(f"{label}.input must be a JSON object")
        if node["children"]:
            raise ValidationError(
                f"leaf node '{node['id']}' must declare children as []"
            )
        return

    require_non_empty_strings(node, ("content",), label)
    if not isinstance(node["evidence"], list) or any(
        not isinstance(item, str) or not item.strip() for item in node["evidence"]
    ):
        raise ValidationError(f"{label}.evidence must be a list of non-empty strings")


def build_registry(workflow):
    if not isinstance(workflow, dict):
        raise ValidationError("workflow must be a JSON object")
    validate_exact_fields(workflow, WORKFLOW_FIELDS, "workflow")
    if workflow["component_contract"] != COMPONENT_CONTRACT:
        raise ValidationError(f"component_contract must be '{COMPONENT_CONTRACT}'")
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


def validate_all_references(registry):
    parents = {node_id: [] for node_id in registry}
    for node_id, node in registry.items():
        seen = set()
        for child_id in node["children"]:
            if child_id in seen:
                raise ValidationError(f"node '{node_id}' repeats child '{child_id}'")
            seen.add(child_id)
            if child_id not in registry:
                raise ValidationError(
                    f"node '{node_id}' references missing child '{child_id}'"
                )
            parents[child_id].append(node_id)
    return parents


def validate_no_cycles(registry):
    state = {node_id: "new" for node_id in registry}
    path = []

    def visit(node_id):
        if state[node_id] == "active":
            cycle_start = path.index(node_id)
            cycle = path[cycle_start:] + [node_id]
            raise ValidationError("cycle detected: " + " -> ".join(cycle))
        if state[node_id] == "done":
            return
        state[node_id] = "active"
        path.append(node_id)
        for child_id in registry[node_id]["children"]:
            visit(child_id)
        path.pop()
        state[node_id] = "done"

    for node_id in registry:
        if state[node_id] == "new":
            visit(node_id)


def reachable_from(root, registry):
    reachable = set()
    pending = [root]
    while pending:
        node_id = pending.pop()
        if node_id in reachable:
            continue
        reachable.add(node_id)
        pending.extend(reversed(registry[node_id]["children"]))
    return reachable


def validate_tree(workflow, registry):
    root = workflow["root"]
    if root not in registry:
        raise ValidationError(f"root references missing node '{root}'")
    parents = validate_all_references(registry)
    validate_no_cycles(registry)

    if parents[root]:
        raise ValidationError(
            f"root node '{root}' must have zero parents; found {len(parents[root])}: "
            + ", ".join(parents[root])
        )
    unreachable = [
        node_id for node_id in registry if node_id not in reachable_from(root, registry)
    ]
    if unreachable:
        raise ValidationError(
            f"unreachable nodes from root '{root}': " + ", ".join(unreachable)
        )
    for node_id, node_parents in parents.items():
        if node_id == root or len(node_parents) == 1:
            continue
        raise ValidationError(
            f"node '{node_id}' must have exactly one parent; found "
            f"{len(node_parents)}: " + ", ".join(node_parents)
        )


def validate_section_record(section):
    if not isinstance(section, dict):
        raise ValidationError("section must be a JSON object")
    section_id = section.get("id", "<unknown>")
    validate_exact_fields(section, SECTION_FIELDS, f"section '{section_id}'")
    if not isinstance(section["id"], str) or not section["id"].strip():
        raise ValidationError("section.id must be a non-empty string")
    section_id = section["id"]
    if not isinstance(section["title"], str) or not section["title"].strip():
        raise ValidationError(
            f"section '{section_id}'.title must be a non-empty string"
        )
    if not isinstance(section["content"], str):
        raise ValidationError(f"section '{section_id}'.content must be a string")
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


def execute_leaf(node, leaf_executors):
    skill = node["skill"]
    executor = leaf_executors.get(skill)
    if not callable(executor):
        raise ValidationError(f"no leaf executor registered for skill '{skill}'")
    request = {
        "id": node["id"],
        "title": node["title"],
        "skill": skill,
        "input": deepcopy(node["input"]),
    }
    section = validate_section_record(executor(request))
    if section["id"] != node["id"]:
        raise ValidationError(
            f"leaf executor for '{skill}' returned id '{section['id']}', "
            f"expected '{node['id']}'"
        )
    if section["title"] != node["title"]:
        raise ValidationError(
            f"leaf executor for '{skill}' returned title '{section['title']}', "
            f"expected '{node['title']}'"
        )
    if section["children"]:
        raise ValidationError(
            f"leaf executor for '{skill}' must return children as []"
        )
    return section


def build_section(node_id, registry, leaf_executors):
    node = registry[node_id]
    if node["kind"] == "leaf":
        return execute_leaf(node, leaf_executors)

    children = [
        build_section(child_id, registry, leaf_executors)
        for child_id in node["children"]
    ]
    section = {
        "id": node["id"],
        "title": node["title"],
        "content": node["content"],
        "evidence": list(node["evidence"]),
        "children": children,
    }
    return validate_section_record(section)


def prepare_workflow(workflow):
    registry = build_registry(workflow)
    validate_tree(workflow, registry)
    return registry


def select_executors(leaf_executors):
    if leaf_executors is None:
        return DEFAULT_LEAF_EXECUTORS
    if not isinstance(leaf_executors, dict):
        raise ValidationError("leaf_executors must be a mapping")
    return leaf_executors


def build_component(workflow, node_id, leaf_executors=None):
    if not isinstance(node_id, str) or not node_id.strip():
        raise ValidationError("component node_id must be a non-empty string")
    registry = prepare_workflow(workflow)
    if node_id not in registry:
        raise ValidationError(f"component references missing node '{node_id}'")
    return build_section(node_id, registry, select_executors(leaf_executors))


def build_memo(workflow, leaf_executors=None):
    registry = prepare_workflow(workflow)
    return build_section(
        workflow["root"], registry, select_executors(leaf_executors)
    )


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
