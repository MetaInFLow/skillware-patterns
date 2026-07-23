# 管道-过滤器模式（Pipes and Filters）

> **人话：** 一个有版本的记录，依次经过多个各自负责一件事的 Filter。

## 1. 先看场景

客服工单要依次经过标准化、脱敏、分类、优先级判断和回复草稿。一个大 Skill 很难替换其中一步，也没有明确的中间数据边界。

## 2. 先看完整 Skill

**Mock Skill：** 我们构造的 Skill 叫 `support-ticket-triage`：

```text
patterns/pipes-and-filters/sample/
├── SKILL.md                                  # runner and pipeline contract
├── references/support-ticket-record-contract.md
├── scripts/run_demo.py
├── fixtures/valid/urgent-access.json
└── tests/test_demo.py
```

关键行为：

```markdown
<!-- runner 管顺序；每个 Filter 只负责一个转换。 -->
normalize -> redact -> classify -> prioritize -> draft
Validate and deep-copy `support-ticket.v1` before and after every Filter.
Stop at the first invalid result and identify its stage.
```

## 3. 这个模式解决了什么

### 没有 Pipes and Filters

```text
caller -> one large triage Skill
```

所有步骤共享内部状态，替换、测试和失败定位都很困难。

### 使用 Pipes and Filters

```text
ticket -> normalize -> redact -> classify -> prioritize -> draft -> final record
```

每一步接收和返回同一个 `support-ticket.v1`，Pipe 负责边界校验和数据交接。

## 4. 市面上的 Skill 案例

**Case Skill：** [OpenMontage animated-explainer pipeline](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/pipeline_defs/animated-explainer.yaml) 和 [pipeline loader](https://github.com/calesthio/OpenMontage/blob/db91727598d08d40919d7d68a47864a5467bd448/lib/pipeline_loader.py)。

它体现 Pipes and Filters 思想的地方：manifest 声明有序 stage Skill，loader 按顺序传递产物。

```text
manifest -> stage Skill 1 -> stage Skill 2 -> stage Skill 3 -> artifact
```

公开文件显示了阶段顺序和产物流，完整共享 Pipe 契约仍记录为 `candidate correspondence`。

## 5. 这个例子对应哪些角色

| Pipes and Filters 角色 | Skillware 中的对应物 |
| --- | --- |
| Data Source | 工单输入和记录创建 |
| Filter | 五个转换 Skill |
| Pipe | `support-ticket.v1` 校验和复制边界 |
| Data Sink | 最终记录和执行 trace |

## 6. 什么时候用

适合：步骤顺序稳定；各步骤需要独立替换；所有步骤可以共享一个明确的数据契约。

不适合：步骤之间需要循环协商；事务必须横跨全部步骤；没有可行的共同数据格式。

## 7. 运行

```bash
python3 sample/scripts/run_demo.py
python3 -m unittest discover -s sample/tests -v
```

继续阅读：[完整样例](sample/)、[角色映射](participant-map.yaml)、[模式定义](definition.md)、[反例](misuse/explanation.md)。

## 8. 边界

本地样例验证了五个可替换 Filter、显式边界和 fail-stop 行为。OpenMontage 只支持候选级对应关系，本地 oracle 不代表分布式 backpressure、并发或运行时等价。
