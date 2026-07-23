# 外观模式（Facade）

## 一眼看懂 / At a glance

**一句话：** 调用者只面对一个入口 Skill，入口 Skill 隐藏多个专家 Skill 的调用顺序。

```mermaid
flowchart LR
    C[Caller] --> F[Facade Skill\nincident-response-facade]
    F --> D[diagnose]
    F --> I[assess-impact]
    F --> M[draft-communication]
    F --> O[One stable result]
```

| | Case Skill（上游案例） | Mock sample（本仓库构造） |
| --- | --- | --- |
| **是哪一个** | [Superpowers `using-superpowers`](https://github.com/obra/superpowers/blob/896224c4b1879920ab573417e68fd51d2ccc9072/skills/using-superpowers/SKILL.md) | [`incident-response-facade`](sample/SKILL.md) |
| **哪里体现模式** | 一个入口策略负责发现、选择并调用其他 Skills | 一个入口 Skill 编排三个专家 Skill，并隐藏内部顺序 |
| **怎么运行** | 上游 Host hook 激活它 | `python3 sample/scripts/run_demo.py` |

**看哪三个文件：** `sample/SKILL.md`、`sample/child-skills/`、`participant-map.yaml`。

This record transfers the Gang of Four Facade pattern to Skillware. It maps a
stable entry Skill to the Facade, independently addressable specialist Skills
to the subsystem, and the operator or task-level agent execution to the
Client.

The standalone sample is **Production Incident Response / 生产事故响应**. Its
root Skill accepts `service` and `signal`, coordinates three specialist Skills,
and always returns `summary`, `impact`, `actions`, and `communication`.

- [English definition](definition.md)
- [中文定义](definition.zh-CN.md)
- [Participant map](participant-map.yaml)
- [Open-source correspondence](correspondence.md)
- [Runnable sample](sample/)
- [Misuse discriminator](misuse/explanation.md)

## Case Skill: upstream implementation

**Case Skill:** `obra/superpowers/skills/using-superpowers/SKILL.md`.

The high-star comparison is [obra/superpowers](https://github.com/obra/superpowers):
`skills/using-superpowers/SKILL.md` is the stable entry policy, while
`hooks/session-start` and `hooks/hooks.json` activate it over specialist Skills.
The observation is pinned and qualified in the
[upstream evidence record](../../docs/upstream-skill-evidence.md#facade--外观模式).
The complete offline local analogue is [`sample/SKILL.md`](sample/SKILL.md).

## Mock sample Skill: this repository

**Mock Skill:** [`sample/SKILL.md`](sample/SKILL.md), named
`incident-response-facade`. It delegates to the `diagnose`, `assess-impact`,
and `draft-communication` child Skills before returning one stable result.

The Facade idea is implemented by hiding specialist order and fallback policy
behind one public operation. Run `python3 sample/scripts/run_demo.py`; the
participant relation is recorded in [`participant-map.yaml`](participant-map.yaml).

The constructive sample and the confirmed Superpowers correspondence are
separate evidence claims. Neither establishes ecosystem frequency,
cross-Host equivalence, or an improvement in quality.
