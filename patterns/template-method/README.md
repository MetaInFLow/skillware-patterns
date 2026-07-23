# 模板方法模式（Template Method）

> **人话：** 根 Skill 固定工作流程，只把少数明确步骤交给领域 Skill 来填写。

## 1. 先看场景

企业 RFP 回复必须按“提取需求、分析差距、领域补充、起草、质量检查”的顺序执行。医疗和金融行业需要不同内容，流程骨架仍然相同。

## 2. 先看完整 Skill

**Mock Skill：** 我们构造的 Skill 叫 `enterprise-rfp-response`：

```text
patterns/template-method/sample/
├── SKILL.md                                  # 固定流程
├── child-skills/
│   ├── healthcare/SKILL.md                   # 领域实现 A
│   └── finance/SKILL.md                      # 领域实现 B
├── references/rfp-domain-hook-contract.md
├── scripts/run_demo.py
└── tests/test_demo.py
```

关键行为：

```markdown
<!-- 根 Skill 固定顺序，子 Skill 只能实现 apply-domain-hook。 -->
1. extract requirements
2. analyze gaps
3. apply one validated domain hook
4. draft the response
5. run the quality check
```

## 3. 这个模式解决了什么

### 没有 Template Method

```text
healthcare Skill: extract -> gaps -> hook -> draft -> quality
finance Skill:    extract -> gaps -> hook -> draft -> quality
```

两套流程很容易逐渐出现顺序和质量门槛差异。

### 使用 Template Method

```text
root workflow: extract -> gaps -> [domain hook] -> draft -> quality
```

根 Skill 管顺序，领域 Skill 只提供被允许的变化点。

## 4. 市面上的 Skill 案例

**Case Skill：** [Superpowers brainstorming](https://github.com/obra/superpowers/blob/896224c4b1879920ab573417e68fd51d2ccc9072/skills/brainstorming/SKILL.md) 和 [test-driven-development](https://github.com/obra/superpowers/blob/896224c4b1879920ab573417e68fd51d2ccc9072/skills/test-driven-development/SKILL.md)。

它体现 Template Method 思想的地方：Skill 规定了有序的工作步骤，同时在任务内容处留下变化空间。

```text
fixed workflow guidance -> task-specific content -> fixed verification steps
```

公开文件支持流程骨架的候选对应关系，完整 AbstractClass/ConcreteClass hook 契约仍需验证。

## 5. 这个例子对应哪些角色

| Template Method 角色 | Skillware 中的对应物 |
| --- | --- |
| AbstractClass | 根 RFP response Skill |
| Template Method | 五步固定工作流 |
| ConcreteClass | healthcare / finance hook Skill |
| Primitive operation | `apply-domain-hook` |

## 6. 什么时候用

适合：大部分步骤固定；只有少数步骤因领域变化；根 Skill 必须守住顺序和质量门槛。

不适合：每个变体都会改变整个流程；所有步骤都可以自由重排；根本没有需要特化的步骤。

## 7. 运行

```bash
python3 sample/scripts/run_demo.py
python3 -m unittest discover -s sample/tests -v
```

继续阅读：[完整样例](sample/)、[角色映射](participant-map.yaml)、[模式定义](definition.md)、[反例](misuse/explanation.md)。

## 8. 边界

本地样例验证了固定顺序和 hook 限制。Superpowers 只支持候选级对应关系，不代表领域内容质量或完整 Template Method 角色映射。
