# 装饰模式（Decorator）

> **人话：** 在不改动原有 Skill 的情况下，按需给它套上额外能力。

## 1. 先看场景

合同审查有一个基础审查，还可能需要隐私、引用和合规检查。不同客户需要不同组合，基础审查的结果格式仍要保持一致。

## 2. 先看完整 Skill

**Mock Skill：** 我们构造的 Skill 叫 `contract-review-enhancers`：

```text
patterns/decorator/sample/
├── SKILL.md                                  # 组合入口
├── child-skills/
│   ├── base-contract-review/SKILL.md          # Component
│   ├── privacy-check/SKILL.md                 # Decorator 1
│   ├── citation-check/SKILL.md                # Decorator 2
│   └── compliance-check/SKILL.md              # Decorator 3
├── references/contract-review-component.md
├── scripts/run_demo.py
└── tests/test_demo.py
```

关键行为：

```markdown
<!-- 每个 wrapper 都接收并返回同一个 contract-review-v1。 -->
base = Base Contract Review
for decorator in requested order:
    base = decorator.wrap(base)
invoke the final Component once
return the same `summary` and `findings` fields
```

## 3. 这个模式解决了什么

| 没有 Decorator | 使用 Decorator |
| --- | --- |
| `base review:`<br>`  if privacy: check privacy`<br>`  if citation: check citation`<br>`  if compliance: check compliance`<br><br>基础 Skill 持续膨胀，组合数量随之增加。 | `base review`<br>`  -> privacy wrapper`<br>`  -> citation wrapper`<br>`  -> same result contract`<br><br>每个 wrapper 增加自己的行为并传递 Component 契约。 |

**变化点：** 可选能力通过包装叠加，基础 Skill 保持稳定。

## 4. 市面上的 Skill 案例

| 上游 Case Skill | 本地 Mock Skill |
| --- | --- |
| [Caveman Skill + activation hook](https://github.com/JuliusBrussee/caveman/blob/25d22f864ad68cc447a4cb93aefde918aa4aec9f/skills/caveman/SKILL.md)<br>激活时在已有交互表面外增加行为。<br>`candidate correspondence` | [`contract-review-enhancers`](sample/SKILL.md)<br>按需叠加 privacy、citation、compliance wrapper。<br>`constructive` |

**Case Skill：** [Caveman Skill](https://github.com/JuliusBrussee/caveman/blob/25d22f864ad68cc447a4cb93aefde918aa4aec9f/skills/caveman/SKILL.md) 和它的 [activation hook](https://github.com/JuliusBrussee/caveman/blob/25d22f864ad68cc447a4cb93aefde918aa4aec9f/src/hooks/caveman-activate.js)。

它体现 Decorator 思想的地方：Host 激活时，hook 在已有 Skill 交互表面外增加行为。

```text
Host activation -> caveman wrapper -> existing Skill interaction
```

公开路径支持“激活时包装”的候选对应关系，完整 Component/Decorator 契约仍未在该版本中声明。

## 5. 这个例子对应哪些角色

| Decorator 角色 | Skillware 中的对应物 |
| --- | --- |
| Component | `contract-review-v1` |
| ConcreteComponent | `base-contract-review` |
| Decorator | privacy、citation、compliance wrapper |
| Client | 合同审查调用者 |

## 6. 什么时候用

适合：额外能力是可选的；能力可以按顺序组合；每层都能保留原有输入/输出契约。

不适合：所有请求永远需要完全相同的能力；wrapper 会改变调用者必须理解的契约；新增能力其实是一条独立工作流。

## 7. 运行

```bash
python3 sample/scripts/run_demo.py --decorators privacy-check,citation-check
python3 -m unittest discover -s sample/tests -v
```

继续阅读：[完整样例](sample/)、[角色映射](participant-map.yaml)、[模式定义](definition.md)、[反例](misuse/explanation.md)。

## 8. 边界

本地样例验证了 wrapper 顺序、一次基础调用和契约保持。Caveman 只支持候选级对应关系，不代表完整的 Component/Decorator 可替换性。
