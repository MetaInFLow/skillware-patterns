# Mediator

**Canonical source.** Mediator is the behavioral pattern described in the Gang
of Four tradition by Gamma, Helm, Johnson, and Vlissides in *Design Patterns:
Elements of Reusable Object-Oriented Software* (1994). This record transfers
that established pattern and makes no claim of invention or priority.

## Intent

Define an object that encapsulates how a set of objects interact, promoting
loose coupling by keeping those objects from referring to one another
explicitly and allowing their interaction to vary independently.

## Forces

- Four deployment specialists must contribute to one release decision without
  acquiring references to one another.
- The joint readiness rule needs one owner, but specialist checks must remain
  inside their respective build, security, docs, and approval Skills.
- Every required report must be present, valid, uniquely addressed, and
  processed exactly once in a stable order.
- A specialist exception must fail closed without preventing later specialists
  from reporting.
- Input and output must remain bounded, immutable at the caller boundary, and
  deterministic enough to serve as an executable oracle.
- Centralization simplifies relationships but can make the coordinator complex
  or turn it into a God Skill if specialist work migrates into it.

## Participants

- **Mediator:** the `deployment-readiness-v1` report interface implemented by
  the Python `Mediator` boundary. It defines how a Colleague reports without
  naming other Colleagues.
- **ConcreteMediator:** the Deployment Coordinator root Skill and
  `DeploymentCoordinator`. It injects and addresses Colleagues, isolates
  failures, owns readiness policy, and returns the final release decision.
- **Colleague:** the build, security, docs, and approval child Skills plus
  `Colleague` instances. Each performs only its bounded specialist work and
  reports one status to the Mediator.
- **Agent Host and Agent Runtime:** execution context, not GoF Mediator
  participants. Their activation and interpretation are not observable here.

## Collaboration

The public API validates and copies all statuses before constructing a
ConcreteMediator. The ConcreteMediator then prevalidates the complete injected
set, including types, non-empty string IDs, exact unique identities, and unbound
state, before binding any item. Rejection leaves every previously unbound
Colleague reusable. It orders the admitted set as build, security, docs,
approval, binds every Colleague to its own address, and addresses each once with
only that participant's status. A Colleague runs its specialist callable and reports
back through `Mediator.receive`; it has no peer collection or peer path. The
ConcreteMediator treats an exception or invalid callable report as `fail` and
continues. After all four attempts, it releases only if every final report is
`pass`; otherwise it blocks. The returned status mapping is a fresh copy in
canonical order and the communication path is always
`participants->mediator->release`.

## Consequences

Direct participant coupling falls from an all-to-all mesh to four central
relationships. Readiness policy, order, failure handling, validation, and
decision output become auditable. Costs include a central policy dependency,
the risk of coordinator growth, and trusted-code assumptions around in-process
binding. A failed callable loses its detailed error in the public result by
design and contributes only fail-closed status.

## Skillware Mapping

Behavioral Source defines and informs the root ConcreteMediator and child
Colleague Skill Artifacts. Those artifacts, their reference contract,
fixtures, and oracle form one constructive Skillware Unit. The standard-library
Python code is a deterministic oracle for the contract; it does not interpret
natural-language Skills.

### Final ontology

The source-pattern roles remain exactly **Mediator**, **ConcreteMediator**, and
**Colleague**. A Behavioral Source is persisted in a Skill Artifact carried by
a Skillware Unit. An Agent Host activates that unit and an Agent Runtime
interprets activated Behavioral Source in context, but neither becomes a GoF
participant. An Execution Trace records situated performance and Task Outcome
is the evaluated effect; this static sample fabricates neither.

## Applicability

Use Mediator when multiple independently owned Skills must contribute to joint
policy, participant topology would otherwise become a peer mesh, and one
coordinator can own interaction without absorbing specialist behavior.
Deployment gates, approval coordination, incident roles, and multi-specialist
reviews are common fits.

## Non-Applicability

Do not use Mediator for a simple independent list with no interaction policy,
for a fixed data transformation pipeline, or when a domain service should own
the specialist work itself. Do not centralize merely to hide a poorly defined
contract. If the coordinator executes all checks, it is a God Skill rather than
a sound Mediator.

## Positive Evidence

The repository sample is **constructive** evidence. It materializes all three
canonical roles; four isolated child Skills; the literal
`coordinate({'build':'pass','security':'pass','docs':'pass','approval':'pass'})`
API; exact release and blocked decisions; the literal communication path;
canonical addressing, invocation count, and order; missing, extra, duplicate,
wrong-type, and invalid status rejection; callable injection; fail-closed
exception and invalid-report isolation; no input mutation; deterministic
fixtures; stable CLI errors; and a standard-library standalone harness.

## Counter-Evidence

The Python oracle does not prove Agent Runtime interpretation, Agent Host
activation, or absence of out-of-band communication. It tests cooperative
objects in one process. It also reduces specialist failures to `fail`, so a
production system needs a separate protected diagnostic channel. Static Skill
text cannot by itself prove that a model will never invoke a peer.

## False Positives

An all-to-all peer workflow is not Mediator because Colleagues still refer to
one another. A central God Skill that performs build, security, docs, and
approval work is not sound Mediator because it removes specialist ownership
instead of encapsulating interaction. Both forms appear in
[`misuse/SKILL.md`](misuse/SKILL.md).

## Open-Source Correspondence

Anthropic financial-services is a **candidate correspondence** at commit
`4aa51ed3d379731f8f9beff498d749580372699c`. The inspected GL Reconciler
orchestrator, three subagent manifests, and cookbook test show central
orchestration, specialist leaf workers, and a depth-one check. The peer source
does not establish a common Colleague contract or verify runtime decision
behavior, invocation order, or failure isolation. See
[`correspondence.md`](correspondence.md) and the
[frozen evidence](evidence/financial-services-frozen-case.md).

## Verification

From `sample/`, run `python3 scripts/run_demo.py` and `python3 -m unittest
discover tests -v`. Tests cover release only after four pass reports, blocking
for every failure position, exact status copies, injected addressing, once-only
canonical order, callable failure and invalid-report isolation, duplicate,
missing, extra, and invalid participants and statuses, cross-mediator binding,
child peer isolation, malformed and non-UTF-8 input, deterministic fixtures,
stable errors, and default CLI output. The repository root harness copies and
executes the materialized record automatically.

## Limitations

The sample assumes trusted in-process code. Private references, type checks,
and binding rules are contract boundaries, not a security sandbox: reflection,
subclass overrides, monkeypatching, arbitrary memory access, or shared external
services can bypass them. The deterministic oracle does not interpret natural
language. Production use needs capability enforcement, authenticated reports,
timeouts, concurrency policy, protected diagnostics, replay resistance,
observability, and explicit audit of real participant communication.
