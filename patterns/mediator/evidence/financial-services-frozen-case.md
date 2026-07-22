# Financial-services frozen Mediator candidate

**Project:** Anthropic financial-services

**Pinned revision:** `4aa51ed3d379731f8f9beff498d749580372699c`

**Claim status:** candidate correspondence

## Inspected source

- [`managed-agent-cookbooks/gl-reconciler/agent.yaml`](https://github.com/anthropics/financial-services/blob/4aa51ed3d379731f8f9beff498d749580372699c/managed-agent-cookbooks/gl-reconciler/agent.yaml)
- [`managed-agent-cookbooks/gl-reconciler/subagents/reader.yaml`](https://github.com/anthropics/financial-services/blob/4aa51ed3d379731f8f9beff498d749580372699c/managed-agent-cookbooks/gl-reconciler/subagents/reader.yaml)
- [`managed-agent-cookbooks/gl-reconciler/subagents/critic.yaml`](https://github.com/anthropics/financial-services/blob/4aa51ed3d379731f8f9beff498d749580372699c/managed-agent-cookbooks/gl-reconciler/subagents/critic.yaml)
- [`managed-agent-cookbooks/gl-reconciler/subagents/resolver.yaml`](https://github.com/anthropics/financial-services/blob/4aa51ed3d379731f8f9beff498d749580372699c/managed-agent-cookbooks/gl-reconciler/subagents/resolver.yaml)
- [`scripts/test-cookbooks.sh`](https://github.com/anthropics/financial-services/blob/4aa51ed3d379731f8f9beff498d749580372699c/scripts/test-cookbooks.sh)

These are the only upstream paths used for the Mediator correspondence claim.
Every URL uses the same full immutable commit id.

## Observed relation

The GL Reconciler `agent.yaml` calls itself an orchestrator, states that it
dispatches, aggregates, and hands off rather than reading counterparty
documents directly, and registers reader, critic, and resolver manifests as
`callable_agents`. The reader extracts candidate breaks, the critic independently
re-verifies them, and the resolver alone writes the result. All three subagent
manifests declare empty `callable_agents`. This is source-observed central orchestration
with specialist leaf workers rather than an explicit peer mesh.

The cookbook test dry-runs all managed-agent manifests and rejects any subagent
that itself exposes callable agents, supporting the depth-one observation.

## Counterevidence and limits

These files do not define a single common Colleague method or result schema
across reader, critic, and resolver. They do not prove at runtime that
specialists cannot communicate out of band, and the dry-run test does not
exercise final orchestrator decision behavior, invocation count, order, or
failure isolation. The project is a peer public source candidate, not a
reference implementation for this constructive record. Consequently the
common Colleague contract and runtime decision behavior remain incomplete and
the mapping is candidate-only.

Static source inspection also cannot establish Agent Host activation, Agent
Runtime interpretation, an Execution Trace, or a Task Outcome.
