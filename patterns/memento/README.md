# 备忘录模式（Memento）

> **人话：** 先保存一份由状态拥有者生成的快照，失败时按原样恢复，管理者无需知道内部细节。

## 1. 先看场景

配置迁移可能在写文件后失败。系统需要恢复迁移前的精确内容、权限和版本信息，迁移协调者不应自己重建配置。

## 2. 先看完整 Skill

**Mock Skill：** 我们构造的 Skill 叫 `configuration-migration`：

```text
patterns/memento/sample/
├── SKILL.md                                  # migration coordinator
├── child-skills/
│   ├── configuration-originator/SKILL.md       # owns state
│   └── migration-caretaker/SKILL.md            # holds checkpoint
├── references/configuration-memento-contract.md
├── scripts/run_demo.py
└── tests/test_demo.py
```

关键行为：

```markdown
<!-- Caretaker 只拿到不透明快照，不能读取配置内部结构。 -->
1. ask the Originator for one opaque snapshot
2. let the Caretaker hold the snapshot
3. attempt the migration
4. restore on failure, discard on verified success
```

## 3. 这个模式解决了什么

### 没有 Memento

```text
caretaker reads old_config
caretaker writes new_config
caretaker reconstructs old_config after failure
```

协调者知道太多内部字段，恢复过程可能丢失字节、权限或所有权信息。

### 使用 Memento

```text
Originator -> opaque snapshot -> Caretaker
                         failure -> restore
                         success -> discard
```

状态的创建和恢复仍由 Originator 负责，Caretaker 只管理快照生命周期。

## 4. 市面上的 Skill 案例

**Case Skill：** [Microsoft SkillOpt staging](https://github.com/microsoft/SkillOpt/blob/b860a5cf88ce75e2bd02ca981ac21fb28cffba83/skillopt_sleep/staging.py)。

它体现 Memento 思想的地方：候选配置被采用前，staging 流程先保存备份。

```text
staging configuration -> backup manifest -> adopt candidate
```

公开路径支持“采用前备份”的候选对应关系，完整的恢复协议没有在该固定文件中暴露。

## 5. 这个例子对应哪些角色

| Memento 角色 | Skillware 中的对应物 |
| --- | --- |
| Originator | configuration-originator Skill |
| Memento | 不透明的 `configuration-memento-v1` 快照 |
| Caretaker | 根迁移 Skill 和 migration-caretaker |

## 6. 什么时候用

适合：需要恢复精确的旧状态；状态拥有者希望隐藏内部结构；快照需要明确的捕获、恢复和销毁规则。

不适合：数据库事务已经提供完整回滚；状态本身就是简单公开值；重试操作就足以解决失败。

## 7. 运行

```bash
python3 sample/scripts/run_demo.py --fail
python3 -m unittest discover -s sample/tests -v
```

继续阅读：[完整样例](sample/)、[角色映射](participant-map.yaml)、[模式定义](definition.md)、[反例](misuse/explanation.md)。

## 8. 边界

本地样例验证了精确快照、回滚和快照销毁。SkillOpt 只支持候选级对应关系，本地样例不代表分布式事务保证。
