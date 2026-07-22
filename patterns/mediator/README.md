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
