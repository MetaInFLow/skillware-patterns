# 观察者模式（Observer）

**经典来源。** Observer 是 Gamma、Helm、Johnson 与 Vlissides 在 1994 年
*Design Patterns: Elements of Reusable Object-Oriented Software* 中归纳的
Gang of Four 行为型模式。本记录只讨论该既有模式向 Skillware 的迁移，不主张
Skillware 发明了新模式，也不主张历史优先权。

## 意图（Intent）

定义一对多依赖，使一个 Subject 状态改变时，所有已注册 Observer 都通过公共
操作收到通知并进行更新。

## 作用力（Forces）

- 发布完成会引发多个独立反应，但发布工作流不应分支处理审计、变更日志或通知
  的内部逻辑。
- 消费者需要独立的生命周期所有权，包括显式注册与注销。
- 确定顺序便于验证，但同步有序交付会增加延迟，也可能产生顺序依赖。
- 一个消费者失败后仍需尝试后续消费者，因此必须显式记录部分交付并定义恢复
  策略。
- 事件 schema 需要版本化，避免 Subject 与 Observer 通过偶然的 payload 细节
  紧耦合。
- 消费者可能触发嵌套工作，因此发布必须定义重入规则，防止递归和重复副作用。

## 参与者（Participants）

- **Subject：**发布事件源与有序订阅所有者，提供 `register`、`unregister` 和
  `publish` 行为。
- **Observer：**`release-observer-v1` 契约；其 `update(event)` 操作接收一条
  精确的 `release.published.v1` 事件，并返回回执或失败。
- **ConcreteSubject：**根 Software Release Notification Skill 与确定性
  `ReleaseSubject` 预言机。它在发布状态成功后通知，并记录每个 Observer 尝试。
- **ConcreteObserver：**审计、变更日志和团队通知消费 Skill。每个 Skill 都实现
  相同更新契约，并保持可独立检查。
- **Agent Host 与 Agent Runtime：**它们是执行上下文，不是 GoF Observer
  参与者。本构造样例无法观察其激活与解释行为。

## 协作（Collaboration）

发布前，ConcreteSubject 按声明顺序执行显式注册与注销操作。它校验发布事实，
构造一条有类型事件，冻结当前注册顺序快照，并以隔离副本调用每个 Observer 一次。
Observer 成功时返回非空回执；抛出异常或返回无效回执时生成失败交付记录，然后继续
调用后续 Observer。交付期间拒绝嵌套发布和订阅变更。

## 后果（Consequences）

发布工作流与消费者可以围绕稳定事件契约独立演化；消费者加入或离开时，无需在
Subject 中增加专用分支。确定顺序和逐消费者记录使部分交付可见。代价包括订阅
所有权、schema 演化、扇出延迟、部分失败恢复、潜在顺序依赖、持久系统中的重复
交付风险，以及未来引入重试时对幂等性的要求。

## Skillware 映射（Skillware Mapping）

自然语言 Behavioral Source 定义根发布策略与三个消费者更新行为。根和子 Skill
Artifact 构成该构造性 Skillware Unit 的一致 Skill 套件。JSON 夹具声明发布状态
和订阅操作，支持代码提供确定性协作预言机。Python 不激活或解释 Skill 行为源。

### 最终本体

经典角色严格保留为 **Subject**、**Observer**、**ConcreteSubject** 与
**ConcreteObserver**。`Agent Host` 激活 Skillware Unit，`Agent Runtime`
解释已激活的 Behavioral Source，但这些上下文对象不会变成源模式参与者。未来的
Execution Trace 或 Task Outcome 可以提供运行时证据；静态样例不虚构这些证据。

## 适用性（Applicability）

当一个已发布生命周期变化需要通过同一有类型契约通知可变数量的独立消费 Skill，
且 Subject 不应了解各消费者内部工作时，适合使用 Observer。审计、索引、通知、
缓存失效和派生制品更新都可能适用，前提是显式订阅和部分交付策略可接受。

## 不适用性（Non-Applicability）

如果所有动作必须原子提交，使用事务协调器；如果只需要一个请求/响应结果，使用
直接调用；如果固定步骤有意依赖前序输出，使用管道。文件系统轮询或无方向的广播
同样不是 Observer。

## 正向证据（Positive Evidence）

仓库样例是 **constructive** 证据。它实现全部四个 GoF 角色、精确的版本化事件、
三个已注册消费 Skill、注册顺序交付、显式注销、逐 Observer 回执、失败隔离、事件
副本隔离和重入拒绝。聚焦测试还证明确定性重跑、输入不变性、严格校验，以及精确的
CLI 输出和错误。

## 反向证据（Counter-Evidence）

确定性函数不能证明 Agent Runtime 会一致解释自然语言 Skill，也不能证明兼容
Agent Host 会激活它们。交付是同步且位于内存中的；样例没有持久队列、重试、去重、
超时、背压、崩溃恢复或事务发件箱。`delivered` 回执只说明更新函数在该预言机中
成功返回。

## 误判（False Positives）

轮询发布文件不是 Subject 驱动的通知。没有托管注册关系而向所有发现的端点广播，
也不构成 GoF 一对多依赖。Hook 名、事件标签或命令数组只是导航证据，除非公共更新
操作和参与者协作已建立。[`misuse/SKILL.md`](misuse/SKILL.md) 有意把轮询和未
注册广播组合成近似但不成立的案例。

## 开源对应（Open-Source Correspondence）

ECC 的评估固定在提交 `2bc924faf2f8e893bfe0af86b1931283693c30ae`。其 Hook
清单、运行器、测试和 continuous-learning-v2 制品为事件触发的独立行为提供部分
源码证据。该声明仅是 **candidate correspondence**：固定路径没有建立公共
Observer 更新契约、Observer 级显式注册与注销、所有匹配项的确定性交付或逐
Observer 失败核算。详情见 [`correspondence.md`](correspondence.md) 和本地固定
证据审计。

## 验证（Verification）

在 `sample/` 中运行 `python3 scripts/run_demo.py` 和 `python3 -m unittest
discover tests -v`。验证覆盖精确输出、三个 Observer 的注册顺序、注销、失败后
继续交付、嵌套发布拒绝、事件副本隔离、确定性重跑、输入不变性、精确夹具错误、
固定证据路径，以及无需网络的标准库独立执行。

## 局限（Limitations）

一个构造性场景和一个候选生态对应不能证明使用频率、比较收益、生产健壮性或跨
Host 行为等价性。该映射保留经典 GoF 意图与角色，不声称 Skillware 发明了
Observer，不声称每个 Hook 系统都实现 Observer，也不声称通知保证消费者侧事务
完成。
