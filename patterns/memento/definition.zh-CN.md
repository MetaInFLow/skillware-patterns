# 备忘录模式（Memento）

**经典来源。** Memento 是 Gamma、Helm、Johnson 和 Vlissides 在
1994 年《Design Patterns: Elements of Reusable Object-Oriented
Software》中描述的 GoF 行为模式。本记录只进行迁移，不声称发明或
历史优先权。

## 意图（Intent）

在不破坏封装的前提下捕获并外部化对象内部状态，使对象日后可恢复到该
状态。

## 作用力（Forces）

- 配置迁移在写入或写后校验失败时必须可恢复，而且保留原始字节布局，不只是
  JSON 语义。
- Caretaker 决定何时捕获、恢复或丢弃检查点，但不应查看或编辑
  Originator 的状态。
- 检查点必须绑定唯一目标和生命周期，防止过期或外来 Memento 覆盖其他配置。
- 原子替换、权限模式、校验和、确定性序列化和大小边界共同使回滚可审计。
- 若恢复本身失败，系统必须同时暴露迁移错误与恢复错误，不得伪称回滚成功。
- 完整快照会增加内存消耗，而且本身不提供并发控制、授权、加密或持久历史。

## 参与者（Participants）

- **Originator：**配置 Originator 子 Skill 和 `ConfigurationOriginator`；它封装已
  校验配置，创建 Memento，执行迁移与写后校验，并解读自己的不透明检查点。
- **Memento：**`configuration-memento-v1` 和 `ConfigurationMemento`；它保存原始
  字节、目标、权限、完整性、归属与生命周期元数据，但不向 Caretaker 公开。
- **Caretaker：**根 Configuration Migration Skill、子 Caretaker 合同和
  `MigrationCaretaker`；负责捕获、失败恢复、成功后丢弃和单活跃检查点策略。
- **Agent Host 与 Agent Runtime：**它们是执行上下文，不是 GoF Memento 参与者；
  本构造性样例不可观测其激活或解读行为。

## 协作（Collaboration）

Caretaker 在任何修改前请求 Originator 创建一个 Memento。Originator 校验常规文件、
非符号链接、UTF-8、JSON 结构与边界，然后保存精确字节和元数据。它先完成
无写入的准备与冲突校验。Originator 把不可变准备载荷私有保存，并与目标、所有者能力、活跃
Memento、令牌标识和完整性封印绑定；Caretaker 只能看到不透明、一次性的 `PreparedMigration` 令牌。
如果目标已被外部更改，Caretaker 先校验 Memento 校验和，再丢弃检查点与未用令牌，保留新内容且不恢复。
只有开始写入尝试后的错误才触发恢复。写入前 Originator 重新校验全部绑定，并在 I/O 前消耗令牌。
写入使用同目录临时文件：先在打开的
文件描述符上设置权限，再同步文件、原子替换为 `n + 1` 版本，最后同步目录并重读校验。
成功时 Caretaker 校验检查点的校验和、所有者、活跃状态与对象标识后使其过期，不恢复。
若写入尝试或写后校验失败，它通过
Originator 原子恢复。恢复失败时，检查点保持活跃，以便可信操作者重试，同时报告迁移与恢复两个错误。

## 后果（Consequences）

收益是恢复责任明确、字节精确回滚、受控生命周期、稳定错误和确定性输出。代价是
完整内存副本、失败时二次写入、文件系统差异、单写者前提，以及检查点格式与
Originator 实现的耦合。

## Skillware 映射（Skillware Mapping）

Behavioral Source 定义根 Caretaker 和子 Originator Skill Artifact。这些 Artifact、引用
合同、夹具和确定性 oracle 构成同一 Skillware Unit。Memento 是该源所定义的运行时
状态对象，不是新的 Skillware 本体类别。确定性 oracle 不解释自然语言 Skill，也不能证明模型中介执行。

### 最终本体（Final ontology）

源模式角色严格只有 **Originator**、**Memento** 和 **Caretaker**。Behavioral Source
持久化在 Skill Artifact 中，由 Skillware Unit 承载。Agent Host 激活该单元，Agent Runtime
在上下文中解读已激活的 Behavioral Source，但两者都不成为 GoF 参与者。Execution
Trace 记录情境化执行，Task Outcome 是被评估的效果；本静态样例不伪造两者。

## 适用性（Applicability）

当状态拥有者需要日后精确恢复，而另一组件必须在不查看内部状态的情况下控制检查点
时机与生命周期时，使用 Memento。配置迁移、事务编辑、分阶段升级和有界撤销历史是常见场景。

## 不适用性（Non-Applicability）

如果只需语义重建、根本没有恢复操作，或数据库事务已完整承担回滚合同，不要套用 Memento。
只有备份、Git 提交或复制文件，而 Caretaker 没有面向 Originator 的运行恢复路径，也不成立。

## 正向证据（Positive Evidence）

本仓库样例是**构造性**证据。它实现三个角色、字面 API `migrate(path, fail=True)`、原始
字节与权限捕获、校验和与目标绑定、原子迁移与恢复、写后校验、成功丢弃、过期与
跨目标拒绝、严格有界 JSON 输入、稳定 CLI 错误和确定性输出。

## 反向证据（Counter-Evidence）

Python oracle 不能证明 Agent Runtime 解读、Agent Host 激活、所有文件系统的崩溃持久性、
多进程隔离或对恶意进程内代码的安全性。恢复失败可能保留完整的新版文件；错误会明确说明
未恢复。权限测试不覆盖 ACL、扩展属性或平台标签。

## 误判（False Positives）

只记录旧值与新值，却无法恢复原始字节的工作流不是 Memento。只有备份目录，但采用代码没有
自主恢复操作，也不是。[`misuse/SKILL.md`](misuse/SKILL.md) 在覆盖文件后才记日志，不能重建
原始空白、键顺序、编码字节或权限。

## 开源对应（Open-Source Correspondence）

Microsoft SkillOpt 在提交 `b860a5cf88ce75e2bd02ca981ac21fb28cffba83` 上是**候选对应**。
精确路径 `skillopt_sleep/staging.py` 在采用前备份活动文件，但未暴露自主恢复路径、精确
检查点合同、生命周期或恢复校验，所以完整 Memento 未验证。见
[`correspondence.md`](correspondence.md) 与[冻结证据](evidence/skillopt-frozen-case.md)。

## 验证（Verification）

在 `sample/` 内运行 `python3 scripts/run_demo.py` 和 `python3 -m unittest discover tests -v`。
测试覆盖字面回滚 API、成功迁移不恢复、字节和权限恢复、写前冲突保留、写入与写后校验失败、
部分原子替换错误的保守恢复、恢复失败报告与重试、过期/外来/跨目标检查点、校验和损坏、
不透明一次性准备令牌、私有不可变载荷、元组式/伪造/篡改/重用令牌拒绝、
损坏检查点的提交与丢弃拒绝、
缺失/损坏/非 UTF-8 输入、重复字段、严格类型、
非有限数、孤立代理项、符号链接、版本与大小上限、确定性夹具和稳定 CLI 错误。仓库根测试
会自动复制并运行本实体化记录。

## 局限（Limitations）

样例假设单一协作式写入者和可信进程内代码。私有属性、归属令牌和校验和是合同边界，不是
安全边界；反射、monkeypatch、任意内存访问或直接文件修改都可绕过它们。原子替换并不保证每种文件系统都具有相同的崩溃持久性。生产使用需要显式
锁、授权、敏感状态保护、备份保留、容量策略、平台元数据政策、可观测性和恢复演练。
