# 配置迁移回滚

这个独立 Memento 样例通过原子替换增加有界 JSON 配置的版本。Originator 将精确
原始字节和可移植权限捕获到不透明 Memento；Caretaker 在捕获后任何失败时请求恢复，
成功时丢弃检查点而不调用恢复。

运行不修改夹具的确定性默认演示：

```bash
python3 scripts/run_demo.py
```

就地迁移指定文件，或演示回滚路径：

```bash
python3 scripts/run_demo.py path/to/service.json
python3 scripts/run_demo.py path/to/service.json --fail
```

运行聚焦测试：

```bash
python3 -m unittest discover tests -v
```

样例需要 Python 3.10 或更高版本，只使用标准库，无需网络或账户，也不导入其他模式的共享
代码。它假设单一可信协作写入者；原子替换可防止局部文件内容，但不提供锁，也不保证所有
文件系统都具有相同崩溃语义。
