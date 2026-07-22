# Memo Section Component Contract

Contract ID: `memo-section-v1`

## Invocation

In Agent mode, invoke the selected root or child Skill with its declared input.
Every child Skill returns `memo-section-v1`. The root invokes its children in
the workflow's declared order and assembles their returned records.

In deterministic demo mode, use `build_component(workflow, node_id,
leaf_executors=None)`. Each Leaf executor has one callable shape:
`executor(leaf_request) -> memo-section-v1`. The request has exactly `id`,
`title`, `skill`, and `input`. Executors are keyed by the associated child
`SKILL.md` path and can be dependency-injected for focused tests. The Python
oracle models the same boundary; it does not read or interpret `SKILL.md`.

## Result

Every Leaf and Composite returns exactly the same five keys in this order:

| Field | Type | Rule |
| --- | --- | --- |
| `id` | string | Non-empty stable node identifier. |
| `title` | string | Non-empty section title. |
| `content` | string | Deterministic section prose. |
| `evidence` | list of strings | Zero or more evidence identifiers in declared order. |
| `children` | list of section records | `[]` for a Leaf; recursively assembled Component records for a Composite. |

The builder validates every executor result before composition. A Leaf result
must preserve its declared `id` and `title` and must return `children: []`.

## Workflow schema

The workflow has exactly `component_contract`, `root`, and `nodes`. `nodes` is
a list so duplicate IDs can be detected before registry overwrite.

- Every Composite node has exactly `id`, `kind`, `title`, `content`, `evidence`,
  and `children`.
- Every Leaf node has exactly `id`, `kind`, `title`, `skill`, `input`, and
  `children`. It stores executor input/configuration, not final `content` or
  `evidence`, and declares `children: []`.

Before any Leaf runs, the validator checks the complete registry: every child
exists; no node repeats a child; no cycle exists anywhere, including a
disconnected component; the root has zero parents; all nodes are reachable
from the root; and every non-root node has exactly one parent. These rules
reject DAG sharing and disconnected graphs as non-trees. The builder deep
copies Leaf input before calling an executor and never mutates the workflow.
