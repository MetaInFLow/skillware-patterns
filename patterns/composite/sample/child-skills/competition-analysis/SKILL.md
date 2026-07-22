---
name: investment-competition-analysis
description: Produce one competition memo section. Use when an investment workflow needs a contract-compatible atomic competition analysis.
intent: Return differentiation and competitor evidence as one memo-section-v1 Leaf record.
type: component
---

# Competition Analysis

Accept `differentiator`, `alternatives`, and ordered `sources`. Analyze the
supplied competition inputs and return exactly `id`, `title`, `content`,
`evidence`, and `children` under `memo-section-v1`. Use
`id: competition-analysis`, cite sources in order, and return `children: []`.
Never add sub-sections or change the shared result shape.
