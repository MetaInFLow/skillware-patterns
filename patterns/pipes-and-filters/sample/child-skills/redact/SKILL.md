---
name: ticket-redact-filter
description: Redact email addresses within support-ticket.v1. Use only for the redact Filter in the support ticket pipeline.
intent: Replace email addresses while preserving the shared record envelope and all unrelated fields.
type: component
---

# Redact Filter / 脱敏过滤器

Under `support-ticket-pipeline-v1`, accept and return the complete
`support-ticket.v1` record. Replace email addresses in `text` with
`[redacted-email]`. Change no other field and invoke no other Filter.

在相同版本记录契约内只脱敏邮箱地址，不执行其他分流阶段。
