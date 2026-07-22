# 策略模式（Strategy）

**经典来源。** Strategy 是 Gamma、Helm、Johnson 与 Vlissides 在 1994 年
*Design Patterns: Elements of Reusable Object-Oriented Software* 中归纳的
Gang of Four 行为型模式。本记录只迁移这一既有模式，不主张发明或历史优先权。

## 意图（Intent）

定义一组算法，把每个算法封装在公共 Strategy 接口之后，并使其可以相互替换，从而
让算法独立于使用它的 Context 发生变化。

## 作用力（Forces）

- 低风险变更需要快速反馈，安全敏感或范围更大的变更值得更深审查。
- 无论审查深度如何，调用方都需要同一请求和结果接口。
- 选择策略必须显式且可测试，不能隐藏在模型选择、对话判断或可变全局上下文中。
- 候选过程必须完成同一任务；一个路由器能到达多个无关分支，不代表它们可互换。
- 更丰富的算法可以发现更多问题，但不能迫使 Context 或调用方理解另一种输出
  schema。
- 拆分策略会增加制品和契约测试，也会引入自身可能判断失误的选择策略。

## 参与者（Participants）

- **Context：**根风险感知代码审查 Skill 和确定性 `RiskAwareCodeReview`。它校验
  请求、选择或接收一个被直接寻址的策略、委托审查并校验结果。
- **Strategy：**所有过程共同遵循的 `risk-aware-code-review-v1` `review` 契约。
- **ConcreteStrategy：**Fast Scan、Deep Review 子 Skill 及对应 Python 对象。
  每个实现在同一操作和请求/结果契约后拥有不同规则集。
- **Agent Host 与 Agent Runtime：**二者是执行上下文，不是 GoF Strategy
  参与者。本构造样例无法观察其激活与解释行为。

## 协作（Collaboration）

Context 先校验严格请求；安全敏感或文件数至少为四个时选择 Deep Review，否则选择
Fast Scan。调用方也可为了审计、重放或契约测试显式寻址任一注册策略。Context 把
同一请求的独立副本交给恰好一个 ConcreteStrategy。Fast Scan 应用三条高信号规则，
Deep Review 在此基础上增加三条上下文规则。返回前，Context 校验策略身份、文件
顺序、发现记录和派生汇总。

## 后果（Consequences）

审查深度可以变化，而调用方和结果接口不变。选择与算法行为可以分别测试，策略可以
注入或替换，不兼容输出在同一边界失败。代价包括每个过程一个制品、重复的契约校验、
需要随风险演进的显式策略，以及较快策略遗漏深度策略可发现问题的可能性。

## Skillware 映射（Skillware Mapping）

自然语言 Behavioral Source 定义 Context 策略、公共 Strategy 操作和两个
ConcreteStrategy 过程。根与子 Skill Artifact 组成一致的 Skillware Unit。JSON
夹具提供审查请求；标准库 Python 为选择、委托和输出契约提供确定性预言机，但不会
激活或解释 Skill 文件。

### 最终本体

经典角色严格保留为 **Context**、**Strategy** 和 **ConcreteStrategy**。
`Agent Host` 激活 Skillware Unit，`Agent Runtime` 解释已激活的 Behavioral
Source，但这些上下文对象都不会成为源模式参与者。Execution Trace 记录情境化执行，
Task Outcome 是被评估的效果；本静态样例不会虚构二者。

## 适用性（Applicability）

当多个过程解决同一任务、遵循同一接口，并且必须按显式策略或直接选择变化而不改写
调用方时，使用 Strategy。真实要求可替换性的审查深度、搜索算法、排序方法、压缩
策略、定价计算或校验模式都可能适用。

## 不适用性（Non-Applicability）

对于必须全部依次执行的步骤、由持久状态控制的生命周期行为、增加职责的包装器，或
输入结果不兼容的无关子命令，不要使用 Strategy。若没有算法契约和可独立寻址的过程，
仅仅选择不同模型也不是 Strategy。

## 正面证据（Positive Evidence）

仓库样例是 **constructive** 证据。它实现三个 GoF 角色、一个严格请求/结果契约、
两个不同策略、显式风险选择、直接寻址、依赖注入、边界校验和确定性夹具。聚焦测试把
选择与委托分开验证，并覆盖同一 Context 中的替换、错误策略结果拒绝、精确输出、
稳定错误、输入不变性，以及无网络和模型依赖的标准库执行。

## 反证与边界（Counter-Evidence）

Python 预言机无法证明 Agent Runtime 会同样解释 Behavioral Source，也无法证明
兼容 Agent Host 会激活它。词法规则不会解析编程语言、检查未变更上下文、跟踪数据流、
执行测试或评估可利用性，因此不构成生产级安全质量证据。四文件阈值也是场景规则，
不是经验最优值。

## 假阳性（False Positives）

当条件路由的分支完成不同任务或暴露不同接口时，它不是 Strategy。若调用方不能通过
同一操作寻址并替换多个提示，这些提示也不必然是策略。
[`misuse/SKILL.md`](misuse/SKILL.md) 特意把依赖链接发现与部署审批路由到不兼容
契约，形成近似但错误的例子。

## 开源对应（Open-Source Correspondence）

UI/UX Pro Max 在提交 `8a81ed60272d21d4b8808f7308d49a0b1b000555` 上是
**candidate correspondence**。固定版本的 Skill 工具会路由领域搜索、技术栈搜索
和设计系统生成。但审阅路径没有为所有分支声明同一请求/结果契约：搜索操作返回带
不同元数据的映射，设计系统生成返回渲染文本；这些路径也没有展示契约一致性测试或
完整的 Context 到 Strategy 替换。论文限定仍是：“Open-source correspondence is
motivation only; comparative benefit requires runtime study.” 详见
[`correspondence.md`](correspondence.md) 与
[固定证据](evidence/ui-ux-pro-max-frozen-case.md)。

## 验证（Verification）

在 `sample/` 下运行 `python3 scripts/run_demo.py` 和 `python3 -m unittest discover
tests -v`。验证覆盖低风险、安全敏感和文件阈值选择，显式寻址，注入替代实现，不同
规则行为，严格公共结果字段，错误注入结果，以及 schema、类型、边界、UTF-8、JSON
和路径校验、确定性重跑与输入不变性。仓库根 harness 会复制并独立运行本样例。

## 局限（Limitations）

一个构造场景不能证明生态普遍性、比较收益、生产审查准确率或跨 Host 行为等价。扩展
请求、规则集、阈值、严重性策略或结果都需要版本化契约变更和新一致性夹具。策略可互换
不表示成本或发现结果相同，而是要求它们可通过声明的接口相互替换。
