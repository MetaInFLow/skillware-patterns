# 外观模式（Facade）

**经典来源。** Facade 是 Gamma、Helm、Johnson 与 Vlissides 在 1994 年
*Design Patterns: Elements of Reusable Object-Oriented Software* 中归纳的
Gang of Four 结构型模式。本记录只讨论该既有模式向 Skillware 的迁移，不主张
Skillware 发明了新模式，也不主张历史优先权。

## 意图（Intent）

在一组可独立寻址的子系统能力之上提供一个稳定、简化的访问契约，使客户端
能够完成常见任务，而不必了解子系统内部的选择与协调细节。

## 作用力（Forces）

- 客户端需要一个任务级操作，而各专门能力需要保持职责收敛并可独立检查。
- 专门能力可以保留直接访问方式，但普通调用者不应掌握选择、顺序与回退策略。
- 即使子系统内部组织变化，公开契约也应保持稳定。
- 集中入口降低客户端耦合，却可能使 Facade 过度膨胀或成为策略瓶颈。

## 参与者（Participants）

- **Client：**调用根事故响应 Skill 的操作员或任务级智能体执行过程。
- **Facade：**`sample/SKILL.md`，定义唯一请求/结果契约、协调规则和回退规则。
- **Subsystem：**诊断、影响评估和沟通三个子 Skill；每个都有可独立检查的
  `SKILL.md`。
- **Agent Host 与 Agent Runtime：**它们是执行上下文，不是 GoF Facade 参与者。
  在实际部署中，Agent Host 激活 Skillware Unit，Agent Runtime 解释行为源；但
  这个确定性构造样例不能观察或证明这两个角色。

## 协作（Collaboration）

Client 向 Facade 提交 `service` 和 `signal`。当信号为 `5xx spike` 时，Facade
先取得诊断，把诊断结果连同事故上下文交给影响评估，再把返回的评估交给沟通
起草，并且只组装四个公开结果字段。遇到未知信号时，它执行声明的人工分诊回退，
同时保留相同结果契约。内部路由细节不会返回给 Client。

## 后果（Consequences）

客户端只需理解一个接口，并与子系统协调细节隔离。专门能力仍可独立检查，也
能在公开契约之后演进。代价包括额外间接层、隐藏有用专门能力的风险，以及入口
Skill 不断吸收策略的压力。公开契约的改变仍须进行面向客户端的兼容性评审。

## Skillware 映射（Skillware Mapping）

根 Skill 中的自然语言行为源可以承载 Facade 操作。bootstrap 或调用策略可以
激活该入口契约，Agent Runtime 可以借助 Agent Host 的 Skill 加载操作解释相关
性、路由与回退规则；不需要新增插件方法或类。迁移成立的依据是参与者关系与
可观察访问行为，而不是文件类型或名称中出现 “facade”。

## 适用性（Applicability）

当调用者反复需要跨多个专门能力完成一个一致任务、稳定的请求/结果契约可以
隐藏协调细节，并且各子系统仍有独立身份时，适合使用 Facade。当激活或
bootstrap 策略需要保证普通任务总是先经过一个入口 Skill 时也适用。

## 不适用性（Non-Applicability）

只有一个原子 Skill、没有子系统时，不应使用 Facade；仅按主题归类 Skill 的
目录也不是 Facade；客户端必须直接控制每一次专门交互时同样不适用。主要矛盾
若是接口转换、算法替换、事件传递或叶节点与组合节点的统一处理，应选择其他模式。

## 正向证据（Positive Evidence）

本仓库样例属于**构造性（constructive）**证据：根事故响应 Skill 协调三个子
Skill，已知路径和回退路径均返回一个稳定契约，并有聚焦测试。与此分开，冻结的
Superpowers 案例为真实开源参与者关系提供**已确认对应（confirmed
correspondence）**证据。

## 反向证据（Counter-Evidence）

自然语言相关性判断和专门 Skill 激活仍依赖 Agent Host 与 Agent Runtime。
源代码检查不能证明不同 Host 具有相同激活可靠性。Facade 关系也不表示客户端
一定被禁止直接调用专门 Skill。

## 误判（False Positives）

仅列举子 Skill 的 README、菜单、注册表或根 `SKILL.md` 不是 Facade。只有路由
名称，却没有统一客户端操作、真实子系统协调和明确回退行为，也不构成 Facade。
[`misuse/SKILL.md`](misuse/SKILL.md) 有意展示了这一近似但不成立的案例。

## 开源对应（Open-Source Correspondence）

Superpowers `using-superpowers` 的评估固定在提交
`896224c4b1879920ab573417e68fd51d2ccc9072`，精确路径为
`skills/using-superpowers/SKILL.md`。任务级智能体执行过程是 Client，该 Skill
提供 Facade 访问策略，专门工作流 Skills 构成子系统。SessionStart hook 引导该
策略；Agent Host 加载它，Agent Runtime 解释它。固定链接和证据边界见
[`correspondence.md`](correspondence.md)。该生态对应主张与本地构造性样例相互独立。

## 验证（Verification）

在 `sample/` 中运行 `python3 scripts/run_demo.py` 和
`python3 -m unittest discover tests -v`。验证覆盖 `5xx spike` 的精确输出、未知
信号时精确的 `request-human-triage` 回退、畸形输入的非零退出、全部参与者路径
解析，以及不使用网络和其他模式目录。

## 局限（Limitations）

一个构造性场景和一个已确认对应不能证明生态使用频率、自动质量提升或跨 Host
行为等价。演示用确定性的 Python 函数作为行为源的可执行判定基准，不模拟概率性
模型解释。该映射保留既有 GoF 作用力与参与者，但不声称 Skillware 发明了 Facade。
