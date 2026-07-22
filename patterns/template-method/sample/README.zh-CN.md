# 企业 RFP 响应

本独立样例用一个不可变的五阶段 RFP 骨架与两个有界领域
ConcreteClass 构造 Template Method。

在本目录中使用 Python 3.10 或更高版本运行：

```bash
python3 scripts/run_demo.py
python3 scripts/run_demo.py fixtures/valid/finance-rfp.json
python3 -m unittest discover tests -v
```

默认输出与 `expected/healthcare-rfp-result.json` 逐字节一致。
无效夹具以状态码 2 返回对应的稳定错误。演示只使用 Python
标准库，不访问网络，也不导入其他模式。

测试验证 `run_rfp("healthcare")` 字面 API、固定顺序、钩子仅调用
一次、失败后立即停止、共享钩子契约、有界替换、必经阶段不可
重写、输入输出隔离、确定性、重复 JSON 成员拒绝、Unicode 与深度/类型
边界。

领域内容只用于展示模式，不是专业 RFP 或合规意见。
