# Support Ticket Triage

> **This directory is the mock sample.** It demonstrates how the Pipes and
> Filters idea is implemented in Skillware; it is not the upstream OpenMontage
> pipeline.

## Evidence at a glance

```mermaid
flowchart LR
    S[Ticket text] --> N[normalize]
    N --> R[redact]
    R --> C[classify]
    C --> P[prioritize]
    P --> D[draft]
    D --> O[record + trace]
```

| Evidence layer | Open this | What proves the Pipes and Filters relation |
| --- | --- | --- |
| **Upstream case Skill** | [OpenMontage manifest](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/pipeline_defs/animated-explainer.yaml) | An ordered manifest names stage Skills and products; the correspondence remains candidate-level. |
| **Mock root Skill** | [`SKILL.md#agent-mode`](SKILL.md#agent-mode) | The runner owns five Filter stages and the shared `support-ticket.v1` contract. |
| **Pipe contract** | [`references/support-ticket-record-contract.md`](references/support-ticket-record-contract.md) | Each boundary validates and deep-copies the same record envelope. |
| **Executable proof** | [`scripts/run_demo.py`](scripts/run_demo.py) · [`tests/test_demo.py`](tests/test_demo.py) | Tests verify order, replacement, fail-stop attribution, and deterministic output. |

**The pattern-bearing line is:** source → normalize → redact → classify →
prioritize → draft → sink. Each stage is independently addressable and every
handoff uses the same explicit record contract.

## Mock Skill source

```text
sample/
├── SKILL.md
├── references/support-ticket-record-contract.md
├── scripts/run_demo.py
├── fixtures/valid/urgent-access.json
└── tests/test_demo.py
```

```markdown
<!-- Pipes and Filters: the runner owns order and the Pipe owns validation. -->
## Agent mode
1. Create `support-ticket.v1` from one bounded ticket.
2. Run five independent Filters in canonical order.
3. Validate and deep-copy before and after each Filter.
4. Stop at the first invalid result and attribute the stage.
```

## Learn the pattern

| Before: one opaque triage function | After: explicit Filters and Pipes |
| --- | --- |
| `caller -> triage(ticket)`<br>`  normalize + redact + classify + prioritize + draft`<br><br>The caller cannot replace one stage or identify its boundary failure. | `caller -> support-ticket-triage`<br>`  -> normalize -> redact -> classify -> prioritize -> draft`<br>`  -> record + canonical trace`<br><br>Each Filter is independently replaceable. |

### Use it when

| Use Pipes and Filters when | Keep it simple when |
| --- | --- |
| stages share a stable record contract and need independent replacement | the work is one indivisible operation |
| order and failure attribution should be visible | stages require rich cyclic collaboration |
| each stage can be tested with the same input/output envelope | boundary copying costs more than the isolation is worth |

### Skill-author recipe

1. Define one versioned record envelope before writing stage Skills.
2. Give every Filter one transformation and one stable interface.
3. Let one runner own order, validation, copying, and fail-stop behavior.
4. Test a positive run, a replacement Filter, and one failing boundary.

## Scenario

An operations team receives a ticket containing urgent language and an email
address. The pipeline normalizes the text, redacts the address, classifies the
request, assigns priority, and drafts a response without sharing mutable stage
state.

## Why this is Pipes and Filters

| POSA role | Skillware carrier in this example |
| --- | --- |
| Data Source | `run_pipeline` admission of ticket text |
| Filter | `normalize`, `redact`, `classify`, `prioritize`, `draft` |
| Pipe | `support-ticket.v1` validation and deep-copy boundary |
| Data Sink | detached final record and canonical trace |

## Contract and run commands

Input: `{"text": "URGENT email a@example.com: cannot login"}`.
Output is one `support-ticket.v1` record plus the exact stage trace. A failing
Filter stops later stages and reports its stage identifier.

From this directory, run the default fixture:

```bash
python3 scripts/run_demo.py
```

Run focused tests:

```bash
python3 -m unittest discover tests -v
```

The demo uses only the Python standard library, needs no network or
credentials, and models a sequential in-process pipeline. Buffering,
backpressure, concurrency, retries, and durable delivery are outside this
sample's contract.
