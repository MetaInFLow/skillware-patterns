# 状态模式（State）

> **人话：** 当前状态决定现在允许做什么，以及成功后会进入什么状态。

## 1. 先看场景

供应商准入要经过 `draft → verified → approved → activated`。处于 `draft` 时可以验证，处于 `approved` 时才可以激活。

## 2. 先看完整 Skill

**Mock Skill：** 我们构造的 Skill 叫 `vendor-onboarding-workflow`：

```text
patterns/state/sample/
├── SKILL.md                                  # Context
├── child-skills/
│   ├── draft/SKILL.md                         # ConcreteState
│   ├── verified/SKILL.md
│   ├── approved/SKILL.md
│   └── activated/SKILL.md
├── references/vendor-state-contract.md
├── scripts/run_demo.py
└── tests/test_demo.py
```

关键行为：

```markdown
<!-- 当前 State Skill 拥有当前阶段的合法动作。 -->
1. load the vendor's persisted state
2. invoke the Skill named by that state
3. reject an action illegal for that state
4. persist the successor state after success
```

## 3. 这个模式解决了什么

### 没有 State

```text
root Skill:
  if draft: verify rules
  if verified: approve rules
  if approved: activate rules
```

所有阶段规则集中在一个越来越大的入口里。

### 使用 State

```text
persisted state -> current State Skill -> legal action -> successor state
```

入口只负责恢复状态和保存转换结果，阶段行为放在对应的 State Skill 中。

## 4. 市面上的 Skill 案例

**Case Skill：** [OpenMontage checkpoint protocol](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/skills/meta/checkpoint-protocol.md) 和 [checkpoint implementation](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/lib/checkpoint.py)。

它体现 State 思想的地方：checkpoint 保存阶段和状态信息，后续执行可以从已恢复的位置继续。

```text
load checkpoint -> recover current stage -> continue permitted work
```

公开文件显示了持久化检查点，完整的 GoF 状态委托关系记录为 `candidate correspondence`。

## 5. 这个例子对应哪些角色

| State 角色 | Skillware 中的对应物 |
| --- | --- |
| Context | 根 onboarding Skill 和持久化记录 |
| State | 状态契约 `vendor-onboarding-state-v1` |
| ConcreteState | `draft`、`verified`、`approved`、`activated` |

## 6. 什么时候用

适合：状态会改变允许的动作；状态需要独立测试；状态需要在重启后恢复。

不适合：状态只用于展示；只有一个简单枚举；流程引擎已经完整管理了状态转换。

## 7. 运行

```bash
python3 sample/scripts/run_demo.py
python3 -m unittest discover -s sample/tests -v
```

继续阅读：[完整样例](sample/)、[角色映射](participant-map.yaml)、[模式定义](definition.md)、[反例](misuse/explanation.md)。

## 8. 边界

本地样例验证了合法转换、持久化和重启恢复。OpenMontage 只支持候选级对应关系，本地样例不代表跨 Host 的状态持久化保证。
