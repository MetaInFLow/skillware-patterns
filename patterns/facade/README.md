# 外观模式 / Facade

> **Scenario / 场景:** Production Incident Response / 生产事故响应

## 1. 先看问题 / The problem

An on-call operator sees a `5xx spike` and needs one incident response. Without
Facade, every caller must know the specialist sequence:

```text
caller -> diagnose
caller -> assess-impact
caller -> draft-communication
```

That spreads ordering, intermediate-result passing, and fallback behavior across
callers.

## 2. 模式一句话 / Pattern in one sentence

**One public Skill hides a group of specialist Skills behind one stable request
and result contract.**

```mermaid
flowchart LR
    C[Caller] --> F[Facade Skill\nincident-response-facade]
    F --> D[diagnose]
    F --> I[assess-impact]
    F --> M[draft-communication]
    F --> O[one stable result]
```

The caller chooses the operation; the Facade owns the internal sequence.

## 3. 现实中的 Skill / Existing Skill case

**Case Skill:** [Superpowers `using-superpowers`](https://github.com/obra/superpowers/blob/896224c4b1879920ab573417e68fd51d2ccc9072/skills/using-superpowers/SKILL.md), activated by the pinned [session-start hook](https://github.com/obra/superpowers/tree/896224c4b1879920ab573417e68fd51d2ccc9072/hooks/session-start). **Status: confirmed correspondence.**

What the case does: one bootstrap policy discovers the relevant specialist
Skills, selects them, and invokes them for the caller.

```text
session start
  -> using-superpowers policy
  -> discover specialist Skills
  -> select and invoke the needed Skills
```

The pattern signal is the stable entry policy plus hidden specialist routing.
The exact pinned paths and claim boundary are in
[`correspondence.md`](correspondence.md).

## 4. 本仓库的 Mock Skill / Mock Skill

Our concrete example is `incident-response-facade`:

```text
patterns/facade/sample/
├── SKILL.md                                  # public Facade contract
├── child-skills/
│   ├── diagnose/SKILL.md                      # specialist 1
│   ├── assess-impact/SKILL.md                 # specialist 2
│   └── draft-communication/SKILL.md           # specialist 3
├── scripts/run_demo.py
└── tests/test_demo.py
```

The important part of [`sample/SKILL.md`](sample/SKILL.md) is:

```markdown
<!-- Facade: callers see one operation; the root owns child order. -->
For `5xx spike`:
1. diagnose the service signal
2. assess customer impact
3. draft the status communication
4. return `summary`, `impact`, `actions`, and `communication`

For an unknown signal, keep the same result shape and request human triage.
```

Input is `{"service":"checkout-api","signal":"5xx spike"}`. Output always
has the same four top-level fields, including the fallback case.

## 5. 角色对应 / Role mapping

| GoF role | Skillware carrier in this example |
| --- | --- |
| Client | operator or task-level caller |
| Facade | root `sample/SKILL.md` |
| Subsystem | `diagnose`, `assess-impact`, and `draft-communication` |

## 6. 什么时候使用 / When to use

| Use Facade when | Keep it simple when |
| --- | --- |
| callers repeat the same multi-Skill sequence | there is one operation and one child |
| one public request/result contract should remain stable | callers genuinely need different workflows |
| internal Skills should remain replaceable | exposing every child operation is the goal |

## 7. 运行与验证 / Run and inspect

```bash
python3 sample/scripts/run_demo.py
python3 -m unittest discover -s sample/tests -v
```

Read the [complete sample](sample/), [participant map](participant-map.yaml),
[definition](definition.md), and [misuse case](misuse/explanation.md).

## 8. 证据边界 / Evidence boundary

The local sample is constructive evidence. The Superpowers paths provide the
recorded correspondence. Neither claim establishes cross-Host equivalence,
ecosystem frequency, or automatic quality improvement.
