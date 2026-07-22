---
name: investment-market-analysis
description: Produce one market memo section. Use when an investment workflow needs a contract-compatible atomic market analysis.
intent: Return market demand and sizing evidence as one memo-section-v1 Leaf record.
type: component
---

# Market Analysis

Accept `customer_segment`, `workflow_problem`, `market_wedge`, and ordered
`sources`. Analyze the supplied market inputs and return exactly `id`, `title`,
`content`, `evidence`, and `children` under `memo-section-v1`. Use
`id: market-analysis`, cite the declared sources in order, and return
`children: []`. Never add sub-sections or change the shared result shape.
