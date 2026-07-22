---
name: ticket-prioritize-filter
description: Prioritize support-ticket.v1 records from urgency signals. Use only for the prioritize Filter in the support ticket pipeline.
intent: Assign low, normal, or high priority while preserving the shared record envelope.
type: component
---

# Prioritize Filter / 优先级过滤器

Under `support-ticket-pipeline-v1`, accept and return the complete
`support-ticket.v1` record. Set `priority` to `low`, `normal`, or `high` from
the current text. Change no other field and invoke no other Filter.

在相同版本记录契约内只设置优先级，不执行其他分流阶段。
