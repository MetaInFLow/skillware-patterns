# 费用审批规则

本独立示例把 Eric Evans 的领域驱动设计 Specification 模式用于费用审批；
它明确不是 GoF 模式。

默认可复用策略要求有票据、金额不超预算、金额不超过 1,000 个授权单位，且部门
不是 `restricted`。根行为位于 [`SKILL.md`](SKILL.md)，叶子行为位于
[`child-skills/`](child-skills/)，精确 Candidate 语义位于
[`references/expense-candidate-contract.md`](references/expense-candidate-contract.md)。

在本目录运行：

```bash
python3 scripts/run_demo.py
python3 -m unittest discover tests -v
```

可传入其他 Candidate 路径并选择轨迹模式：

```bash
python3 scripts/run_demo.py fixtures/valid/missing-receipt.json --evaluation short-circuit
```

策略满足时退出码为 0，合法 Candidate 被拒时为 1，输入无效时为 2。精确输出和
错误 fixture 位于 [`expected/`](expected/)。
