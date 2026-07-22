---
name: support-ticket-triage
description: Transform a support ticket through five isolated record filters. Use when triage must be ordered, replaceable, validated, and deterministic.
intent: Run normalization, redaction, classification, prioritization, and drafting through one versioned Pipe contract without hidden state.
type: workflow
---

# Support Ticket Triage / 客服工单分流

## Trigger

Use this root Skill to triage one support ticket under
[`support-ticket-pipeline-v1`](references/support-ticket-record-contract.md).

## 中文触发约定

当客服工单必须经过可替换、可校验且顺序固定的五个过滤阶段时，使用本根 Skill。

## POSA participants

This is the Pipes and Filters architectural pattern from Pattern-Oriented
Software Architecture, not a Gang of Four pattern. The canonical roles are
Data Source, Filter, Pipe, and Data Sink. Agent Host and Agent Runtime are
execution context, not pattern participants.

## Agent mode

1. Admit exactly one non-blank Unicode `text` value of at most 65,536 UTF-8
   bytes and create a fresh `support-ticket.v1` record.
2. Require exactly one independently addressable Filter for each of normalize,
   redact, classify, prioritize, and draft. Reject duplicate, missing, unknown,
   or invalid Filters before running any stage. Freeze ordinary descriptor
   mutation and snapshot ordered `(filter_id, transform)` pairs at admission.
3. The runner owns the order above. Before and after every Filter, validate the
   complete Pipe contract and pass a deep copy. Do not use hidden conversation
   state or share record aliases.
4. Stop at the first exception or invalid Filter result and attribute the error
   to that stage. Do not invoke later Filters.
5. Emit a detached final record and the exact canonical trace. Do not mutate
   the caller's request.

## Demo mode and root harness

The standard-library oracle models the local sequential pipeline; it does not
interpret these Skill files. From `sample/`, run:

```bash
python3 scripts/run_demo.py
python3 -m unittest discover tests -v
```

The literal API `run_pipeline({'text':'URGENT email a@example.com: cannot
login'})` yields trace `normalize`, `redact`, `classify`, `prioritize`, `draft`,
redacts the email, and assigns high priority.

## Limits

Buffering, backpressure, concurrency, network transport, retries, distributed
cancellation, and durable replay are outside the local oracle. In-process copy
and type boundaries are trusted contracts, not a security sandbox. Filter
callables can still mutate external state or closures and use reflection; the
snapshot protects topology identity/order, not arbitrary callable side effects.

## Anti-pattern

One monolithic triage function falsely labeled a pipeline has no independently
replaceable Filters and is not Pipes and Filters. See `../misuse/SKILL.md`.
