# Skillware Patterns

Skillware 论文的双语可执行模式迁移补充材料。

[English](README.md)

## 论文与仓库定位

本仓库是 Haodi Fan 与 Zucong Lan 的公开论文 [Skillware: A Software Ontology and Engineering Lifecycle for Persistent Behavioral Artifacts](https://arxiv.org/abs/2607.18970) 的双语可执行补充，发布论文中“软件工程连续性”论证的一个有界部分：可审计的模式迁移记录与确定性示例。

**Skillware 是将软件工程扩展至持久行为制品的软件抽象。** 这里涉及的边界是：

```text
Behavioral Source -> Skill Artifact -> Skillware Unit -> Agent Host -> Agent Runtime
```

Behavioral Source 承载持久的任务指令与约束；Skill Artifact 将这些来源与可选代码、资源组织在一起；Skillware Unit 为该制品提供可独立管理的软件身份与生命周期；兼容的 Agent Host 激活该单元；Agent Runtime 在具体执行上下文中解释已激活的来源。完整定义及类别条件见[《Skillware 定义》](docs/skillware-definition.md)。

## 软件工程连续性

本仓库检验的是：当关键职责由持久行为制品而非仅由传统类承载时，既有软件模式能否仍保持可识别。只有源意图、设计作用力、参与者对应、后果、实现证据、聚焦验证和误用判别器均可观察时，迁移才能准入。

这不是新的设计模式集合。源模式及其传统仍属于既有软件工程知识。本补充贡献的是有界的 Skillware 参与者映射和构造性实现，不主张模式所有权，也不把模式名称本身当作迁移证据。

## 职责分工

| 制品 | 职责 | 证据边界 |
| --- | --- | --- |
| [公开 arXiv 论文](https://arxiv.org/abs/2607.18970) | 定义 Skillware 本体，并提出软件工程连续性的论证。 | 公开摘要页是论文的权威入口。 |
| 私有写作与研究档案 | 保存论文源码、语料分析、冻结案例、反证与研究溯源。 | 写作版本 `1fc1dfd` 是不带链接的溯源标识；该档案不是公开依赖。 |
| `MetaInFlow/skillware-patterns`（本仓库） | 发布迁移协议、有来源的目录、参与者映射、可运行示例、误用案例和聚焦测试。 | 这份自包含的可执行补充提供检查与运行其主张所需的本地证据；构造性输出不能验证本体，也不能证明生态普遍性。 |

[论文映射](docs/paper-map.md)明确区分这三类职责，并把本补充绑定到 `v0.1-paper-v1`。

## 目录概览

| 声明范围 | 含义 | 索引 |
| --- | --- | --- |
| **23 GoF patterns screened** | 每个经典 Gang of Four 模式对应一条有来源的筛查记录；筛查不等于实现。 | [GoF-23 筛查矩阵](catalog/gof-23-screening.md) |
| **10 detailed GoF implementations** | 六个正文模式和四个仓库补充模式，各自带独立的构造性示例。 | [详细模式索引](catalog/pattern-index.md) |
| **2 patterns from other established traditions** | POSA 的 Pipes and Filters 与 DDD 的 Specification，和 GoF 分开标注。 | [详细目录元数据](catalog/pattern-index.yaml) |

十二个模式目录在一个扁平导航树中互为同级。每个 `pattern.yaml` 用 `source_tradition`、`source_category`、`paper_role` 和 `implementation_status` 记录元数据；`source_category` 保留来源传统中的类别，不形成第二套目录层级。

## 正文映射

论文第 5.3 节和表 5 使用下列六个映射。生态对应与本地可构造性是两类独立主张。

| 模式 | 来源传统 / `source_category` | Skillware 参与者关系 | 生态主张 | 本地示例主张 | 记录与证据 |
| --- | --- | --- | --- | --- | --- |
| [Facade](patterns/facade/definition.md) | `gang-of-four` / `structural` | 一个入口 Skill 在多个专家 Skill 之上提供稳定契约。 | confirmed correspondence | constructive | [对应记录](patterns/facade/correspondence.md) · [示例](patterns/facade/sample/) |
| [Adapter](patterns/adapter/definition.md) | `gang-of-four` / `structural` | 薄绑定把规范 Skill 语义转换为目标系统契约。 | confirmed correspondence | constructive | [对应记录](patterns/adapter/correspondence.md) · [示例](patterns/adapter/sample/) |
| [Composite](patterns/composite/definition.md) | `gang-of-four` / `structural` | 原子阶段和组合阶段共享同一调用及结果契约。 | candidate correspondence | constructive | [对应记录](patterns/composite/correspondence.md) · [示例](patterns/composite/sample/) |
| [Observer](patterns/observer/definition.md) | `gang-of-four` / `behavioral` | Subject 向已注册且相互独立的消费者发送类型化事件。 | candidate correspondence | constructive | [对应记录](patterns/observer/correspondence.md) · [示例](patterns/observer/sample/) |
| [State](patterns/state/definition.md) | `gang-of-four` / `behavioral` | 持久状态控制允许的动作与转换。 | candidate correspondence | constructive | [对应记录](patterns/state/correspondence.md) · [示例](patterns/state/sample/) |
| [Strategy](patterns/strategy/definition.md) | `gang-of-four` / `behavioral` | 一个请求/结果契约在可互换过程之间进行选择。 | candidate correspondence | constructive | [对应记录](patterns/strategy/correspondence.md) · [示例](patterns/strategy/sample/) |

这些状态复现[论文映射](docs/paper-map.md)中的证据边界；构造性示例不会把候选生态对应升级为已确认对应。

## 仓库补充实现

补充部分提供四个额外 GoF 记录，以及两个来自其他既有传统的记录。

| 模式 | 来源传统 / `source_category` | Skillware 参与者关系 | 生态主张 | 本地示例主张 | 记录与证据 |
| --- | --- | --- | --- | --- | --- |
| [Decorator](patterns/decorator/definition.md) | `gang-of-four` / `structural` | 可选审查 Skill 围绕同一个组件契约逐层包装。 | candidate correspondence | constructive | [对应记录](patterns/decorator/correspondence.md) · [示例](patterns/decorator/sample/) |
| [Template Method](patterns/template-method/definition.md) | `gang-of-four` / `behavioral` | 根 Skill 固定工作流顺序，并开放有边界的特化钩子。 | candidate correspondence | constructive | [对应记录](patterns/template-method/correspondence.md) · [示例](patterns/template-method/sample/) |
| [Memento](patterns/memento/definition.md) | `gang-of-four` / `behavioral` | Caretaker 捕获并恢复 Originator 的不透明配置状态。 | candidate correspondence | constructive | [对应记录](patterns/memento/correspondence.md) · [示例](patterns/memento/sample/) |
| [Mediator](patterns/mediator/definition.md) | `gang-of-four` / `behavioral` | 协调器集中管理部署就绪 Skill 之间的交互。 | candidate correspondence | constructive | [对应记录](patterns/mediator/correspondence.md) · [示例](patterns/mediator/sample/) |
| [Pipes and Filters](patterns/pipes-and-filters/definition.md) | `pattern-oriented-software-architecture` / `architectural` | 有序 Filter 通过显式 Pipe 转换同一个带版本工单记录。 | candidate correspondence | constructive | [对应记录](patterns/pipes-and-filters/correspondence.md) · [示例](patterns/pipes-and-filters/sample/) |
| [Specification](patterns/specification/definition.md) | `domain-driven-design` / `domain` | 具名且可组合的规则评估一个有边界的费用候选对象。 | not observable | constructive | [对应记录](patterns/specification/correspondence.md) · [示例](patterns/specification/sample/) |

Pipes and Filters 不是 GoF 模式，Specification 也不是 GoF 模式；两者分别保留 POSA 与 DDD 的既有来源。

## Facade 示例导览

“生产事故响应”示例把模式迁移落实为可检查步骤：

1. 根[外观 Skill](patterns/facade/sample/SKILL.md)接收 `service` 与 `signal`。[参与者映射](patterns/facade/participant-map.yaml)把入口契约、三个专家 Skill 和调用者对应到源模式参与者。
2. 确定性[演示脚本](patterns/facade/sample/scripts/run_demo.py)读取有效的[事故输入](patterns/facade/sample/fixtures/valid/incident.json)，依次调用诊断、影响评估和沟通专家，最终生成稳定的[预期结果](patterns/facade/sample/expected/incident-result.json)：`summary`、`impact`、`actions` 与 `communication`。

```bash
python3 patterns/facade/sample/scripts/run_demo.py
```

3. [聚焦测试](patterns/facade/sample/tests/test_demo.py)验证精确结果契约、专家调用顺序与上下文传递、回退行为、输入校验失败，以及仅使用标准库的隔离边界。

```bash
python3 -m unittest discover -s patterns/facade/sample/tests -v
```

这些结果只构成本地映射的 constructive 证据；独立的固定版本 Facade 案例才是 `confirmed correspondence` 生态主张的依据。

## 快速开始与验证

需要 Python 3.10+。从全新检出的仓库开始，在根目录按以下步骤执行；可编辑安装会先安装 PyYAML，再运行任何依赖目录解析的测试或校验器。

1. 创建并激活隔离环境。

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. 安装本仓库及其声明的依赖。

```bash
python -m pip install -e .
```

3. 运行示例、聚焦验证、完整测试和仓库完整性校验器。

```bash
python3 patterns/facade/sample/scripts/run_demo.py
python3 -m unittest discover -s patterns/facade/sample/tests -v
python3 -m unittest tests/test_docs.py -v
python3 -m unittest discover -s tests -v
python3 scripts/validate_repository.py
```

每个示例都可独立运行，只使用 Python 标准库，不需要网络或凭据；既可按上面的方式从仓库根目录运行，也可按各示例的本地说明在其目录中运行。

## 模式迁移准入协议

候选迁移必须用七项明确记录满足[完整协议](docs/pattern-transfer-protocol.md)：

```text
Source intent
Design forces
Participant correspondence
Consequences
Implementation evidence
Focused verification
Misuse discriminator
```

名称、文件名、注释或结构相似性本身不能确立迁移。这七项必须围绕同一个已声明的 Skillware Unit 与版本形成一致记录。

## 主张状态

[受控词表](docs/evidence-and-claim-status.md)使用下列含义：

| 状态 | 含义 |
| --- | --- |
| `constructive` | 仓库示例证明该映射可以被构造。 |
| `confirmed correspondence` | 固定版本的来源证据满足该参与者关系。 |
| `candidate correspondence` | 已有部分来源证据，但仍有参与者或行为未经验证。 |
| `unsupported` | 可用证据与源模式契约相矛盾，或未能满足该契约。 |
| `not observable` | 无法从可用制品评价所需关系。 |

这些状态是描述性的，而非评分。它们用于描述特定主张、关系、单元和版本，不对模式、项目、用途或软件质量进行排序。

## GoF-23 筛查

[可读矩阵](catalog/gof-23-screening.md)及其 [YAML 来源](catalog/gof-23-screening.yaml)记录 **23 GoF patterns screened**。每一行保留经典源意图、可能的 Skillware 载体、筛查结果与理由、误判风险，以及是否存在详细示例。

该筛查是有边界的分析清单。本版本有十个 GoF 条目具备详细实现，其余十三个保持为筛查记录。某一行提到可能载体，并不因此证明生态频率、适用性、质量、模式对应或具体实现。

## 仓库结构

```text
catalog/                 有来源的详细索引与 GoF-23 筛查
docs/                    本体边界、论文映射、协议、状态与局限
patterns/<pattern>/      单一扁平层级中可独立检查的模式记录
  definition*.md         英文与中文定义
  participant-map.yaml   源模式参与者到 Skillware 的对应
  correspondence.md      固定版本生态证据与主张边界
  sample/                根 Skill、输入、oracle、预期结果与测试
  misuse/                近似反例及决定性判别
scripts/                 仓库完整性校验器
tests/                   目录、文档、模式记录与示例契约
```

可以从[详细索引](catalog/pattern-index.md)开始，再进入 [`patterns/`](patterns/) 下任一同级目录。扁平布局避免把来源类别误解为新分类体系或实现排序。

## 科学局限

这些制品只证明有界的可构造性，并在明确标注时提供固定版本对应证据。它们不证明生态频率、自动质量优势、生产可靠性、安全性、有用性、比较性能或跨 Host 行为等价。确定性 oracle 验证声明的示例契约，但不复现模型解释，也不验证 Skillware 本体。

本仓库不主张发明既有模式。模式、实现维度、机制和生命周期阶段是不同分析轴，不蕴含先后排序。详见[完整局限说明](docs/limitations.md)。

## 引用

Haodi Fan、Zucong Lan，[《Skillware: A Software Ontology and Engineering Lifecycle for Persistent Behavioral Artifacts》](https://arxiv.org/abs/2607.18970)，arXiv:2607.18970 [cs.SE]，2026 年 7 月 21 日提交。

正式的软件与首选论文引用元数据见 [CITATION.cff](CITATION.cff)。[论文映射](docs/paper-map.md)提供主张级路径；写作版本 `1fc1dfd` 在其中作为不带链接的溯源标识保留。

## 贡献

贡献应保留既有来源、扁平模式布局、七项准入协议、受控状态、双语定义、独立示例、近似误用案例和聚焦测试。不能仅凭一个熟悉的模式名称就准入新目录。

完整的准入契约、验证要求及贡献许可边界见[贡献指南](CONTRIBUTING.md)。参与本项目须遵守 [Contributor Covenant 行为准则](CODE_OF_CONDUCT.md)。本仓库仍处于发布准备阶段，尚未达到公开发布就绪状态；CI、公开发布与 release 创建仍待 Task 20 完成。

## 许可证

许可边界按文件位置正式生效。所有 `patterns/*/sample/**`、`scripts/**`、`tests/**`、`.github/workflows/**` 和 `pyproject.toml` 均采用 [Apache License 2.0](LICENSE-CODE)。定义、模式元数据、参与者映射、对应记录、误用记录、catalog 文件、docs、READMEs 与治理文本均采用 [Creative Commons Attribution 4.0 International](LICENSE-DOCS)。

规范许可证文件保留其自身文本。链接的第三方制品仍遵循其上游许可证，本仓库不对其重新授权。完整边界见[贡献指南](CONTRIBUTING.md#license-boundary)。
