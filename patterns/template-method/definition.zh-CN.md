# 模板方法模式（Template Method）

**经典来源。** Template Method 是 Gamma、Helm、Johnson 与 Vlissides 在
1994 年 *Design Patterns: Elements of Reusable Object-Oriented Software*
中归纳的 Gang of Four 行为型模式。本记录只迁移这一既有模式，不主张
发明或历史优先权。

## 意图（Intent）

在 AbstractClass 操作中定义算法骨架，把选定操作延迟给 ConcreteClass
实现，但不允许 ConcreteClass 改变算法结构。

## 作用力（Forces）

- 每份企业 RFP 都必须按可审计顺序提取需求、分析缺口、应用领域知识、
  起草并完成质量检查。
- 医疗与金融响应需要不同关注点和证据，但复制整套流程会使必经阶段漂移。
- 领域扩展需要足够上下文，同时不能跳过、重复或重排必经工作。
- 钩子失败或输出畸形时必须可预期地停止，否则草案可能在缺少有效领域
  输入时被误认为完整。
- 输入、钩子输出和最终结果都需要确定性边界校验、稳定错误与复制隔离，
  否则畸形或可变数据会破坏骨架不变式。
- 严格骨架会限制扩展自由；钩子过多也会降低可理解性。

## 参与者（Participants）

- **AbstractClass：**根企业 RFP 响应 Skill 与确定性
  `RfpResponseTemplate`。它拥有 `run-rfp` 模板方法、实现所有必经
  操作、显式分派自身模板实现，并仅调用一次可重写操作。
- **ConcreteClass：**医疗与金融子 Skill Artifact 及对应 Python 子类。
  每个实现仅通过 `rfp-domain-hook-v1` 提供静态 `apply-domain-hook` 可调用项。
- **Agent Host 与 Agent Runtime：**二者是执行上下文，不是 GoF Template
  Method 参与者。本构造样例无法观察其激活与解释行为。

原语操作和模板方法是上述两个经典参与者拥有或实现的操作，不是额外
参与者角色。

## 协作（Collaboration）

公开帮助器显式调用 AbstractClass 模板实现，不创建 ConcreteClass 实例。
AbstractClass 校验请求，把身份、领域、需求与轨迹保留为局部快照，再提取需求 id、
分析缺口、构建隔离钩子请求，并仅调用一次静态钩子。它在起草前校验并复制
钩子结果，然后质检并校验完整结果。ConcreteClass 直接定义的模板或必经阶段名会被拒绝；
通过多重继承引入的同名方法不会被分派。钩子异常原样传播，且不会继续起草或质检。

## 后果（Consequences）

根流程单一拥有顺序政策，领域变体共享必经行为，扩展边界也可测试。
新领域只需添加一个符合契约的 ConcreteClass。代价包括根与子组件耦合、
契约版本管理、刻意狭窄的扩展面，以及骨架演进时的协同修改。

## Skillware 映射（Skillware Mapping）

Behavioral Source 定义并指导根与子 Skill Artifact。根文件指定
AbstractClass 算法，子文件指定两个 ConcreteClass 操作。这些制品与其
契约构成一个一致的 Skillware Unit。JSON 夹具提供请求，标准库 Python
是顺序与边界行为的确定性预言机，不是 Agent Runtime 解释器。

### 最终本体

经典 GoF 角色严格保留为 **AbstractClass** 和 **ConcreteClass**。
Behavioral Source 持久化在 Skill Artifact 中，并由 Skillware Unit 承载。
Agent Host 激活该单元，Agent Runtime 在上下文中解释已激活的行为源，但二者都
不会成为源模式参与者。Execution Trace 记录情境化执行，Task Outcome 是经评估
的效果；本静态样例不虚构二者。

## 适用性（Applicability）

当变体共享有意义且稳定的算法顺序，只在少数已声明操作上不同时，适合使用
Template Method。受监管的响应流程、审查协议、文档生产、准入和验证流程都可能适用。

## 不适用性（Non-Applicability）

如果需在运行时通过统一接口选择整套可互换算法，应使用 Strategy。对于没有共同
不变部分的独立清单，或根本无需特化的简单序列，不应强行引入本模式。

## 正向证据（Positive Evidence）

仓库样例是 **constructive** 证据。它实现两个经典角色、五阶段骨架、
共享同一精确静态钩子契约的两个 ConcreteClass、钩子仅调用一次、AbstractClass
显式分派、多重继承绕过抵抗、子类重写拒绝、局部快照、失败终止、严格输入/钩子/结果校验、
复制隔离、稳定错误、精确夹具与确定性重跑。

## 反向证据（Counter-Evidence）

Python 语言约束和测试不能证明 Agent Runtime 会以相同方式解释
Behavioral Source，也不能证明 Agent Host 会激活预期制品。领域输出只是
夹具内容，不是经证实的行业专业意见。该进程内预言机不是 Python 沙箱；拥有模块访问权的
可信钩子仍可产生无关副作用或启动独立嵌套流程，但它无法改变当前调用的局部身份、领域、轨迹与必经分派。

## 误判（False Positives）

没有可重写操作的固定清单只是固定流程。若每个领域配置都自己拥有整套顺序，
就没有 AbstractClass 保护顺序，因而不是 Template Method。运行时选择完整
算法更接近 Strategy。[`misuse/SKILL.md`](misuse/SKILL.md) 故意让领域重排和省略阶段。

## 开源对应（Open-Source Correspondence）

Superpowers 在提交 `896224c4b1879920ab573417e68fd51d2ccc9072` 上构成
**candidate correspondence**。其精确 brainstorming 与 TDD Skill 路径规定不变
流程骨架。被审查源没有证明有界领域钩子、ConcreteClass 替换、防止特化重排或
Agent Runtime 行为，因此不是已确认对应。

## 验证（Verification）

在 `sample/` 中运行 `python3 scripts/run_demo.py` 与 `python3 -m unittest
discover tests -v`。验证覆盖精确五阶段顺序、AbstractClass 所有权、钩子仅调用
一次、共享契约的两个 ConcreteClass、显式非绑定分派、BypassMixin 绕过抵抗、静态钩子隔离、
恶意修改与阶段声明拒绝、有界替换、钩子失败、畸形结果、确定性
夹具、输入不变、输出隔离、重复 JSON 成员、无效 UTF-8、孤立代理项、循环、深度和类型。

## 局限（Limitations）

一个构造式 RFP 场景不能证明模式流行度、比较优势、生产安全性或跨 Host 行为等价。
样例只建模一个扩展操作。新的采购法域、证据检索、协商例外、人工审核或渲染都需要显式契约与测试。
