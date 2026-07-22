# 投资备忘录生成

这个独立 Composite 样例通过调用市场、财务、竞争和风险 Leaf 来组装一份投资
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
的共享代码。四个确定性执行器以子 Skill 路径为键，根据夹具输入计算 Leaf 结果；
Python 不解释 `SKILL.md`。构建器支持依赖注入，校验每个返回记录，保持调用顺序，
并且不会修改工作流。

在任何 Leaf 执行前，完整注册表校验会拒绝缺失引用、重复子节点、共享子节点 DAG、
拥有父节点的根、不可达节点，以及断开组件中的循环。

JSON 工作流提供节点注册表和子节点引用；目录结构本身不是 Composite 关系。统一
的 Component 结果和经过校验的部分-整体遍历才构成该关系。
