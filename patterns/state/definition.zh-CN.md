# 状态模式（State）

**经典来源。** State 是 Gamma、Helm、Johnson 与 Vlissides 在 1994 年
*Design Patterns: Elements of Reusable Object-Oriented Software* 中归纳的
Gang of Four 行为型模式。本记录只迁移这一既有模式，不主张发明或历史优先权。

## 意图（Intent）

让 Context 把依赖内部 State 的请求委托给当前 State 对象，从而在内部状态变化时
改变行为。

## 作用力（Forces）

- 供应商验证、审批和激活允许不同动作并产生不同结果，但调用方需要一个稳定的
  工作流接口。
- 合法转换需要单一所有者；若调用方或 Context 到处复制条件分支，生命周期难以
  审计。
- 工作流必须跨进程重启恢复，不能从对话或活动标签猜测当前状态。
- 非法动作或后继状态写入失败时，持久状态不能前进。
- 损坏状态必须保持可见，不能被静默重置成看似合理的阶段。
- 对于简单的无环生命周期，显式状态对象也会增加制品数量和迁移责任。

## 参与者（Participants）

- **Context：**根供应商准入流程 Skill 和确定性 `VendorWorkflow`。它提供统一
  转换操作、重载持久状态、委托行为，并原子提交合法后继状态。
- **State：**所有状态实现共同遵循的 `vendor-onboarding-state-v1`
  `handle-action` 契约。
- **ConcreteState：**draft、verified、approved、activated 子 Skill 及对应
  Python 类。每个实现拥有自身允许动作、后继状态和状态特定结果。
- **Agent Host 与 Agent Runtime：**二者是执行上下文，不是 GoF State
  参与者。本构造样例无法观察其激活与解释行为。

## 协作（Collaboration）

Context 在每次动作前重载并校验版本化记录，再调用恢复出的 ConcreteState 的
`handle`。只有 draft 接受 `verify`，只有 verified 接受 `approve`，只有
approved 接受 `activate`，activated 不接受任何转换。ConcreteState 要么在写入前
拒绝动作，要么请求 Context 原子持久化其指定的后继状态。只有替换成功后，Context
才更新内存 State。新建 Context 可在重启后恢复同一持久状态。首次构造 Context 是
显式 bootstrap 边界，此时记录不存在可以创建 draft；已经初始化后再重载时若记录
消失，则视为损坏，绝不静默创建替代工作流。

## 后果（Consequences）

依赖状态的行为和合法转换被局部化，调用方保持统一接口，持久恢复也成为显式契约。
非法路径可确定性验证。代价包括每状态一个制品、状态 schema 迁移、终态策略、
持久化失败处理，以及引入多个写入者时所需的并发控制。

## Skillware 映射（Skillware Mapping）

自然语言 Behavioral Source 定义 Context 协议、公共 State 操作和四个
ConcreteState 职责。根与子 Skill Artifact 组成一致的 Skillware Unit。JSON
夹具提供状态与动作，标准库 Python 为委托和持久化提供确定性预言机，但不会激活
或解释 Skill 文件。

### 最终本体

经典角色严格保留为 **Context**、**State** 和 **ConcreteState**。`Agent Host`
激活 Skillware Unit，`Agent Runtime` 解释已激活的 Behavioral Source，但这些
上下文对象都不会成为源模式参与者。Execution Trace 记录情境化执行，Task Outcome
是经过评估的效果；本静态样例不虚构二者。

## 适用性（Applicability）

当一个长期工作流具有显式生命周期、当前状态会改变允许的动作与结果，且后续工作
必须恢复该状态时，适合使用 State。审批、开通、发布、履约和事件处置等具有不同
转换职责的生命周期都可能适用。

## 不适用性（Non-Applicability）

可互换的无状态算法应使用 Strategy。对于不改变行为的被动标签，或没有持久生命
周期的短固定管道，不应引入状态对象。若所有转换分支仍由调用方负责，单独一个数据
库状态列也不足以构成 State。

## 正向证据（Positive Evidence）

仓库样例是 **constructive** 证据。它实现全部三个 GoF 角色、四个独立
ConcreteState 处理器、三个自主管理的转换、版本化持久状态、原子替换、动作前
重载、重启恢复、缺失与损坏校验和写入前拒绝。聚焦测试还证明精确输出、确定性重跑、
输入不变、非 UTF-8 拒绝，以及写入失败时内存与磁盘一致。

## 反向证据（Counter-Evidence）

Python 预言机不能证明 Agent Runtime 会一致解释 Behavioral Source，也不能证明
兼容 Agent Host 会激活它。样例只支持本地单写入者，没有锁、比较并交换、分布式
事务、外部证据校验、授权、回滚或状态 schema 迁移实现。

## 误判（False Positives）

如果条件文本只提到阶段，却不持久化记录、不让当前阶段拥有行为，也没有重启恢复，
它就不是 State。查找表可以校验转换，但仅有查找表并不能实现参与者映射中声明的
ConcreteState 职责。[`misuse/SKILL.md`](misuse/SKILL.md) 故意展示了这种条件
文本近似案例。

## 开源对应（Open-Source Correspondence）

OpenMontage 在提交 `db91727598d08d40919d7d68a47864a5467bd448` 上构成
**candidate correspondence**。其 checkpoint 库持久化阶段与状态、从已完成
checkpoint 推导下一阶段，checkpoint 协议还针对 `in_progress` 和
`awaiting_human` 定义不同恢复行为。但固定路径没有定义独立 State、ConcreteState
参与者或 Context 到 State 的委托，因此不是 confirmed GoF 映射。详情见
[`correspondence.md`](correspondence.md) 与
[`evidence/openmontage-frozen-case.md`](evidence/openmontage-frozen-case.md)。

## 验证（Verification）

在 `sample/` 中运行 `python3 scripts/run_demo.py` 和 `python3 -m unittest
discover tests -v`。验证覆盖完整动作序列、每步后的持久重载、approved 状态重启
恢复、逐状态处理职责、非法转换不写入、原子替换失败、缺失与损坏状态、非 UTF-8、
非字符串 state、供应商身份不匹配、精确夹具输出与错误、确定性重跑，以及无需网络
的标准库独立执行。

## 局限（Limitations）

一个构造场景不能证明普遍性、比较收益、生产耐久性或跨 Host 行为等价。无环 revision
规则仅属于本场景。新增纠正、暂停、退出或重试时，必须显式设计新状态、转换、持久化
语义和测试，不能依赖对话推断。
