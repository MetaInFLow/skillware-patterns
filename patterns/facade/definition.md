# 外观模式（Facade）

**Canonical source.** Facade is the structural pattern described in the Gang
of Four tradition by Gamma, Helm, Johnson, and Vlissides in *Design Patterns:
Elements of Reusable Object-Oriented Software* (1994). This record transfers
that established pattern; it does not claim a new pattern or historical
priority for Skillware.

## Intent

Provide one stable, simplified access contract over a set of independently
addressable subsystem capabilities. A client can perform the common task
without learning the subsystem's internal selection and coordination details.

## Forces

- The client needs one task-level operation, while specialists retain narrower
  responsibilities and remain inspectable in their own right.
- Direct specialist access may remain useful, but routine callers should not
  need to understand selection, ordering, or fallback policy.
- The public contract should stay stable as subsystem organization changes.
- Centralization reduces client coupling but can make the Facade too broad or
  turn it into a policy bottleneck.

## Participants

- **Client:** the operator or task-level agent execution that invokes the root
  incident-response Skill.
- **Facade:** `sample/SKILL.md`, which defines the single request/result
  contract and the coordination and fallback policy.
- **Subsystem:** the diagnosis, impact-assessment, and communication child
  Skills. Each has an independently inspectable `SKILL.md`.
- **Agent Host and Agent Runtime:** supporting runtime roles, not Facade
  participants by default. The Agent Host activates the Skillware Unit; the
  Agent Runtime interprets its activated behavioral source.

## Collaboration

The Client supplies `service` and `signal` to the Facade. For the known `5xx
spike` signal, the Facade obtains a diagnosis, passes that result with the
incident context to impact assessment, then passes the returned assessment to
communication drafting. It assembles only the four public result fields. For
an unknown signal, it applies the declared human triage fallback while
preserving the same result contract. Subsystem routing details are not returned
to the Client.

## Consequences

The client learns one interface and is insulated from subsystem coordination.
Specialists remain independently inspectable and can evolve behind the public
contract. The trade-offs are added indirection, the risk of hiding useful
specialist capability, and pressure for the entry Skill to accumulate too
much policy. Changes to the public contract still require client-facing
compatibility review.

## Skillware Mapping

Natural-language behavioral source in a root Skill can carry the Facade
operation. A bootstrap or invocation policy can activate that entry contract,
and the Agent Runtime can interpret its relevance, routing, and fallback
rules through the Agent Host's Skill-loading operation. A new plugin method or
class is not required. The transfer depends on the participant relation and
observable access behavior, not on file type or the use of the word
"facade."

## Applicability

Use Facade when callers repeatedly need a coherent task spanning multiple
specialists, when one stable request/result contract can hide coordination
details, and when the subsystem capabilities still have meaningful independent
identities. It is particularly useful when activation or bootstrap policy
should consistently route ordinary work through one entry Skill.

## Non-Applicability

Do not use Facade for a single atomic Skill with no subsystem, for a directory
that merely groups related Skills, or when clients must control every
specialist interaction directly. Use a different pattern when the primary
force is interface translation, interchangeable algorithms, event delivery,
or uniform leaf/composite treatment.

## Positive Evidence

The repository sample is **constructive** evidence: its root incident-response
Skill coordinates three child Skills, returns one stable contract for both the
known and fallback paths, and is exercised by focused tests. Separately, the
frozen Superpowers case supplies a **confirmed correspondence** for a real
open-source participant relation.

## Counter-Evidence

Natural-language relevance judgment and specialist activation still depend on
the Agent Host and Agent Runtime. Source inspection does not establish equal
activation reliability across Hosts. The Facade relation also does not imply
that clients are prohibited from invoking a specialist directly.

## False Positives

A README, menu, registry, or root `SKILL.md` that only names child Skills is
not a Facade. Neither is a router label without a unified client operation,
actual subsystem coordination, and defined fallback behavior. The
[`misuse/SKILL.md`](misuse/SKILL.md) artifact intentionally demonstrates this
near miss.

## Open-Source Correspondence

Superpowers `using-superpowers` is evaluated at commit
`896224c4b1879920ab573417e68fd51d2ccc9072`, exact path
`skills/using-superpowers/SKILL.md`. Task-level agent execution is the Client,
that Skill supplies the Facade access policy, and the specialist workflow
Skills are the subsystem. A SessionStart hook bootstraps the policy; the Agent
Host loads it and the Agent Runtime interprets it. See
[`correspondence.md`](correspondence.md) for the pinned links and evidence
boundary. This ecosystem claim is independent of the local constructive
sample.

## Verification

From `sample/`, run `python3 scripts/run_demo.py` and
`python3 -m unittest discover tests -v`. Verification checks exact output for
`5xx spike`, the exact `request-human-triage` fallback for an unknown signal,
nonzero failure for malformed input, resolution of all participant paths, and
absence of network or cross-pattern imports.

## Limitations

One constructive scenario and one confirmed correspondence do not establish
ecosystem frequency, automatic quality improvement, or cross-Host behavioral
equivalence. The demo uses deterministic Python functions as an executable
oracle for behavioral source; it does not simulate probabilistic model
interpretation. The mapping preserves the established GoF forces and
participants without asserting that Skillware invented Facade.
