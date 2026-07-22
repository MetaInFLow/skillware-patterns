# 供应商准入流程

这个独立 State 样例让供应商依次经过持久化的 draft、verified、approved 和
activated 状态。每个 ConcreteState 拥有自身允许的动作和后继状态；Context 在
委托前重载并校验状态。

在本目录运行默认完整工作流：

```bash
python3 scripts/run_demo.py
```

运行重启恢复夹具：

```bash
python3 scripts/run_demo.py fixtures/valid/recover-approved.json
```

运行聚焦测试：

```bash
python3 -m unittest discover tests -v
```

演示要求 Python 3.10 或更高版本，只使用标准库，不需要网络或外部账户，也不导入
其他模式的共享代码。四个 Python 类模拟可独立检查的 ConcreteState Skill；
Python 不加载或解释 `SKILL.md`。

写入采用同目录原子替换，而且只有替换成功后内存才会前进。本样例只支持单写入者；
原子替换不能代替跨进程并发控制。首次构造是显式 bootstrap 边界；此后若已知状态
记录被删除，将返回损坏错误，绝不会静默重建 `draft`。
