# 组合模式（Composite）

**经典来源。** Composite 是 Gamma、Helm、Johnson 与 Vlissides 在 1994 年
*Design Patterns: Elements of Reusable Object-Oriented Software* 中归纳的
Gang of Four 结构型模式。本记录只讨论该既有模式向 Skillware 的迁移，不主张
Skillware 发明了新模式，也不主张历史优先权。

## 意图（Intent）

把组件组合成部分-整体树，使 Client 能够通过同一个 Component 契约统一处理
单个对象与对象组合。

## 作用力（Forces）

- 一个任务同时包含原子单元和结构化分组，但 Client 不应根据接收对象的种类
  编写不同分支。
- Leaf 需要保持可独立检查，父级组合也需要保留有意义的共同身份。
- 公共契约必须同时适用于两类角色，不能不断加入只对其中一类有意义的操作。
- 明确的包含顺序和循环规则使部分-整体关系可预测，但会增加校验与遍历成本。
- 文件和目录组织可以承载这种关系，却不能在缺少统一行为和显式组合时证明它。

## 参与者（Participants）

- **Client：**调用根投资备忘录的任务调用者，也可以通过相同结果契约调用可独立
  寻址的分析 Leaf。
- **Component：**公共节点调用与 `memo-section-v1` 记录；后者严格包含 `id`、
  `title`、`content`、`evidence` 和 `children`。演示模式用
  `build_component(workflow, node_id, leaf_executors=None)` 模拟调用。
- **Leaf：**市场、财务、竞争和风险分析 Skill。每个都返回一条 Component 记录，
  且 `children: []`。
- **Composite：**根投资备忘录 Skill 与声明子节点引用的序列化工作流。它返回
  相同的 Component 字段，并在 `children` 中包含完整的子 Component 记录。
- **Agent Host 与 Agent Runtime：**它们是执行上下文，不是 GoF Composite
  参与者。实际部署中的 Host 可以激活 Skill，Runtime 可以解释行为源，但本构造
  样例无法观察这些关系。

## 协作（Collaboration）

Client 通过 Component 契约调用根节点或任一 Leaf。在 Agent 模式中，根节点以
声明输入调用每个关联的子 Skill；在演示模式中，构建器调用以该子 Skill 路径为键
的显式确定性执行器。每个 Leaf 计算并返回子列表为空的公共五字段记录，Composite
校验并组装这些记录。完整注册表校验先于调用执行，强制满足引用存在、节点唯一、
单一父节点、从根可达和全局无环。

## 后果（Consequences）

客户端可以使用同一个递归数据形状处理原子章节和完整备忘录。Leaf 保持可独立
检查，新增嵌套分组不改变 Client 契约，声明顺序也保持可观察。代价包括递归校验
成本、Component 契约过宽的风险、只适用于 Composite 的操作所带来的歧义，以及
必须明确所有权、身份、循环和错误策略。

## Skillware 映射（Skillware Mapping）

自然语言行为源定义原子工作和分组工作，序列化工作流则提供节点身份、Leaf 输入、
关联 Skill 路径和包含引用。确定性执行器与构建器是协作和遍历规则的可执行判定
基准，但不解释 `SKILL.md`。模式关系跨越根 Skill、子 Skill、契约引用和工作流，
而不是由某一种文件类型决定。

### 最终本体（Final ontology）

最终本体保留经典 GoF 的四个角色，不增加平台角色：**Client**、**Component**、
**Leaf** 与 **Composite**。`Agent Host` 和 `Agent Runtime` 仍是本体之外的上下文
角色。目录不是第五个参与者，文件夹包含关系本身也不是 Composite。统一的
Component 处理方式与有效的部分-整体关系共同构成定义性结构。

## 适用性（Applicability）

当 Skillware 任务包含原子 Skill 和嵌套工作流 Skill、二者应通过同一个稳定契约
调用或消费、分组结果有真实身份，并且显式子引用可以形成经过校验的部分-整体树时，
适合使用 Composite。它适用于报告、计划、评审包及其他章节也能独立存在的递归
产物。

## 不适用性（Non-Applicability）

有意返回不同形状的扁平阶段序列、任意依赖图或仅归类相关 Skill 的目录，都不应
使用 Composite。不要为了表面一致而把只属于 Leaf 的操作强行加入 Component。
主要矛盾是简化子系统访问时使用 Facade；处理逐级转换的数据流时使用 Pipes and
Filters；集中协调同级对象时使用 Mediator。

## 正向证据（Positive Evidence）

本仓库样例属于**构造性（constructive）**证据。根备忘录和四个 Leaf 返回完全
相同的键与类型。四个显式执行器根据序列化输入计算 Leaf 记录，依赖注入测试证明
它们按声明顺序各调用一次。完整注册表测试拒绝缺失引用、重复子节点、共享子节点
DAG、根的父节点、不可达节点、断开循环、重复 ID、畸形 schema 和错误结果。

## 反向证据（Counter-Evidence）

确定性函数不能证明 Agent Runtime 会在不同 Host 中以相同方式解释自然语言
Skill。默认样例只有一层 Composite，尽管聚焦测试额外覆盖了嵌套 Composite。
执行器只模拟子节点协作和可预测的夹具分析；Python 不调用或解释子 Skill 指令，
样例也不模拟概率性分析质量。

## 误判（False Positives）

当市场、财务、竞争和风险 Skill 返回不同形状，而父级只列出路径时，它们所在的
目录不是 Composite。如果工作流中的边表示依赖而不是部分-整体包含、一个子节点
拥有多个父节点，或 Leaf 与分组暴露不同契约，该工作流同样不是 Composite。
[`misuse/SKILL.md`](misuse/SKILL.md) 有意展示了这种近似但不成立的案例。

## 开源对应（Open-Source Correspondence）

OpenMontage 的评估固定在提交
`db91727598d08d40919d7d68a47864a5467bd448`，精确公共路径包括
`pipeline_defs/animation.yaml`、
`skills/pipelines/animation/executive-producer.md`、
`skills/pipelines/animation/research-director.md` 与 `lib/pipeline_loader.py`。
该清单-编排器-阶段关系只是**候选对应（candidate correspondence）**，不是已确认
对应。各阶段产物使用不同 schema，并可能构成管道依赖图，而不是统一部分-整体树。
`.agents/skills/create-video/SKILL.md` 是供应商/API 指南，不是正向阶段证据。固定
链接与证据边界见 [`correspondence.md`](correspondence.md)。

## 验证（Verification）

在 `sample/` 中运行 `python3 scripts/run_demo.py` 和 `python3 -m unittest
discover tests -v`。验证覆盖精确组装结果、四个 Leaf 的声明顺序、递归记录中相同的
键与类型、Leaf 空子列表、执行器按顺序各调用一次、完整树不变量、严格结果校验、
输入不变性、精确 CLI 错误、固定证据路径，以及不使用网络和共享导入。

## 局限（Limitations）

一个构造性场景和一个候选生态对应不能证明使用频率、比较收益、生产健壮性或跨
Host 等价性。样例只验证结构组合，不验证夹具内容的真实性或投资质量。该映射保留
经典 GoF 意图与角色，不声称 Skillware 发明了 Composite，也不声称 Skill 目录会
自动实现该模式。
