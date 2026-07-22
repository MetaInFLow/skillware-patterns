# Memo Section Component Contract

Contract ID: `memo-section-v1`

Every Leaf and Composite supports the same invocation operation:
`build_component(workflow, node_id)`. `workflow` is the validated JSON mapping
described below and `node_id` is the non-empty ID of the Component to invoke.
The operation may select an atomic Leaf or a nested Composite without changing
its arguments or return contract. `build_memo(workflow)` is only the CLI-facing
convenience operation that selects `workflow.root` through the same traversal.

Every Leaf and Composite returns exactly the same five keys in this order:

| Field | Type | Rule |
| --- | --- | --- |
| `id` | string | Non-empty stable node identifier. |
| `title` | string | Non-empty section title. |
| `content` | string | Deterministic section prose. |
| `evidence` | list of strings | Zero or more evidence identifiers in declared order. |
| `children` | list of section records | `[]` for a Leaf; recursively assembled Component records for a Composite. |

The workflow is a JSON object with exactly `component_contract`, `root`, and
`nodes`. `nodes` is a list rather than a JSON object so duplicate node IDs can
be detected instead of silently overwritten. Every node has exactly `id`,
`kind`, `title`, `content`, `evidence`, and `children`. A Leaf declares
`children: []`; a Composite declares child node IDs in traversal order.

The builder rejects invalid workflow or node schemas, unknown kinds, duplicate
IDs, missing roots, missing children, Leaf nodes with children, invalid result
records, and cycles. A cycle error reports the complete reference path. The
builder copies output lists and never mutates the parsed workflow.
