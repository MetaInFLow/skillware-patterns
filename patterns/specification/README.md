# 规约模式（Specification）

> **人话：** 把每条业务规则写成可以命名、组合、测试和解释的规则 Skill。

## 1. 先看场景

费用审批要检查收据、预算、授权金额和部门。规则以后还会被复用到不同审批政策中，调用者需要知道每条规则为什么通过或失败。

## 2. 先看完整 Skill

**Mock Skill：** 我们构造的 Skill 叫 `expense-approval-policy`：

```text
patterns/specification/sample/
├── SKILL.md                                  # policy composition
├── child-skills/
│   ├── has-receipt/SKILL.md                   # leaf Specification
│   ├── within-budget/SKILL.md
│   ├── authorized-amount/SKILL.md
│   └── department/SKILL.md
├── references/expense-candidate-contract.md
├── scripts/run_demo.py
└── tests/test_demo.py
```

关键行为：

```markdown
<!-- 每条规则都有同一个 Candidate 输入和解释接口。 -->
HasReceipt() & WithinBudget() & AuthorizedAmount(1000) & ~Department("restricted")

Validate the Candidate first, then evaluate named rules left-to-right.
Return the decision together with a structured explanation trace.
```

## 3. 这个模式解决了什么

| 没有 Specification | 使用 Specification |
| --- | --- |
| `caller -> eligible(expense)`<br><br>收据、预算、授权和部门判断全部藏在一个函数里，规则无法单独命名、复用、组合或解释。 | `Candidate`<br>`  -> HasReceipt`<br>`  -> WithinBudget`<br>`  -> AuthorizedAmount`<br>`  -> NOT Department(restricted)`<br>`  -> decision + explanation`<br><br>每条规则独立测试，再通过 `AND / OR / NOT` 组成政策。 |

**变化点：** 业务判断从一个黑盒函数变成可命名、可组合的规则 Skill。

## 4. 市面上的 Skill 案例

| 上游 Case Skill | 本地 Mock Skill |
| --- | --- |
| 本 release 没有纳入可验证的公开 Specification Skill。<br>`not observable` | [`expense-approval-policy`](sample/SKILL.md)<br>具名规则通过 `AND / OR / NOT` 组合，并返回解释。<br>`constructive` |

**Case Skill:** 本记录没有纳入公开的上游 Skill 案例，状态是 `not observable`。这个空位需要保留，避免把普通的规则代码强行包装成 Skillware 生态证据。

## 5. 这个例子对应哪些角色

| Specification 角色 | Skillware 中的对应物 |
| --- | --- |
| Candidate | 有边界的费用对象 |
| Specification | 每个具名规则 Skill |
| Composite Specification | `AND`、`OR`、`NOT` 组合节点 |

## 6. 什么时候用

适合：规则需要复用；规则需要组合；规则需要独立测试或解释；输入可以被定义为有边界的 Candidate。

不适合：只有一个简单判断；操作本身会改变外部状态；规则无法形成稳定的决策契约。

## 7. 运行

```bash
python3 sample/scripts/run_demo.py
python3 -m unittest discover -s sample/tests -v
```

继续阅读：[完整样例](sample/)、[角色映射](participant-map.yaml)、[模式定义](definition.md)、[反例](misuse/explanation.md)。

## 8. 边界

本地样例证明了具名规则、组合和解释可以被构造。没有外部 Specification 案例，因此生态对应关系保持 `not observable`。
