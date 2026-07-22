---
name: ticket-classify-filter
description: Classify support-ticket.v1 records by issue type. Use only for the classify Filter in the support ticket pipeline.
intent: Assign access, billing, or general while preserving the shared record envelope.
type: component
---

# Classify Filter / 分类过滤器

Under `support-ticket-pipeline-v1`, accept and return the complete
`support-ticket.v1` record. Set `category` to `access`, `billing`, or `general`
from the redacted normalized text. Change no other field and invoke no other
Filter.

在相同版本记录契约内只设置工单类别，不执行其他分流阶段。
