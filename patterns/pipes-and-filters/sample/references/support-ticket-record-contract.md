# Support Ticket Pipeline Contract

`support-ticket-pipeline-v1` connects one Data Source, five independent
Filters, explicit Pipes, and one Data Sink.

## Data Source

The public request is exactly `{"text": <non-blank Unicode string>}`. The Data
Source copies it into this versioned record:

```json
{
  "schema": "support-ticket.v1",
  "text": "...",
  "category": "unclassified",
  "priority": "normal",
  "draft": ""
}
```

No other field is permitted. Category is one of `unclassified`, `access`,
`billing`, or `general`; priority is one of `low`, `normal`, or `high`.

## Filter

Every Filter must accept and return the same `support-ticket.v1` record. The
five required addresses are `normalize`, `redact`, `classify`, `prioritize`,
and `draft`. A replacement is valid only when it keeps one required address
and the same record-to-record contract.

The runner rejects duplicate, missing, unknown, non-Filter, or invalid Filter
definitions before invoking any Filter. It owns canonical order and invokes
each admitted Filter exactly once.

## Pipe

Before and after every Filter, the Pipe validates the complete record schema,
field types, enumerations, Unicode, and depth. Each transfer returns a deep
copy. Filters receive neither the caller's request nor an alias held by another
Filter, and no hidden conversation state crosses a boundary.

## Data Sink

The Data Sink requires a classified record and non-blank draft. It returns
exactly `record` and `trace`, with trace equal to the five canonical addresses.
The final record and trace are detached copies.

## Failure

The first Filter exception or invalid output stops the pipeline. The error
names the failing stage; later Filters do not run. Input, configuration, Pipe,
and result failures use stable deterministic messages.

## Local oracle boundary

The oracle is sequential and in process. Buffering, backpressure, concurrency,
network transport, retries, distributed cancellation, and durable replay are
outside its scope and require separate production policies.
