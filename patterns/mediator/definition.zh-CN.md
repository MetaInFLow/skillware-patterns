# 中介者模式（Mediator）

**经典来源。** Mediator 是 Gamma、Helm、Johnson 与 Vlissides 在 1994 年
*Design Patterns: Elements of Reusable Object-Oriented Software* 中描述的
Gang of Four 行为型模式。本记录只做迁移，不主张发明或优先权。

## 意图（Intent）

定义一个封装一组对象交互方式的对象。让对象不再显式引用彼此，以促进松耦合，并允许独立
改变交互方式。

## 作用力（Forces）

- 构建、安全、文档和审批四个专长必须共同形成发布决定，却不能持有彼此引用。
- 联合就绪政策需要唯一所有者，但专长检查必须留在对应子 Skill 内。
- 每份必需报告都必须存在、合法、唯一寻址，并按稳定顺序恰好处理一次。
- 一个专长发生异常时应保守阻止发布，同时不能阻断后续参与者。
- 输入输出必须有界、不修改调用方数据，并能产生确定性 oracle。
- 中心化减少关系数量，却可能让协调者变复杂；若吸收专长工作就会退化为 God Skill。

## 参与者（Participants）

- **Mediator：** `deployment-readiness-v1` 报告接口及 Python `Mediator` 边界。
  它定义 Colleague 如何报告，而不命名其他 Colleague。
- **ConcreteMediator：** Deployment Coordinator 根 Skill 与
  `DeploymentCoordinator`。它注入并寻址参与者、隔离失败、拥有就绪政策并作最终决定。
- **Colleague：** 构建、安全、文档、审批子 Skill 与 `Colleague` 实例。每个参与者只执行
  自己的有界专长工作，并仅向 Mediator 报告一次。
- **Agent Host 与 Agent Runtime：** 它们是执行上下文，不是 GoF Mediator 参与者；本构造
  样例没有观察到其激活或解释行为。

## 协作（Collaboration）

ConcreteMediator 先校验完整且不重复的参与者集合，再按构建、安全、文档、审批顺序绑定到
自身地址。输入经校验和复制后，每个 Colleague 只收到自己的状态并被寻址一次。Colleague
执行自身可调用专长，再通过 `Mediator.receive` 报告；它不持有同伴集合或同伴路径。
ConcreteMediator 将异常或无效报告隔离为 `fail` 并继续。四次尝试结束后，只有全部为
`pass` 才发布，否则阻止。输出状态是固定顺序的新副本，通信路径固定为
`participants->mediator->release`。

## 后果（Consequences）

参与者关系从全连接网状结构降为四条中心关系。就绪政策、顺序、失败处理、校验与决定变得
可审计。代价是中心政策依赖、协调者膨胀风险和进程内可信代码假设。公开结果有意只保留
`fail`，不会携带专长异常细节。

## Skillware 映射（Skillware Mapping）

Behavioral Source 定义并指导根 ConcreteMediator 与子 Colleague Skill Artifact。这些
Artifact、参考契约、夹具和 oracle 共同组成一个构造性 Skillware Unit。标准库 Python 是
确定性 oracle，不解释自然语言 Skill。

### 最终本体

源模式角色严格保持 **Mediator**、**ConcreteMediator**、**Colleague**。Behavioral
Source 持久化于 Skill Artifact，并由 Skillware Unit 承载。Agent Host 激活该单元，Agent
Runtime 在上下文中解释激活的 Behavioral Source，但二者都不成为 GoF 参与者。Execution
Trace 记录情境化执行，Task Outcome 是经评价的效果；本静态样例不伪造二者。

## 适用性（Applicability）

当多个独立负责的 Skill 必须共同参与一项政策、拓扑原本会形成同伴网状结构，而一个协调者
可以只拥有交互而不吸收专长行为时，使用 Mediator。部署门禁、审批协调、事故角色和多专长
评审都适合。

## 不适用性（Non-Applicability）

若只是互不相关的列表、固定数据变换管道，或领域服务本就应拥有全部工作，则不要使用
Mediator。不要用中心化掩盖含糊契约。协调者若执行全部检查，就是 God Skill，而不是健全的
Mediator。

## 正向证据（Positive Evidence）

仓库样例是**构造性**证据。它实现三个经典角色、四个隔离子 Skill、字面
`coordinate({'build':'pass','security':'pass','docs':'pass','approval':'pass'})`
API、精确发布/阻止决定与通信路径、固定寻址次数和顺序、缺失/额外/重复/错误类型/非法状态
拒绝、可调用参与者注入、异常及无效报告的保守隔离、不修改输入、确定性夹具、稳定 CLI 错误
以及纯标准库独立运行。

## 反向证据（Counter-Evidence）

Python oracle 不证明 Agent Runtime 解释、Agent Host 激活或不存在带外通信。它只测试单进程
协作对象。它也把专长失败压缩为 `fail`；生产系统需要另设受保护诊断通道。静态 Skill 文本
本身不能证明模型永远不会调用同伴。

## 误判（False Positives）

所有参与者互相调用的全连接工作流不是 Mediator，因为 Colleague 仍显式引用彼此。中心 God
Skill 若亲自完成构建、安全、文档和审批，也不是健全 Mediator，因为它抹除了专长所有权而
非封装交互。两种误用都见 [`misuse/SKILL.md`](misuse/SKILL.md)。

## 开源对应（Open-Source Correspondence）

Anthropic financial-services 在提交
`4aa51ed3d379731f8f9beff498d749580372699c` 上是**候选对应**。检查过的 GL Reconciler
协调者、三个子代理清单和 cookbook 测试展示了中心编排、专长叶节点与深度一检查。但该同级
公开来源没有建立共同 Colleague 契约，也没有验证运行时决定行为、调用顺序或失败隔离。见
[`correspondence.md`](correspondence.md) 与
[冻结证据](evidence/financial-services-frozen-case.md)。

## 验证（Verification）

在 `sample/` 内运行 `python3 scripts/run_demo.py` 和 `python3 -m unittest discover tests
-v`。测试覆盖全员通过后发布、任一位置失败即阻止、精确状态副本、注入寻址、恰好一次的固定
顺序、可调用异常及无效报告隔离、重复/缺失/额外/非法参与者与状态、跨 Mediator 绑定、子
Skill 同伴隔离、损坏和非 UTF-8 输入、确定性夹具、稳定错误及默认 CLI 输出。仓库根 harness
会自动复制并执行本实体化记录。

## 局限（Limitations）

样例假设可信进程内代码。私有引用、类型校验与绑定规则是契约边界，不是安全沙箱；反射、
子类覆盖、monkeypatch、任意内存访问或共享外部服务都可绕过。
确定性 oracle 不解释自然语言 Skill。生产系统还需要能力强制、报告认证、超时、并发政策、受保护诊断、重放防护、可观测性
以及真实参与者通信审计。
