# 投资备忘录生成

这个独立 Composite 样例把市场、财务、竞争和风险分析 Skill 组合为一份投资
备忘录。原子章节与根备忘录使用同一个 `memo-section-v1` 结果契约。

在本目录运行默认有效工作流：

```bash
python3 scripts/run_demo.py
```

运行指定的工作流夹具：

```bash
python3 scripts/run_demo.py fixtures/valid/investment-memo.json
```

运行聚焦测试：

```bash
python3 -m unittest discover tests -v
```

演示要求 Python 3.10 或更高版本，仅使用标准库，不需要网络，也不导入其他模式
的共享代码。它递归校验序列化的节点引用，保持子节点声明顺序，并且不会修改解析
后的工作流。无效 schema、种类、结果契约、重复 ID、缺失节点、包含子节点的 Leaf
和循环引用都会以确定的错误消息失败。

JSON 工作流提供节点注册表和子节点引用；目录结构本身不是 Composite 关系。统一
的 Component 结果和经过校验的部分-整体遍历才构成该关系。
