# 生产事故响应

这个独立 Facade 样例通过一个根 Skill 接收 `service` 和 `signal`。它协调可独立
检查的诊断、影响评估与沟通 Skill，但只返回 `summary`、`impact`、`actions` 和
`communication`。

在本目录运行已知信号样例：

```bash
python3 scripts/run_demo.py
```

运行未知信号样例：

```bash
python3 scripts/run_demo.py fixtures/invalid/unknown-signal.json
```

运行聚焦测试：

```bash
python3 -m unittest discover tests -v
```

演示要求 Python 3.10 或更高版本，仅使用标准库，不需要网络、凭据或其他模式
样例。畸形请求会返回清晰的校验错误，并以非零状态退出。
