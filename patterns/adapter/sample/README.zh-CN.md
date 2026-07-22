# 多问题追踪器发布

这个独立 Adapter 样例接收包含 `id`、`title`、`description` 与 `severity` 的
规范问题，以及 `github`、`jira` 或 `linear` 目标。每个轻量绑定返回所选追踪器
的精确载荷，同时保留规范身份和含义。

在本目录运行默认 GitHub 样例：

```bash
python3 scripts/run_demo.py
```

运行另一个样例：

```bash
python3 scripts/run_demo.py fixtures/valid/linear.json
```

运行聚焦测试：

```bash
python3 -m unittest discover tests -v
```

演示要求 Python 3.10 或更高版本，仅使用标准库，不需要网络、凭据或其他模式
样例。未知目标和畸形规范问题会返回清晰的校验错误，并以非零状态退出。
