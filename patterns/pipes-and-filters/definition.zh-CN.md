# 管道-过滤器模式

**规范来源。** 管道-过滤器是 Pattern-Oriented Software Architecture 传统中的架构模式，
由 Buschmann 等人系统描述；它不是 Gang of Four（GoF）模式。本记录保留 Data Source、
Filter、Pipe 与 Data Sink 四个规范角色。

## 意图（Intent）

让数据依次经过可独立替换的转换阶段，并用具有共同数据契约的显式通道连接这些阶段。

## 作用力（Forces）

- 各分流阶段需要独立职责与替换边界。
- 阶段顺序和恰好一次调用必须由外部运行器拥有。
- 每个边界都必须拒绝非法记录，不能依赖对话隐式状态。
- 调用者与相邻阶段之间不得共享可变记录别名。
- 失败必须停止后续处理并明确归属阶段。

## 参与者（Participants）

- **Data Source：**接收工单文本并创建 `support-ticket.v1`。
- **Filter：**规范化、脱敏、分类、优先级和回复草拟；都接受并返回同一记录。
- **Pipe：**在阶段间校验并深拷贝版本化记录。
- **Data Sink：**输出完成的分流记录与规范轨迹。
- Agent Host 与 Agent Runtime 是执行上下文，不是 POSA 参与者。

## 协作（Collaboration）

运行器先校验完整 Filter 集合并拥有固定顺序。Data Source 产生初始记录；Pipe 在每个
Filter 之前和之后校验并复制记录。首个异常或非法输出立即停止流程并标注阶段。Data
Sink 再校验并分离最终结果。

## 后果（Consequences）

Filter 可寻址、可测试、可替换，边界契约和失败位置清晰。代价是重复校验与复制、固定
拓扑，以及必须另外定义运行期流量策略。

## Skillware 映射（Skillware Mapping）

根 Skill 声明拓扑，五个子 Skill Artifact 承载 Filter 行为，引用文档承载 Pipe 契约，
fixture 分别表示 Data Source 与 Data Sink。Python oracle 只演示本地契约，不解释自然
语言 Skill。

### 最终本体（Final ontology）

源模式角色严格保持为 **Data Source**、**Filter**、**Pipe**、**Data Sink**。Behavioral
Source 持久化在 Skillware Unit 的 Skill Artifact 中；Agent Host 和 Agent Runtime 仍是
上下文，不改名为 POSA 参与者。

## 适用性（Applicability）

当处理具有稳定顺序、所有阶段能交换共同显式记录，且阶段需要独立测试或替换时使用。

## 不适用性（Non-Applicability）

当阶段需要循环协作、所有步骤必须共享一个事务，或无法形成实用共同契约时不要使用。
一个不可分割操作不应仅靠命名阶段伪装成管道。

## 正向证据（Positive Evidence）

构造示例验证字面 `run_pipeline` 场景、五个独立可注入 Filter、固定恰好一次顺序、每阶段
前后 Pipe 校验、深拷贝、邮箱脱敏、高优先级、可替换性、确定性和失败即停。

## 反向证据（Counter-Evidence）

oracle 是单进程顺序可信代码，不证明 Agent Runtime 解释、Host 激活、安全隔离、生产
吞吐、分布式取消或持久交付。

## 误判（False Positives）

把单体函数错误命名为 pipeline 并不是管道-过滤器：其步骤不可独立寻址或替换，也没有
显式 Pipe 契约。依赖隐藏对话状态的文字清单同样是误判。

## 开源对应（Open-Source Correspondence）

OpenMontage 在固定提交 `db91727598d08d40919d7d68a47864a5467bd448` 上是候选对应。
manifest、loader 与阶段 Skill 路径展示了顺序阶段和制品流，但共同记录、隔离与运行行为
仍未验证。详见 [`correspondence.md`](correspondence.md) 与
[冻结证据](evidence/openmontage-frozen-case.md)。

## 验证（Verification）

在仓库根目录运行 `python3 -m unittest discover patterns/pipes-and-filters/sample/tests -v`。
根 harness 还会隔离复制记录、运行专注测试并执行默认 CLI。

## 局限（Limitations）

本地 oracle 明确不覆盖缓冲、背压、并发和网络传输，也不覆盖重试、并行分支、持久队列、
超时、认证和资源计量。生产管道必须另行显式定义这些策略。Filter callable 属于可信代码；
它仍可修改外部状态、自身闭包，或通过反射绕过普通属性冻结。拓扑快照只保证当前运行的
身份和顺序不被描述符或原列表变更，不限制任意副作用。
