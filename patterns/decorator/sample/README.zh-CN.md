# 合同审查增强

本独立样例使用一个严格的 `contract-review-v1` Component 接口实现
Decorator 模式。Base Contract Review 是 ConcreteComponent，Privacy Check
和 Citation Check 是可组合的 ConcreteDecorator，Compliance Check 是可选的第三个
ConcreteDecorator。所有参与者都仅接受
`text`，并仅返回 `summary` 和 `findings`。

运行：

```bash
python3 scripts/run_demo.py
python3 scripts/run_demo.py fixtures/valid/clean-contract.json
python3 scripts/run_demo.py --decorators citation-check,privacy-check
python3 scripts/run_demo.py --decorators privacy-check,citation-check,compliance-check
python3 -m unittest discover tests -v
```

默认组合是 `with_citation_check(with_privacy_check(base_review))`。基础组件
先返回结果，隐私检查再追加发现，引用检查最后追加。反转包装顺序只会
反转这两个增强项。每个边界都会校验并复制输入与输出，避免调用者、
被包装组件或装饰器通过共享引用互相修改数据。精确 `(type, message)`
身份使重复的同一装饰器具有幂等性。契约约束单个字符串和嵌套深度，但不对
`findings` 数量设定有限上限，以保持额外包装组合的可替换性。

演示仅使用 Python 标准库，不调用网络、模型或其他模式目录。JSON 夹具固定了
成功输出，以及 JSON 格式、重复成员、精确字段与类型、空白文本、孤立 Unicode
代理项和过深嵌套的稳定错误。聚焦程序测试覆盖非 UTF-8、非字符串映射 key、循环值、
parser 递归、单个字符串边界、超过 100 个发现与包装器、重复发现身份与幂等性，
以及别名隔离。Python 只是确定性预言机，不是法律、隐私、引用或合规审查系统，
也不证明 Agent Runtime 会解释 Behavioral Source。
