# 中介者模式（Mediator）

> **人话：** 多个 Skill 只和一个协调 Skill 交流，彼此不直接调用。

## 1. 先看场景

一次发布需要 build、security、docs、approval 四个检查。若它们互相调用，新增一个检查就会增加很多新的依赖关系。

```text
build <-> security <-> docs <-> approval
```

## 2. 先看完整 Skill

**Mock Skill：** 我们构造的 Skill 叫 `deployment-coordinator`：

```text
patterns/mediator/sample/
├── SKILL.md                                  # Mediator
├── child-skills/
│   ├── build/SKILL.md                         # Colleague
│   ├── security/SKILL.md
│   ├── docs/SKILL.md
│   └── approval/SKILL.md
├── references/deployment-readiness-contract.md
├── scripts/run_demo.py
└── tests/test_demo.py
```

关键行为：

```markdown
<!-- Colleague 向中心报告，Colleague 之间不互相调用。 -->
1. invoke build, security, docs, and approval once
2. collect one readiness report from each Skill
3. isolate a failed report
4. release only when the all-pass policy is satisfied
```

## 3. 这个模式解决了什么

### 没有 Mediator

```text
build -> security -> docs -> approval
security -> build
docs -> security
```

每个专家都需要了解其他专家，协作关系迅速变复杂。

### 使用 Mediator

```text
build + security + docs + approval -> deployment-coordinator -> release decision
```

专家只知道中心的报告契约，协调规则集中在 Mediator Skill 中。

## 4. 市面上的 Skill 案例

**Case Skill：** [Anthropic GL reconciler coordinator](https://github.com/anthropics/financial-services/blob/4aa51ed3d379731f8f9beff498d749580372699c/managed-agent-cookbooks/gl-reconciler/agent.yaml) 和 [reader/critic/resolver subagents](https://github.com/anthropics/financial-services/tree/4aa51ed3d379731f8f9beff498d749580372699c/managed-agent-cookbooks/gl-reconciler/subagents)。

它体现 Mediator 思想的地方：中心 coordinator 分派工作并收集专家报告。

```text
coordinator -> reader / critic / resolver
reader / critic / resolver -> coordinator
```

公开文件支持集中协调的候选对应关系，共享 Colleague 契约仍需进一步确认。

## 5. 这个例子对应哪些角色

| Mediator 角色 | Skillware 中的对应物 |
| --- | --- |
| Mediator | 根 deployment coordinator Skill |
| ConcreteMediator | all-pass readiness policy |
| Colleague | build、security、docs、approval |

## 6. 什么时候用

适合：多个专家需要协调；同伴依赖正在增长；决策规则需要集中维护。

不适合：只有两个 Skill 的简单调用；协调器开始承担所有专家工作；专家之间确实需要直接协作。

## 7. 运行

```bash
python3 sample/scripts/run_demo.py
python3 -m unittest discover -s sample/tests -v
```

继续阅读：[完整样例](sample/)、[角色映射](participant-map.yaml)、[模式定义](definition.md)、[反例](misuse/explanation.md)。

## 8. 边界

本地样例验证了中心调度、失败隔离和 all-pass 决策。Anthropic cookbook 只支持候选级对应关系，不代表完整的 Colleague 接口。
