# 适配器模式（Adapter）

**Canonical source.** Adapter is the structural pattern described in the Gang
of Four tradition by Gamma, Helm, Johnson, and Vlissides in *Design Patterns:
Elements of Reusable Object-Oriented Software* (1994). This record transfers
that established pattern; it does not claim a new pattern or historical
priority for Skillware.

## Intent

Convert the interface of an existing component into the Target interface a
Client expects, so the Client and otherwise incompatible component can
collaborate without duplicating or changing the component's canonical
semantics.

## Forces

- One canonical issue contract should remain authoritative across trackers.
- GitHub, Jira, and Linear use different field names and severity
  representations even though the issue meaning must remain stable.
- Compatibility logic should be thin, explicit, and independently testable.
- A binding must reject an unsupported target or semantic gap instead of
  silently dropping identity or weakening severity.
- Each target contract can evolve, so every Adapter carries maintenance cost.

## Participants

- **Client:** the task caller that supplies a canonical issue and chooses a
  tracker.
- **Target:** the selected tracker's publishing payload contract, documented in
  `sample/references/tracker-contracts.md`.
- **Adaptee:** `sample/SKILL.md`, the canonical issue-publishing Skill whose
  `id`, `title`, `description`, and `severity` semantics remain authoritative.
- **Adapter:** the `adapt_github`, `adapt_jira`, and `adapt_linear` bindings in
  `sample/scripts/run_demo.py`. Each translates the canonical issue into one
  Target payload.
- **Agent Host and Agent Runtime:** execution context, not GoF Adapter
  participants. A Host binding can carry an Adapter, but the Host itself is not
  automatically the Client, Target, Adapter, or Adaptee.

## Collaboration

The Client submits `target` plus a canonical `issue`. The Adaptee contract
validates that all canonical fields are present and that severity is one of
`low`, `medium`, `high`, or `critical`. The selected Adapter constructs a new
Target payload: GitHub receives `body` and a severity label, Jira receives
`summary` and a named priority, and Linear receives its documented numeric
priority. Every binding copies canonical `id` to `external_id`, preserves the
title and description meaning, and leaves the input unchanged.

## Consequences

The canonical Skill remains tracker-independent, Client code uses one stable
issue model, and target-specific change is localized. Explicit translation
also makes identity and semantic parity testable. The costs are another layer
of indirection, a compatibility matrix that must be maintained, and the need
for target-specific runtime tests. Translation cannot manufacture a target
capability that does not exist.

## Skillware Mapping

Natural-language behavioral source can define the canonical Adaptee contract,
while a thin declarative or executable binding implements a Target contract.
The pattern depends on semantic translation and delegation, not on file names,
classes, or field renaming alone. An Agent Host can distribute or activate a
binding, and an Agent Runtime can interpret it, but those platform roles remain
execution context unless the concrete participant relation says otherwise.

## Applicability

Use Adapter when one independently meaningful Skill must serve clients through
multiple incompatible discovery, invocation, field, or result conventions and
the canonical procedure should stay unchanged. It is especially useful when
each mapping can state how identity, required values, and domain meaning are
preserved.

## Non-Applicability

Do not use Adapter when contracts are already compatible, when target-specific
policy legitimately changes domain behavior, or when the task is merely to
rename or copy a Skill file. Use Strategy when the procedure itself varies,
Facade when one entry operation coordinates a subsystem, and a validation
boundary when no compatible target semantics exist.

## Positive Evidence

The repository sample is **constructive** evidence: three thin bindings
translate one canonical issue into exact GitHub, Jira, and Linear payloads.
Focused tests check output equality, identity and semantic parity, input
immutability, rejection behavior, local paths, standalone imports, and CLI
execution. Separately, the frozen gstack case supplies a **strong
correspondence** for generated and system-specific Host surfaces.

## Counter-Evidence

The deterministic oracle does not exercise a real tracker or Agent Host. A
payload that looks correct locally can still fail against a remote API. The
gstack source observations show generation and Host-specific rewriting at one
revision but do not prove equivalent execution across every advertised Host.

## False Positives

A Skill copy that renames `title` to `summary` while dropping canonical `id`
and severity meaning is not an Adapter. It neither preserves identity nor
implements semantic parity with the Adaptee. The
[`misuse/SKILL.md`](misuse/SKILL.md) artifact intentionally demonstrates this
near miss.

## Open-Source Correspondence

gstack is evaluated at commit
`11de390be1be6849eb9a15f91ff4922dd16c589a`. Its generator and system-specific
Host configurations translate canonical Skill sources into target discovery,
frontmatter, path, and tool-name conventions. The canonical Skill semantics
are the Adaptee, each generated or system-specific binding is an Adapter, the
Host-specific Skill contract is the Target, and task-level invocation is the
Client. See [`correspondence.md`](correspondence.md) for pinned links and the
runtime-parity limitation. This ecosystem claim is independent of the local
constructive sample.

## Verification

From `sample/`, run `python3 scripts/run_demo.py` and
`python3 -m unittest discover tests -v`. Verification checks exact payloads for
all three trackers, identity and meaning preservation, non-mutation of input,
clear nonzero failure for unknown targets and malformed issues, resolution of
participant and evidence paths, and absence of network or cross-pattern
imports.

## Limitations

One constructive scenario and one strong ecosystem correspondence do not
establish pattern frequency, comparative quality, or cross-Host runtime
parity. The demo uses deterministic Python as an executable oracle for the
behavioral contract; it does not simulate probabilistic Agent Runtime
interpretation or tracker APIs. The mapping preserves established GoF forces
and participants without asserting that Skillware invented Adapter.
