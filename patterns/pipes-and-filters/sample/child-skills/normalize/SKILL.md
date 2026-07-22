---
name: ticket-normalize-filter
description: Normalize ticket text within support-ticket.v1. Use only for the normalize Filter in the support ticket pipeline.
intent: Canonicalize Unicode, whitespace, and case without performing other triage stages.
type: component
---

# Normalize Filter / 规范化过滤器

Under `support-ticket-pipeline-v1`, accept and return the complete
`support-ticket.v1` record. Normalize text to NFC, collapse whitespace, and
case-fold it. Change no other field and invoke no other Filter.

在相同版本记录契约内只规范化文本，不执行其他分流阶段。
