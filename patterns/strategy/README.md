# 策略模式（Strategy）

> **人话：** 请求格式不变，根据条件选择一套具体做法。

## 1. 先看场景

普通改动适合快速审查，涉及安全或四个以上文件的改动需要深度审查。调用者只想提交一份 review request，并得到一种 review result。

## 2. 先看完整 Skill

**Mock Skill：** 我们构造的 Skill 叫 `risk-aware-code-review`：

```text
patterns/strategy/sample/
├── SKILL.md                                  # Context and selector
├── child-skills/
│   ├── fast-scan/SKILL.md                    # Strategy A
│   └── deep-review/SKILL.md                  # Strategy B
├── references/review-strategy-contract.md
├── scripts/run_demo.py
└── tests/test_demo.py
```

关键行为：

```markdown
<!-- 选择规则会变化，公开的 review.v1 结果契约保持不变。 -->
if `security_sensitive` or changed files >= 4:
    select `deep-review`
else:
    select `fast-scan`
Validate the same `review.v1` result after either Skill.
```

## 3. 这个模式解决了什么

| 没有 Strategy | 使用 Strategy |
| --- | --- |
| `review Skill:`<br>`  if risky: run all deep-review rules`<br>`  else: run all fast-scan rules`<br><br>选择条件和审查算法纠缠在一个大 Skill。 | `review request`<br>`  -> selector`<br>`  -> fast-scan OR deep-review`<br>`  -> review.v1`<br><br>Context 负责选择，Strategy Skill 负责执行。 |

**变化点：** 选择规则可以变化，候选执行方案仍共享同一个结果契约。

## 4. 市面上的 Skill 案例

| 上游 Case Skill | 本地 Mock Skill |
| --- | --- |
| [UI/UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/8a81ed60272d21d4b8808f7308d49a0b1b000555/.claude/skills/ui-ux-pro-max/SKILL.md)<br>router 按 domain/stack 选择 procedure。<br>`candidate correspondence` | [`risk-aware-code-review`](sample/SKILL.md)<br>按风险选择 `fast-scan` 或 `deep-review`，共享 `review.v1`。<br>`constructive` |

**Case Skill：** [UI/UX Pro Max Skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/8a81ed60272d21d4b8808f7308d49a0b1b000555/.claude/skills/ui-ux-pro-max/SKILL.md) 和它的 [router](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/8a81ed60272d21d4b8808f7308d49a0b1b000555/scripts/search.py)。

它体现 Strategy 思想的地方：router 根据请求的 domain、stack 或 design system 选择具体 procedure。

```text
request -> router -> selected procedure
```

公开文件支持路由关系，所有候选 procedure 是否完全可替换仍记录为 `candidate correspondence`。

## 5. 这个例子对应哪些角色

| Strategy 角色 | Skillware 中的对应物 |
| --- | --- |
| Context | 根 code-review Skill |
| Strategy | `review.v1` 过程契约 |
| ConcreteStrategy | `fast-scan` 和 `deep-review` |

## 6. 什么时候用

适合：有多套可互换的执行方式；选择条件需要和执行逻辑分开；所有候选方案可以共享输入/输出契约。

不适合：只有一套做法；每个候选方案返回完全不同的结果；分支只有一两行且不会继续增长。

## 7. 运行

```bash
python3 sample/scripts/run_demo.py
python3 -m unittest discover -s sample/tests -v
```

继续阅读：[完整样例](sample/)、[角色映射](participant-map.yaml)、[模式定义](definition.md)、[反例](misuse/explanation.md)。

## 8. 边界

本地样例验证了选择逻辑和共享结果契约。UI/UX Pro Max 只支持候选级对应关系，不代表其所有 procedure 都满足完整替换契约。
