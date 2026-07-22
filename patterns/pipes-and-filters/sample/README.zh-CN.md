# 客服工单分流

本独立示例依次运行规范化、脱敏、分类、优先级和回复草拟过滤器。每个阶段都通过会
校验并深拷贝的 Pipe 接受和返回 `support-ticket.v1`。

```bash
python3 scripts/run_demo.py
python3 -m unittest discover tests -v
```

默认输入位于 `fixtures/valid/urgent-access.json`，精确输出与错误位于 `expected/`。
