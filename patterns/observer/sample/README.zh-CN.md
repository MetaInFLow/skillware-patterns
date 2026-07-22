# 软件发布通知

这个独立 Observer 样例把一个有类型的软件发布事件发送给显式注册的审计、变更
日志和团队通知消费 Skill。

在本目录运行默认有效工作流：

```bash
python3 scripts/run_demo.py
```

运行发布前注销变更日志消费者的夹具：

```bash
python3 scripts/run_demo.py fixtures/valid/release-after-unregistration.json
```

运行聚焦测试：

```bash
python3 -m unittest discover tests -v
```

演示要求 Python 3.10 或更高版本，仅使用标准库，不需要网络或外部账户，也不
导入其他模式的共享代码。三个确定性更新函数模拟可独立检查的子 Skill；Python
不加载或解释 `SKILL.md`。

Subject 会执行显式注册操作，按注册顺序冻结本次交付列表，为每个 Observer 提供
隔离的事件副本，记录每次尝试，在失败后继续，并拒绝发布重入。通知不等于事务
完成，本样例也不执行隐式重试。
