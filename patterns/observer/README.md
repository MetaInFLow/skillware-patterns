# 观察者模式（Observer）

> **人话：** 一个 Skill 发布事件，多个已经注册的 Skill 各自接收并处理。

## 1. 先看场景

软件发布成功后，审计、变更日志和团队通知都需要同一份发布信息。发布 Skill 不应承担每个消费者的具体工作，也不应因为一个消费者失败就丢掉其他通知。

## 2. 先看完整 Skill

**Mock Skill：** 我们构造的 Skill 叫 `software-release-notification`：

```text
patterns/observer/sample/
├── SKILL.md                                  # Subject
├── child-skills/
│   ├── audit/SKILL.md                         # Observer 1
│   ├── changelog/SKILL.md                     # Observer 2
│   └── team-notification/SKILL.md             # Observer 3
├── references/release-event-contract.md
├── scripts/run_demo.py
└── tests/test_demo.py
```

关键行为：

```markdown
<!-- Subject 管理注册，Observer 只处理收到的事件。 -->
1. validate `release.published.v1`
2. freeze the active registration order
3. invoke each registered consumer once
4. record each receipt and isolate consumer failures
```

## 3. 这个模式解决了什么

| 没有 Observer | 使用 Observer |
| --- | --- |
| `publish_release()`<br>`  call audit()`<br>`  call changelog()`<br>`  call team_notification()`<br><br>增加消费者需要修改发布 Skill，失败处理也被写死。 | `release.published.v1`<br>`  -> audit Observer`<br>`  -> changelog Observer`<br>`  -> team-notification Observer`<br><br>发布 Skill 维护事件和订阅关系，消费者独立维护行为。 |

**变化点：** 发布者只发布事件，消费者通过注册关系接收事件。

## 4. 市面上的 Skill 案例

| 上游 Case Skill | 本地 Mock Skill |
| --- | --- |
| [ECC lifecycle hooks](https://github.com/affaan-m/ECC/blob/2bc924faf2f8e893bfe0af86b1931283693c30ae/hooks/hooks.json)<br>生命周期事件被路由给观察 Skill。<br>`candidate correspondence` | [`software-release-notification`](sample/SKILL.md)<br>发布事件通知 audit、changelog、team-notification。<br>`constructive` |

**Case Skill：** [Everything Claude Code lifecycle hooks](https://github.com/affaan-m/ECC/blob/2bc924faf2f8e893bfe0af86b1931283693c30ae/hooks/hooks.json) 和 [continuous-learning observer hook](https://github.com/affaan-m/ECC/blob/2bc924faf2f8e893bfe0af86b1931283693c30ae/skills/continuous-learning-v2/hooks/observe.sh)。

它体现 Observer 思想的地方：Host 生命周期事件被路由给独立的观察 Skill。

```text
Host lifecycle event -> hook router -> observation Skill
```

公开文件显示了事件路由，完整的注册、注销和送达语义仍记录为 `candidate correspondence`。

## 5. 这个例子对应哪些角色

| Observer 角色 | Skillware 中的对应物 |
| --- | --- |
| Subject | 根 release-notification Skill |
| Observer | audit、changelog、team-notification |
| ConcreteSubject | 发布事件来源 |
| ConcreteObserver | 每个注册消费者的具体实现 |

## 6. 什么时候用

适合：消费者可以独立增加或移除；一个事件需要通知多个 Skill；需要单独记录每个消费者的结果。

不适合：只有一个固定接收者；所有步骤必须在同一事务里完成；事件订阅会让流程比直接调用更难理解。

## 7. 运行

```bash
python3 sample/scripts/run_demo.py
python3 -m unittest discover -s sample/tests -v
```

继续阅读：[完整样例](sample/)、[角色映射](participant-map.yaml)、[模式定义](definition.md)、[反例](misuse/explanation.md)。

## 8. 边界

本地样例验证了注册、注销、送达回执和失败隔离。ECC 的公开路径只支持候选级对应关系，不代表生产级消息投递保证。
