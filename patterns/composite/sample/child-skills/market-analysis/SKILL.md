---
name: investment-market-analysis
description: Produce one market memo section. Use when an investment workflow needs a contract-compatible atomic market analysis.
intent: Return market demand and sizing evidence as one memo-section-v1 Leaf record.
type: component
---

# Market Analysis

Read the declared market interview and sizing evidence. Return exactly `id`,
`title`, `content`, `evidence`, and `children` under `memo-section-v1`. Use
`id: market-analysis`, preserve evidence order, and return `children: []`.
Never add sub-sections or change the shared result shape.
