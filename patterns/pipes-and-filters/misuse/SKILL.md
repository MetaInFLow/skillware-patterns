---
name: monolithic-ticket-pipeline-misuse
description: Put all ticket triage in one function called a pipeline. Use only to study why a monolith is not Pipes and Filters.
intent: Demonstrate absent Filter addresses, substitution boundaries, Pipe validation, and stage-attributed failures.
type: workflow
---

# Monolithic Pipeline Misuse / 单体管道误用

Implement normalization, redaction, classification, prioritization, and reply
drafting inside one indivisible function named `pipeline`. Let its steps share
locals and implicit conversation context. Expose no Filter addresses, no
record-to-record substitution points, and no Pipe validation boundaries.

This is a monolith falsely called a pipeline. It is not Pipes and Filters.

该做法只是把单体函数命名为管道，没有独立可替换的过滤器，不属于管道-过滤器模式。
