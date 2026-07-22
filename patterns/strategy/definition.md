# Strategy

**Canonical source.** Strategy is the behavioral pattern described in the Gang
of Four tradition by Gamma, Helm, Johnson, and Vlissides in *Design Patterns:
Elements of Reusable Object-Oriented Software* (1994). This record transfers
that established pattern; it does not claim invention or historical priority.

## Intent

Define a family of algorithms, encapsulate each one behind a common Strategy
interface, and make them interchangeable so the algorithm can vary
independently of its Context.

## Forces

- Low-risk changes need quick feedback while security-sensitive or broader
  changes justify more review work.
- Callers need one request and result interface regardless of review depth.
- Selection policy must be explicit and testable rather than hidden in model
  choice, conversational judgment, or mutable global context.
- Alternative procedures must perform the same task; unrelated branches cannot
  be substituted merely because one router can reach them.
- A richer algorithm may find more issues, but it must not force the Context or
  callers to understand a different output schema.
- Separate strategies add artifacts, conformance duties, and a selection policy
  that can itself make poor decisions.

## Participants

- **Context:** the root Risk-Aware Code Review Skill and deterministic
  `RiskAwareCodeReview`. It validates a request, selects or accepts one
  addressed strategy, delegates review, and validates the result.
- **Strategy:** the `risk-aware-code-review-v1` `review` contract shared by all
  procedures.
- **ConcreteStrategy:** the Fast Scan and Deep Review child Skills and
  corresponding built-in Python objects. Each built-in owns a distinct rule
  set behind the same operation and request/result contract. An injected
  replacement may use another algorithm that satisfies that shared contract.
- **Agent Host and Agent Runtime:** execution context, not GoF Strategy
  participants. Their activation and interpretation behavior is not observable
  in this constructive sample.

## Collaboration

The Context validates the exact request and selects Deep Review when the change
is security-sensitive or contains at least four files; otherwise it selects
Fast Scan. A caller can also address either registered strategy explicitly for
audit, replay, or conformance testing. The Context passes an independent copy
of the same request to exactly one ConcreteStrategy. Fast Scan applies three
high-signal checks. Deep Review applies those checks plus three contextual
checks. The Context validates the selected identity, reviewed-file order,
finding structure and unique identity, and strictly typed derived summary before
returning the result. JSON member order has no semantic effect; the boundary
canonicalizes output fields and findings by request file, line, and rule ID.
The Context does not inspect an injected procedure or require built-in rules.

The demo module also retains a compact plan-compatibility `review` API. It
accepts only integer file count and security sensitivity, chooses Deep Review
for security sensitivity or more than five files, and returns exactly strategy,
findings, and confidence. That compact surface is separate from the richer
file-content CLI contract and the two objects are not mutually substitutable.

## Consequences

Review depth varies without changing callers or the result interface. Selection
and algorithm behavior can be tested separately, strategies can be injected or
replaced, and incompatible outputs fail at one boundary. Costs include one
artifact per procedure, duplicated conformance work, an explicit policy that
must evolve with risk, and the possibility that a cheaper strategy misses an
issue that a deeper one would report.

## Skillware Mapping

Natural-language Behavioral Source defines the Context policy, common Strategy
operation, and two ConcreteStrategy procedures. The root and child Skill
Artifacts form one coherent Skillware Unit. JSON fixtures supply review
requests; standard-library Python provides a deterministic oracle for
selection, delegation, and output conformance. It does not activate or
interpret the Skill files.

### Final ontology

The canonical roles remain exactly **Context**, **Strategy**, and
**ConcreteStrategy**. `Agent Host` activates a Skillware Unit and `Agent
Runtime` interprets activated Behavioral Source, but neither contextual object
becomes a source-pattern participant. An Execution Trace records situated
performance and Task Outcome is the evaluated effect; this static sample
fabricates neither.

## Applicability

Use Strategy when several procedures solve the same task, conform to one
interface, and must vary by policy or explicit choice without rewriting their
caller. It fits review depth, search algorithms, ranking methods, compression
policies, pricing calculations, or validation modes when substitution is a real
contract requirement.

## Non-Applicability

Do not use Strategy for sequential steps that all must run, lifecycle behavior
controlled by persisted state, wrappers that add responsibility, or unrelated
subcommands with incompatible inputs and results. Model choice alone is not
Strategy when no algorithm contract or independently addressable procedures are
defined.

## Positive Evidence

The repository sample is **constructive** evidence. It materializes all three
GoF roles, one exact request/result contract, two distinct strategies, explicit
risk selection, direct addressing, dependency injection, boundary validation,
canonical output, unique finding identities, and deterministic fixtures. Focused
tests prove selection separately from delegation, substitution through the same
Context, built-in rule ownership separately from shared conformance, strict
summary integer types, semantic-free mapping order, duplicate JSON member and
lone-surrogate rejection, exact outputs, stable errors, input immutability, and
standard-library execution without network or model dependencies.

## Counter-Evidence

The Python oracle cannot prove that an Agent Runtime interprets the Behavioral
Source identically or that a compatible Agent Host activates it. The lexical
rules do not parse programming languages, inspect unchanged context, follow
data flow, execute tests, evaluate exploitability, or establish production
security quality. The threshold of four files is scenario-specific rather than
an empirical optimum.

## False Positives

A conditional router is not Strategy when its branches perform different jobs
or expose different interfaces. Alternative prompts are not necessarily
strategies when callers cannot address and substitute them through one
operation. The [`misuse/SKILL.md`](misuse/SKILL.md) artifact deliberately routes
dependency discovery and deployment approval through incompatible contracts.

## Open-Source Correspondence

UI/UX Pro Max is a **candidate correspondence** at commit
`8a81ed60272d21d4b8808f7308d49a0b1b000555`. Its pinned Skill-backed CLI routes
domain search, stack search, and design-system generation. The reviewed paths
do not declare one request/result contract for every branch: search operations
return mappings with differing metadata while design-system generation returns
rendered text. They also do not show conformance testing or complete
Context-to-Strategy substitution. The paper qualification remains:
"Open-source correspondence is motivation only; comparative benefit requires
runtime study." See [`correspondence.md`](correspondence.md) and the
[frozen evidence](evidence/ui-ux-pro-max-frozen-case.md).

## Verification

From `sample/`, run `python3 scripts/run_demo.py` and `python3 -m unittest
discover tests -v`. Verification covers low-risk, security-sensitive, and
file-threshold selection; explicit addressing; injected alternatives; distinct
rule behavior; the verbatim compact compatibility API; exact shared result
fields; canonical order and unique finding identities; malformed injected
results; schema, type, bound, UTF-8, surrogate, duplicate-member JSON, and path
validation; deterministic reruns; and input immutability. The repository
harness copies and runs the sample standalone.

## Limitations

One constructive scenario does not establish prevalence, comparative benefit,
production review accuracy, or cross-Host behavioral equivalence. Extending the
request, rule set, threshold, severity policy, or result requires a versioned
contract change and new conformance fixtures. Strategy interchangeability does
not imply equal cost or equal findings; it requires substitutability through
the declared interface. The compact compatibility API and richer CLI are two
explicitly separate public contracts and must not be treated as interchangeable.
