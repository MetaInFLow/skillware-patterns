---
name: investment-risk-analysis
description: Produce one risk memo section. Use when an investment workflow needs a contract-compatible atomic risk analysis.
intent: Return material risks and diligence gates as one memo-section-v1 Leaf record.
type: component
---

# Risk Analysis

Read the declared risk-register evidence. Return exactly `id`, `title`,
`content`, `evidence`, and `children` under `memo-section-v1`. Use
`id: risk-analysis`, preserve evidence order, and return `children: []`.
Never add sub-sections or change the shared result shape.
