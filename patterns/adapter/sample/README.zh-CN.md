# 多问题追踪器发布

这个独立 Adapter 样例接收规范问题、`github`、`jira` 或 `linear` 目标，以及
精确的目标位置上下文。每个轻量绑定生成有官方文档依据的 REST 或 GraphQL 请求
描述符，同时保留规范身份和严重性。

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
样例。未知目标和畸形规范问题会返回清晰的校验错误，并以非零状态退出。额外的
请求字段或问题字段会被拒绝，而不是被忽略。

输出只是离线描述符。演示不会发送请求，也不声称 GitHub、Jira 或 Linear 已接受
该请求。官方供应商文档链接见 `references/tracker-contracts.md`。
