---
name: investment-financial-analysis
description: Produce one financial memo section. Use when an investment workflow needs a contract-compatible atomic financial analysis.
intent: Return growth, burn, and financing evidence as one memo-section-v1 Leaf record.
type: component
---

# Financial Analysis

Accept `growth_signal`, `burn_profile`, `financing_condition`, and ordered
`sources`. Analyze the supplied financial inputs and return exactly `id`,
`title`, `content`, `evidence`, and `children` under `memo-section-v1`. Use
`id: financial-analysis`, cite sources in order, and return `children: []`.
Never add sub-sections or change the shared result shape.
