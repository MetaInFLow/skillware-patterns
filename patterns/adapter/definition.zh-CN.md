# 适配器模式（Adapter）

**经典来源。** Adapter 是 Gamma、Helm、Johnson 与 Vlissides 在 1994 年
*Design Patterns: Elements of Reusable Object-Oriented Software* 中归纳的
Gang of Four 结构型模式。本记录只讨论该既有模式向 Skillware 的迁移，不主张
Skillware 发明了新模式，也不主张历史优先权。

## 意图（Intent）

把既有组件的接口转换为 Client 所期待的 Target 接口，使原本不兼容的 Client
与组件能够协作，同时不复制或改变组件的规范语义。

## 作用力（Forces）

- 跨多个问题追踪器时，应只有一份规范问题契约作为权威来源。
- GitHub REST、Jira REST v3 与 Linear GraphQL 的操作、上下文、文档和字段约定
  不同，但问题含义必须稳定。
- 兼容逻辑应保持轻薄、显式并可独立测试。
- 遇到不支持的目标或语义缺口时，绑定必须拒绝请求，不能静默丢失身份或弱化
  严重性。
- 严重性描述影响，追踪器优先级表达排期策略；接口适配不能混淆两者。
- 每个目标契约都可能变化，因此每个 Adapter 都有维护成本。

## 参与者（Participants）

- **Client：**提交规范问题、选择追踪器并提供精确目标上下文的任务调用者。
- **Target：**记录在 `sample/references/tracker-contracts.md` 中的追踪器 REST
  或 GraphQL 请求契约。
- **Adaptee：**`sample/SKILL.md`，即规范问题发布 Skill；其 `id`、`title`、
  `description` 与 `severity` 语义保持权威。
- **Adapter：**`sample/scripts/run_demo.py` 中的 `adapt_github`、`adapt_jira`
  和 `adapt_linear` 绑定；每个绑定把规范问题和目标上下文转换为离线 Target
  请求描述符。
- **Agent Host 与 Agent Runtime：**它们是执行上下文，不是 GoF Adapter
  参与者。Host 绑定可以承载 Adapter，但 Host 本身不会自动成为 Client、
  Target、Adapter 或 Adaptee。

## 协作（Collaboration）

Client 提交精确的 `target`、`issue` 与 `target_context` 记录。Adaptee 契约校验
全部规范字段和四值严重性词表。所选 Adapter 新建请求描述符：GitHub 使用带版本
的创建问题 REST 路径、请求头、Markdown 标记和严重性标签；Jira 使用 REST v3
创建问题路径、项目与问题类型上下文、ADF 描述和来源/严重性标签；Linear 使用
带 `variables.input` 与 Markdown 元数据的 `issueCreate` mutation。每个绑定都
保留身份、标题、描述和严重性，不增加优先级策略，也不修改输入。

## 后果（Consequences）

规范 Skill 不依赖具体追踪器，Client 使用一个稳定问题模型，目标差异被限制在
各 Adapter 中。显式转换也使身份与语义等价可测试。代价包括额外间接层、需要
维护兼容矩阵，以及必须补充目标侧运行测试。转换不能凭空创造目标不存在的能力。
离线描述符无法验证凭据、租户元数据、权限、标签可用性、实时接受结果或副作用。

## Skillware 映射（Skillware Mapping）

自然语言行为源可以定义规范 Adaptee 契约，轻量声明式或可执行绑定则实现
Target 契约。模式成立依赖语义转换和委派，而不依赖文件名、类或单纯字段改名。
Agent Host 可以分发或激活绑定，Agent Runtime 可以解释绑定，但除非具体参与者
关系另有证据，这些平台角色仍只是执行上下文。

## 适用性（Applicability）

当一个具有独立意义的 Skill 必须通过多种不兼容的发现、调用、字段或结果约定
服务客户端，并且规范流程应保持不变时，适合使用 Adapter。若每个映射都能明确
说明如何保留身份、必需值与领域含义，尤其适用。

## 不适用性（Non-Applicability）

契约本来就兼容、目标专属策略确实需要改变领域行为，或任务只是重命名、复制
Skill 文件时，不应使用 Adapter。流程本身变化应考虑 Strategy；统一入口需要
协调子系统时应考虑 Facade；目标不存在等价语义时应建立校验边界并拒绝转换。

## 正向证据（Positive Evidence）

本仓库样例属于**构造性（constructive）**证据：三个轻量绑定从同一规范问题
构建带版本的 GitHub REST、Jira REST v3 与 Linear GraphQL 离线请求描述符。
聚焦测试覆盖精确描述符、十二种严重性/目标组合、身份保留、目标上下文使用、输入
不变性、严格 schema 错误、本地路径、独立导入和 CLI 执行。与此分开，冻结的
gstack 案例为生成式和系统专属 Host 表面提供**已确认对应（confirmed
correspondence）**证据。

**论文表述（非状态）：** Strong correspondence. Parity requires runtime tests.

## 反向证据（Counter-Evidence）

确定性判定程序没有调用真实追踪器或 Agent Host。符合文档形状的请求仍可能因
认证、权限、租户配置、字段或标签不可用、API 演进或目标 ID 无效而失败。gstack
源码观察只证明一个固定修订中的生成与 Host 专属改写，不能证明所有声明 Host
的运行行为等价。

## 误判（False Positives）

如果一个 Skill 副本只把 `title` 改名为 `summary`，同时丢弃规范 `id` 和严重性
含义，它就不是 Adapter。该副本既不保留身份，也没有实现与 Adaptee 的语义等价。
[`misuse/SKILL.md`](misuse/SKILL.md) 有意展示了这一近似但不成立的案例。

## 开源对应（Open-Source Correspondence）

gstack 的评估固定在提交 `11de390be1be6849eb9a15f91ff4922dd16c589a`。
其 `SKILL.md.tmpl` 是规范 Adaptee 模板。生成器与系统专属 Host 配置把该源转换
为目标发现方式、frontmatter、路径和工具名约定；生成的 `SKILL.md` 是输出表面，
不是规范源。每个生成绑定是 Adapter，Host 专属 Skill 契约是 Target，任务级调用
是 Client。固定链接与运行等价限制见 [`correspondence.md`](correspondence.md)。
该 confirmed correspondence 与本地构造样例相互独立。

## 验证（Verification）

在 `sample/` 中运行 `python3 scripts/run_demo.py` 和
`python3 -m unittest discover tests -v`。验证覆盖三个追踪器的精确描述符、四种
严重性下的身份与含义保留、目标上下文使用、输入不变性、精确 schema 与 CLI
错误、参与者与证据路径解析，以及不使用网络和其他模式目录。

## 局限（Limitations）

一个构造性场景和一个已确认生态对应不能证明模式使用频率、比较质量或跨 Host 运行
等价。演示用确定性 Python 作为行为契约的可执行判定基准，不模拟概率性 Agent
Runtime 解释，也不调用追踪器 API。输出只是离线工件，不主张实时接受或副作用。
该映射保留既有 GoF 作用力与参与者，但不声称 Skillware 发明了 Adapter。
