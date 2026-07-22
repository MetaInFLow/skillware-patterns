# 规约模式

**规范来源。**Specification 是 Eric Evans 在《Domain-Driven Design》中描述的
领域模式，不是 Gang of Four（GoF）模式。本记录保留 Specification、
Candidate 与 Composite Specifications（And/Or/Not）三类规范角色。

## 意图（Intent）

把领域规则表达为可命名、可复用的对象，判断 Candidate 是否满足规则，
并在不隐藏语义的前提下组合多条规则。

## 作用力（Forces）

- 费用规则需要独立命名、测试和复用。
- 任何规则执行前，Candidate 必须通过精确且有界的输入契约。
- 组合必须保留确定的布尔语义和清晰的优先级。
- 判定需要可检查解释，但不能改变布尔 API。
- 评估不得修改 Candidate，也不得依赖隐式状态。

## 参与者（Participants）

- **Specification：**具有 `is_satisfied_by(candidate) -> bool` 接口的命名规则。
- **Candidate：**接受 Specification 判定的费用数据映射。
- **Composite Specifications：**用 And、Or 和 Not 组合其他 Specification，
  仍保持相同接口。
- Agent Host 和 Agent Runtime 是执行上下文，不是 DDD 参与者。

## 协作（Collaboration）

调用方把不可变叶子 Specification 组合为可复用策略。策略先严格校验所有
叶子所需 Candidate 字段的并集，并保留每个字段从左到右首次出现的顺序。
内置规则与组合类是封闭实现；自定义规则必须通过冻结且已校验的 `Predicate`
包装器进入，不允许任意子类。布尔评估再按从左到右短路语义执行。`explain`
可保留短路轨迹，或在纯函数前提下评估全部叶子；两种模式的策略结果一致。

## 后果（Consequences）

领域规则可命名、可独立测试、可复用且可解释，组合能避免复制策略逻辑。
代价是更多小对象、显式 schema 治理，以及对评估和解释语义的明确定义。

## Skillware 映射（Skillware Mapping）

根 Skill Artifact 承载可复用费用审批策略，四个子 Skill Artifact 承载叶子
Specification 行为，引用文档承载精确 Candidate 与组合契约，共同构成
一个 Skillware Unit。Python oracle 只演示本地契约，不解释自然语言 Skill。

### 最终本体（Final ontology）

完整上下文是 **Behavioral Source -> Skill Artifact -> Skillware Unit -> Agent Host
-> Agent Runtime -> Execution Trace -> Task Outcome**。DDD 角色始终是
**Specification**、**Candidate** 和 **Composite Specifications**；Agent Host 与
Agent Runtime 仍是上下文，不改名为模式参与者。

## 适用性（Applicability）

当领域判定需要独立命名、组合、复用、测试或解释，且 Candidate 数据有明确
边界时使用。

## 不适用性（Non-Applicability）

对本质上会修改状态的命令、无法表达为稳定规则的无界判断，或不需复用与组合的
单个简单检查，不应使用。持久化查询转译是另一设计边界。

## 正向证据（Positive Evidence）

构造示例验证了字面的票据、预算、授权额度与部门场景，不可变叶子与组合
对象，AND/OR/NOT 真值语义，精确 Candidate 校验，有界整数金额，确定性纯评估，
自定义 Memo Predicate，任意子类拒绝，短路/全量解释，有界文件读取、ASCII 安全输出
和稳定 CLI 错误。

## 反向证据（Counter-Evidence）

本记录没有评估任何冻结外部实现，因此生态关系的证据状态是 **not observable**。
本地示例仅是构造性证据，不证明 Agent Host 激活、Agent Runtime 解释、生产策略适用性、
持久化转译或跨 Host 等价性。

## 误判（False Positives）

如果一个不透明的 `eligible(expense)` 函数包含所有规则，且条件不能独立命名、
组合、解释或复用，它就不是本模式。“确保费用有效”这类模糊文字也不是 Specification。

## 开源对应（Open-Source Correspondence）

**状态：not observable。**本记录不虚构、也不评估某个生态项目。仓库示例证明可构造性，
不是外部对应证据。详见 [`correspondence.md`](correspondence.md)。

## 验证（Verification）

在仓库根目录运行 `python3 -m unittest discover patterns/specification/sample/tests -v`。
根 harness 还会断言记录已物化、在隔离副本中运行聚焦测试，并执行默认 CLI。

## 局限（Limitations）

金额仅接受 0 到 1,000,000,000 的非负整数；集成方必须说明货币单位，通常为分。
浮点、NaN、无穷大和布尔值伪装的整数都会被拒绝。部门名在 NFC 规范化后区分大小写比较。
自定义 Predicate 值必须是有界 JSON 兼容数据：字符串最多 4,096 UTF-8 字节，
集合最多 128 项，数值绝对值最大 1,000,000,000，校验后 Candidate 最多 65,536 字节。
Predicate 名最多 128 字节，必须声明 1-32 个有序字段，解释最多 4,096 字节。
评估与解释 callable 每次都接收深拷贝，但它们仍只是按契约确定、纯函数的可信代码，
不是沙箱；闭包、反射和外部副作用无法被强制阻止。CLI 最多读取 65,537 字节并输出
ASCII 安全 JSON。
