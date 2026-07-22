# 部署协调

这个独立 Mediator 样例让构建、安全、文档和审批 Colleague 只通过一个 Deployment
Coordinator 协作。每个参与者按固定顺序被寻址一次，并只向 Mediator 报告。
ConcreteMediator 隔离可调用专长的失败，应用全员通过政策，并在不吸收专长工作的前提下
返回确定性的发布或阻止决定。

运行默认的就绪演示：

```bash
python3 scripts/run_demo.py
```

运行安全失败夹具和聚焦测试：

```bash
python3 scripts/run_demo.py fixtures/valid/security-failure.json
python3 -m unittest discover tests -v
```

样例需要 Python 3.10 或更高版本，只使用标准库，不需要网络或账户，不导入其他模式代码，
也不修改夹具。参与者绑定与同伴隔离是可信代码契约，不是安全沙箱。
