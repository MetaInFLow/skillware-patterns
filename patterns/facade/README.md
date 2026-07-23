# 外观模式（Facade）

> **人话：** 调用者只需要调用一个入口 Skill，入口 Skill 负责安排内部的多个专家 Skill。

## 1. 先看场景

值班工程师发现 `checkout-api` 出现 `5xx spike`。他想得到一份完整的事故响应结果，不想自己记住“先诊断、再评估影响、最后写通知”的顺序。

```json
{"service": "checkout-api", "signal": "5xx spike"}
```

## 2. 先看完整 Skill

**Mock Skill：** 我们构造的 Skill 叫 `incident-response-facade`：

```text
patterns/facade/sample/
├── SKILL.md                                  # 唯一公开入口
├── child-skills/
│   ├── diagnose/SKILL.md                      # 专家 Skill 1
│   ├── assess-impact/SKILL.md                 # 专家 Skill 2
│   └── draft-communication/SKILL.md           # 专家 Skill 3
├── scripts/run_demo.py
└── tests/test_demo.py
```

`sample/SKILL.md` 的关键部分：

```markdown
<!-- 调用者只看到一个入口，内部顺序由根 Skill 管理。 -->
For a `5xx spike`:
1. diagnose the service signal
2. assess customer impact
3. draft the status communication
4. return `summary`, `impact`, `actions`, and `communication`
```

调用者只发起一次请求，得到一个固定结构的结果。

## 3. 这个模式解决了什么

### 没有 Facade

```text
caller -> diagnose
caller -> assess-impact
caller -> draft-communication
```

每个调用者都要知道内部顺序、如何传递中间结果、失败时返回什么。

### 使用 Facade

```text
caller -> incident-response-facade
           -> diagnose -> assess-impact -> draft-communication
           -> one stable incident result
```

入口 Skill 把内部协作藏起来，同时维护一个稳定的输入和输出契约。

## 4. 市面上的 Skill 案例

**Case Skill：** [Superpowers `using-superpowers`](https://github.com/obra/superpowers/blob/896224c4b1879920ab573417e68fd51d2ccc9072/skills/using-superpowers/SKILL.md)，由固定版本的 [session-start hook](https://github.com/obra/superpowers/tree/896224c4b1879920ab573417e68fd51d2ccc9072/hooks/session-start) 激活。

它体现 Facade 的地方：

```text
session start
  -> using-superpowers
  -> discover specialist Skills
  -> select and invoke the needed Skills
```

调用者面对的是 `using-superpowers` 这一个入口策略，专家 Skill 的发现和调用由入口负责。仓库把这个对应关系记录为 `confirmed correspondence`，完整证据见 [`correspondence.md`](correspondence.md)。

## 5. 这个例子对应哪些角色

| Facade 角色 | Skillware 中的对应物 |
| --- | --- |
| Client | 值班工程师或任务调用者 |
| Facade | `sample/SKILL.md` |
| Subsystem | `diagnose`、`assess-impact`、`draft-communication` |

判断一个 Skill 是否使用 Facade，关键看入口是否真正隐藏了子 Skill 的协作；目录中有多个文件并不能证明 Facade。

## 6. 什么时候用

适合：多个调用者重复同一组 Skill 的调用顺序；需要一个稳定的公开请求/结果；内部专家 Skill 需要独立替换。

不适合：只有一个操作和一个子 Skill；调用者确实需要分别控制每个子 Skill；内部顺序本身就是调用者的业务决策。

## 7. 运行

```bash
python3 sample/scripts/run_demo.py
python3 -m unittest discover -s sample/tests -v
```

继续阅读：[完整样例](sample/)、[角色映射](participant-map.yaml)、[模式定义](definition.md)、[反例](misuse/explanation.md)。

## 8. 边界

本地样例证明了这种 Skill 结构可以被构造和验证。Superpowers 提供固定版本的生态对应证据。两者都不能推出跨 Host 行为等价或质量提升。
