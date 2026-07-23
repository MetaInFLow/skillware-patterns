# 组合模式（Composite）

> **人话：** 单个 Skill 和由多个 Skill 组成的整体，使用同一种结果格式。

## 1. 先看场景

投资备忘录需要市场、财务、竞品和风险四个部分。调用者希望把“一个章节”和“整份备忘录”用同样的方式读取、校验和继续组合。

## 2. 先看完整 Skill

**Mock Skill：** 我们构造的 Skill 叫 `investment-memo-builder`：

```text
patterns/composite/sample/
├── SKILL.md                                  # Composite root
├── child-skills/
│   ├── market-analysis/SKILL.md              # Leaf
│   ├── financial-analysis/SKILL.md           # Leaf
│   ├── competition-analysis/SKILL.md         # Leaf
│   └── risk-analysis/SKILL.md                # Leaf
├── references/section-contract.md
├── scripts/run_demo.py
└── tests/test_demo.py
```

所有节点都返回 `memo-section-v1`：

```markdown
<!-- Leaf 和 Root 使用同一份递归结果契约。 -->
Leaf -> {id, title, content, evidence, children: []}
Root -> {id, title, content, evidence, children: [validated leaves]}
```

## 3. 这个模式解决了什么

### 没有 Composite

```text
root -> market()  -> market-specific result
root -> finance() -> finance-specific result
root -> risk()   -> risk-specific result
```

根 Skill 必须知道每种结果的特殊格式，嵌套组合会越来越难处理。

### 使用 Composite

```text
memo-section-v1(root)
  ├── memo-section-v1(market)
  ├── memo-section-v1(finance)
  ├── memo-section-v1(competition)
  └── memo-section-v1(risk)
```

调用者只需要理解一种节点格式。

## 4. 市面上的 Skill 案例

**Case Skill：** [OpenMontage animation pipeline](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/pipeline_defs/animation.yaml) 和由 [pipeline loader](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/lib/pipeline_loader.py) 加载的 stage Skills。

它体现组合思想的地方：一个 pipeline definition 把多个 stage Skill 组织成更大的工作流。

```text
animation pipeline -> research stage -> production stage -> output artifact
```

公开文件显示了组合关系，但没有充分证明所有 stage 共享统一的 Leaf/Composite 结果契约，因此仓库将其标为 `candidate correspondence`。

## 5. 这个例子对应哪些角色

| Composite 角色 | Skillware 中的对应物 |
| --- | --- |
| Client | 备忘录调用者 |
| Component | `memo-section-v1` |
| Leaf | 四个分析 Skill |
| Composite | 根 Skill `investment-memo-builder` |

目录里有子目录不等于 Composite。真正的判断依据是“部分和整体共享接口，并且存在经过校验的包含关系”。

## 6. 什么时候用

适合：整体和部分可以共享一个结果契约；需要递归组合；调用者不想为叶子和根节点写两套逻辑。

不适合：只是平行步骤的顺序执行；不同节点完全没有共同契约；关系是共享引用或复杂网络而非清晰的部分-整体。

## 7. 运行

```bash
python3 sample/scripts/run_demo.py
python3 -m unittest discover -s sample/tests -v
```

继续阅读：[完整样例](sample/)、[角色映射](participant-map.yaml)、[模式定义](definition.md)、[反例](misuse/explanation.md)。

## 8. 边界

本地样例验证了递归结果契约和树校验。OpenMontage 只支持候选级对应关系，不能据此推出统一的 stage 结果格式。
