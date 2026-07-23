# 适配器模式（Adapter）

> **人话：** Skill 的任务含义保持不变，只在边界处翻译成目标 Host 或服务商需要的格式。

## 1. 先看场景

同一个问题需要发布到 GitHub、Jira 或 Linear。三家的请求格式不同，但问题的身份、标题和严重程度必须保持一致。

```json
{
  "target": "github",
  "issue": {"id": "INC-42", "title": "Checkout failures", "severity": "high"}
}
```

## 2. 先看完整 Skill

**Mock Skill：** 我们构造的 Skill 叫 `multi-tracker-issue-publisher`：

```text
patterns/adapter/sample/
├── SKILL.md                              # canonical issue 入口
├── child-skills/
│   ├── github/SKILL.md                   # GitHub Adapter
│   ├── jira/SKILL.md                     # Jira Adapter
│   └── linear/SKILL.md                   # Linear Adapter
├── references/tracker-contracts.md
├── scripts/run_demo.py
└── tests/test_demo.py
```

`sample/SKILL.md` 的关键部分：

```markdown
<!-- 只改变目标格式，不改变 issue 的身份和 severity 含义。 -->
1. validate one canonical issue
2. select `github`, `jira`, or `linear`
3. build that target's request descriptor
4. return the descriptor without a network call
```

输入是一份 canonical issue，输出是对应平台的离线请求描述。

## 3. 这个模式解决了什么

### 没有 Adapter

```text
GitHub Skill: 自己定义 issue 语义
Jira Skill:   再定义一套 issue 语义
Linear Skill: 继续复制一套 issue 语义
```

多个实现逐渐产生语义漂移。

### 使用 Adapter

```text
canonical issue
  -> GitHub Adapter -> GitHub REST descriptor
  -> Jira Adapter   -> Jira REST + ADF descriptor
  -> Linear Adapter -> Linear GraphQL descriptor
```

规范 Skill 只维护一份，平台差异集中在边界绑定中。

## 4. 市面上的 Skill 案例

**Case Skill：** [gstack `SKILL.md.tmpl`](https://github.com/garrytan/gstack/blob/11de390be1be6849eb9a15f91ff4922dd16c589a/SKILL.md.tmpl)、[生成器](https://github.com/garrytan/gstack/blob/11de390be1be6849eb9a15f91ff4922dd16c589a/scripts/gen-skill-docs.ts) 和 [Host bindings](https://github.com/garrytan/gstack/tree/11de390be1be6849eb9a15f91ff4922dd16c589a/hosts)。

它体现 Adapter 的地方：同一个 Skill 模板被翻译成 Claude、Codex 等 Host 需要的入口和 frontmatter。核心对应关系是：

```text
canonical Skill template -> Claude binding
                          -> Codex binding
```

仓库把这个对应关系记录为 `confirmed correspondence`，具体路径见 [`correspondence.md`](correspondence.md)。

## 5. 这个例子对应哪些角色

| Adapter 角色 | Skillware 中的对应物 |
| --- | --- |
| Client | 任务调用者 |
| Target | canonical issue-publisher 契约 |
| Adapter | GitHub、Jira、Linear binding Skill |
| Adaptee | 各平台 REST 或 GraphQL 请求契约 |

判断重点是“边界翻译”，不是“有多个平台配置”。翻译前后的任务语义需要能够对照。

## 6. 什么时候用

适合：同一个行为要接入多个不兼容的 Host 或服务商接口；平台差异可以局部翻译；新目标不应该复制整个根 Skill。

不适合：目标接口已经接受 canonical contract；翻译会改变任务本意；只有一个目标且没有兼容压力。

## 7. 运行

```bash
python3 sample/scripts/run_demo.py
python3 -m unittest discover -s sample/tests -v
```

继续阅读：[完整样例](sample/)、[角色映射](participant-map.yaml)、[模式定义](definition.md)、[反例](misuse/explanation.md)。

## 8. 边界

本地样例验证了三种请求描述的生成和 canonical 语义保留。gstack 证据支持源码层面的绑定关系，真实 Host 运行一致性仍需单独测试。
