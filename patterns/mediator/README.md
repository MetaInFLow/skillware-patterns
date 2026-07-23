# 中介者模式（Mediator）

This record transfers the canonical Gang of Four Mediator pattern to Skillware.
It maps the coordination interface to **Mediator**, the central deployment
policy owner to **ConcreteMediator**, and the four isolated specialist Skills to
**Colleague**.

The standalone sample is **Deployment Coordinator / 部署协调**. Build,
security, documentation, and approval colleagues report one status each to the
central coordinator. They never invoke peers. The coordinator alone applies
the all-pass release policy and returns either `release` or `blocked`.

Start with [`definition.md`](definition.md), inspect the exact role mapping in
[`participant-map.yaml`](participant-map.yaml), then run the [`sample`](sample/).
The public correspondence remains candidate-only because the inspected
financial-services cookbook shows central orchestration and leaf workers but
does not establish a shared Colleague contract or runtime decision behavior.

## Upstream Skill example

The high-star comparison is [anthropics/financial-services](https://github.com/anthropics/financial-services):
`managed-agent-cookbooks/gl-reconciler/agent.yaml` coordinates the isolated
`subagents/reader.yaml`, `subagents/critic.yaml`, and `subagents/resolver.yaml`
workers, with a reproducible check in `scripts/test-cookbooks.sh`. The exact
revision and candidate boundary are documented in the [upstream evidence
record](../../docs/upstream-skill-evidence.md#mediator--中介者模式). The local
demo makes the central status contract and no-peer rule executable.
