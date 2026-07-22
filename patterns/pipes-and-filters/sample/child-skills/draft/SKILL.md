---
name: ticket-draft-filter
description: Draft a reply in support-ticket.v1 after triage. Use only for the draft Filter in the support ticket pipeline.
intent: Produce a deterministic category-and-priority acknowledgement while preserving the record envelope.
type: component
---

# Draft Filter / 回复草拟过滤器

Under `support-ticket-pipeline-v1`, accept and return the complete
`support-ticket.v1` record. Set `draft` from the existing category and priority.
Change no other field and invoke no other Filter.

在相同版本记录契约内只生成确定性回复草稿，不执行其他分流阶段。
