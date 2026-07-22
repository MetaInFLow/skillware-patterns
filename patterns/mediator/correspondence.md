# Mediator correspondence

## Public open-source candidate

- **Project:** Anthropic financial-services
- **Revision:** `4aa51ed3d379731f8f9beff498d749580372699c`
- **Exact orchestrator path:** `managed-agent-cookbooks/gl-reconciler/agent.yaml`
- **Exact subagent paths:**
  `managed-agent-cookbooks/gl-reconciler/subagents/reader.yaml`,
  `managed-agent-cookbooks/gl-reconciler/subagents/critic.yaml`, and
  `managed-agent-cookbooks/gl-reconciler/subagents/resolver.yaml`
- **Exact test path:** `scripts/test-cookbooks.sh`
- **Status:** candidate correspondence
- **Frozen record:** [frozen evidence](evidence/financial-services-frozen-case.md)

At the pinned paths, the GL Reconciler manifest declares one orchestrator and
three `callable_agents`. Its source comment says the orchestrator dispatches,
aggregates, and hands off instead of reading counterparty documents directly.
The subagents have different specialist responsibilities and declare no
callable agents. The shell test checks that resolved cookbook bodies remain
depth one. This is source-observed central orchestration and leaf-worker
separation.

The inspected source does not establish one common Colleague report contract,
prove that all peer communication is impossible at runtime, or test the
orchestrator's final decision behavior. It is also a peer public repository,
not the constructive record's reference implementation. The claim therefore
remains candidate-only.

## Constructive sample

- **Status:** constructive
- **Mediator contract:**
  [`sample/references/deployment-readiness-contract.md`](sample/references/deployment-readiness-contract.md)
- **ConcreteMediator:** [`sample/SKILL.md`](sample/SKILL.md)
- **Colleagues:** [`sample/child-skills/`](sample/child-skills/)
- **Executable oracle:** [`sample/scripts/run_demo.py`](sample/scripts/run_demo.py)
- **Focused verification:** [`sample/tests/test_demo.py`](sample/tests/test_demo.py)

The local sample supplies the missing shared status contract, central release
policy, exact addressing and order, duplicate rejection, failure isolation,
and deterministic decision tests. It does not establish upstream or Agent
Runtime behavior.
