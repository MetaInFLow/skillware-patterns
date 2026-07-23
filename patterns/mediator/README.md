# 中介者模式（Mediator）

## 一眼看懂 / At a glance

**一句话：** 多个专家 Skill 不互相调用，统一向一个协调 Skill 报告。

```mermaid
flowchart TB
    B[Build] --> M[Mediator\ndeployment-coordinator]
    S[Security] --> M
    D[Docs] --> M
    A[Approval] --> M
    M --> O[release / blocked]
```

| | Case Skill（上游案例） | Mock sample（本仓库构造） |
| --- | --- | --- |
| **是哪一个** | [GL reconciler coordinator](https://github.com/anthropics/financial-services/blob/4aa51ed3d379731f8f9beff498d749580372699c/managed-agent-cookbooks/gl-reconciler/agent.yaml) + [reader/critic/resolver](https://github.com/anthropics/financial-services/tree/4aa51ed3d379731f8f9beff498d749580372699c/managed-agent-cookbooks/gl-reconciler/subagents) | [`deployment-coordinator`](sample/SKILL.md) |
| **哪里体现模式** | 一个中心 cookbook 协调多个 leaf workers（候选对应） | 四个 Colleague 只向 Coordinator 报告，Coordinator 独立做 all-pass 决策 |
| **怎么运行** | 由 cookbook coordinator 驱动 | `python3 sample/scripts/run_demo.py` |

**看哪三个文件：** `sample/SKILL.md`、`sample/child-skills/`、`sample/references/deployment-readiness-contract.md`。

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

## Case Skill: upstream implementation

**Case Skill:** the GL reconciler coordinator in
`anthropics/financial-services/managed-agent-cookbooks/gl-reconciler/agent.yaml`.

The high-star comparison is [anthropics/financial-services](https://github.com/anthropics/financial-services):
`managed-agent-cookbooks/gl-reconciler/agent.yaml` coordinates the isolated
`subagents/reader.yaml`, `subagents/critic.yaml`, and `subagents/resolver.yaml`
workers, with a reproducible check in `scripts/test-cookbooks.sh`. The exact
revision and candidate boundary are documented in the [upstream evidence
record](../../docs/upstream-skill-evidence.md#mediator--中介者模式). The local
demo makes the central status contract and no-peer rule executable.

## Mock sample Skill: this repository

**Mock Skill:** [`sample/SKILL.md`](sample/SKILL.md), named
`deployment-coordinator`. It addresses `build`, `security`, `docs`, and
`approval` child Skills and alone applies the all-pass release policy.

The Mediator idea is implemented by a single report boundary and no peer-to-peer
calls. Run `python3 sample/scripts/run_demo.py`; the mapping is in
[`participant-map.yaml`](participant-map.yaml).
