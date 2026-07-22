---
name: investment-financial-analysis
description: Produce one financial memo section. Use when an investment workflow needs a contract-compatible atomic financial analysis.
intent: Return growth, burn, and financing evidence as one memo-section-v1 Leaf record.
type: component
---

# Financial Analysis

Read the declared management accounts and cash-plan evidence. Return exactly
`id`, `title`, `content`, `evidence`, and `children` under
`memo-section-v1`. Use `id: financial-analysis`, preserve evidence order, and
return `children: []`. Never add sub-sections or change the shared result shape.
