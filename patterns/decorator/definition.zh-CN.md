# Skillware 中的装饰模式

## 意图（Intent）

在保持同一 Component 接口的前提下，动态地为 Skill 增加有界的职责，
使调用者能够通过同一操作使用基础 Skill、单个包装器或多层包装组合。

## 作用力（Forces）

- 稳定的核心行为不应为每个可选检查而被复制或修改。
- 不论启用哪些检查，调用者都需要同一请求与结果契约。
- 每个增强职责需要独立组合或移除。
- 包装顺序可能影响结果，因此必须明确声明并测试。
- 如果每个边界不隔离所有权，可变请求和结果会产生隐式耦合。
- 包装器的失败语义必须与被包装 Component 一致。

## 参与者（Participants）

### Component

定义被包装和未包装对象共用的操作与严格请求/结果契约。本样例中是
`contract-review-v1`：`review({text})` 严格返回 `{summary, findings}`。

### ConcreteComponent

实现可以单独使用的基础操作。Base Contract Review 校验合同文本，返回稳定的
基础结果，不添加增强发现。

### Decorator

保存另一个 Component 的引用，并实现同一 Component 接口。通用包装协议会
校验并复制请求，只委托一次，校验并复制结果，保持失败语义，且不增加必填字段。

### ConcreteDecorator

在委托前后增加一项职责，同时保持通用包装协议。Privacy Check 追加邮箱隐私
发现，Citation Check 追加缺失引用标记发现。它们都仍然是有效 Component，可以包装
基础组件或相互包装。

Agent Host 和 Agent Runtime 是执行上下文，不是 GoF 参与者，也不构成
Component/Decorator 关系的证据。

## 协作（Collaboration）

调用者把有效 Component 请求交给最外层装饰器。每层 Decorator 校验自己的请求
快照，并用另一份拷贝只调用被包装 Component 一次。进入时从外向内委托，
ConcreteComponent 返回后再从内向外传递结果。每个 ConcreteDecorator 校验并复制
完整内层结果，然后只追加自己的发现。

对于 `with_citation_check(with_privacy_check(base_review))`，进入路径是 Citation、
Privacy、Base，返回路径是 Base、Privacy、Citation。因此基础发现在前，隐私发现
其次，引用发现最后。反转包装层级会得到引用在前、隐私在后，但 Component 契约不变。

## 结果（Consequences）

可选审查行为可在不修改基础 Skill 的情况下组合。调用者可以通过同一操作替换
装饰后的 Component，也可以独立增加新的有界装饰器。

该设计会增加参与者边界，且使嵌套顺序成为行为的一部分。重复校验与复制会增加工作量，
但能防止变异和别名泄漏。无界包装栈可能重复检查或遮蔽延迟，契约演进需要在所有参与者间版本化。

## Skillware 映射（Skillware Mapping）

| GoF 角色 | Skillware 载体 | 构造性产物 |
| --- | --- | --- |
| Component | 共享 Skill 请求/结果契约 | `sample/references/contract-review-component.md` |
| ConcreteComponent | 基础合同审查子 Skill | `sample/child-skills/base-contract-review/SKILL.md` |
| Decorator | 保持契约的包装协议与根组合 | `sample/SKILL.md` |
| ConcreteDecorator | 隐私和引用检查子 Skill | `sample/child-skills/privacy-check/SKILL.md`, `sample/child-skills/citation-check/SKILL.md` |

Python 预言机提供相同关系的可调用对象。自然语言 Skill 是行为源；预言机校验所声明的
协作，但不声称能解释这些 Skill。

## 适用性（Applicability）

当基础职责稳定、可选检查共享完整接口、多个检查需要组合，且调用者不应关心
Component 是否被包装时，使用装饰模式。包装顺序与失败策略必须可以被精确声明并做一致性测试。

## 不适用性（Non-Applicability）

如果增加的行为需要不同请求或结果契约、替代而不是环绕基础任务、协调无关对等者、
选择一种可互换算法、只控制访问而不增加职责，或需要全局工作流知识，就不应使用装饰模式。

## 正向证据（Positive Evidence）

构造性样例包装一个可注入 Component，而不是检查或复制它。严格测试覆盖计划中的原样调用
`with_citation_check(with_privacy_check(base_review))`，验证隐私后引用的发现顺序，
反转包装顺序，注入替代基础组件，在每个边界校验同一字段，原样传播异常，以及请求/结果别名隔离。

## 反向证据（Counter-Evidence）

[`misuse/SKILL.md`](misuse/SKILL.md) 复制基础过程，增加必填 `approval_token`，
并返回必填 `privacy_approved` 字段。它既不保存也不委托给 Component，无法替换
`contract-review-v1`。

## 假阳性（False Positives）

hook、中间件标签、嵌套目录或外形像包装器的 prompt 不会自动成为 Decorator。如果
日志包装改变了公共契约或从未调用原任务，仅在任务前后记录日志也不足够。复制基础 prompt 后增加步骤是复制式继承，不是对象组合。

## 开源对应（Open-Source Correspondence）

**状态：未评估对应。** 本记录未评估任何公开且锁定修订的生态案例。目录中的可能载体类别
不能单独证明完整参与者关系。有界证据标准与构造性声明见
[`correspondence.md`](correspondence.md)。

## 验证（Verification）

在 `sample/` 中运行 `python3 scripts/run_demo.py` 和 `python3 -m unittest discover tests -v`。
验证覆盖原样兼容 API、Component 字段保持、默认与反转装饰顺序、单次委托、注入组件、
匹配与不匹配行为、原样失败传播、确定性输出，以及严格请求、结果、发现、UTF-8、代理项、重复 JSON 成员、类型和边界校验。根仓库 harness 会独立复制并运行样例。

## 局限（Limitations）

样例中的邮箱正则和 `[missing]` 字面标记不是生产级隐私、引用或法律审查。一个构造性
样例不能证明生态普及度、跨 Host 等价性、模型解释、生产质量或比较收益。Python 边界复制只是对所有权策略的建模，不证明 Agent Runtime 会强制执行该策略。
