# 风险感知代码审查

本独立样例用一个代码审查 Context、一个严格的请求/结果 Strategy 契约和两个可互换
ConcreteStrategy 实现 Strategy 模式。Fast Scan 执行高信号规则，Deep Review
增加上下文规则。安全敏感请求或文件数达到四个时选择 Deep Review，否则选择 Fast
Scan。

运行：

```bash
python3 scripts/run_demo.py
python3 scripts/run_demo.py fixtures/valid/security-sensitive-review.json
python3 scripts/run_demo.py fixtures/valid/low-risk-review.json --strategy deep-review
python3 -m unittest discover tests -v
```

演示只使用 Python 标准库，不发起网络或模型调用。两个策略都可注入或直接寻址，每个
结果都按同一严格富契约校验。JSON 对象成员顺序不影响语义，输出字段和发现顺序会被
规范化。夹具固定了成功输出，以及 JSON 格式或重复成员、schema、类型、边界、
不安全路径、孤立 Unicode 代理项和未知策略标识的稳定错误。

模块级 `review({"files": int, "security_sensitive": bool})` 另行保留精简计划 API。
安全敏感或 `files > 5` 时选择 Deep Review，并严格返回 `strategy`、`findings`、
`confidence`。注入到富接口的自定义策略可以使用其他过程；Context 只强制公共结构、
确定性发现顺序和唯一身份，不要求使用内置词法规则。

Python 只是参与者协作的确定性预言机，不会激活或解释自然语言 Skill；其中的小型
词法规则集也不是生产级安全审查系统。
