---
name: investment-competition-analysis
description: Produce one competition memo section. Use when an investment workflow needs a contract-compatible atomic competition analysis.
intent: Return differentiation and competitor evidence as one memo-section-v1 Leaf record.
type: component
---

# Competition Analysis

Read the declared competitor-matrix evidence. Return exactly `id`, `title`,
`content`, `evidence`, and `children` under `memo-section-v1`. Use
`id: competition-analysis`, preserve evidence order, and return
`children: []`. Never add sub-sections or change the shared result shape.
