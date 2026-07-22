# 配置迁移回滚

这个独立 Memento 样例通过原子替换增加有界 JSON 配置的版本。Originator 将精确
原始字节和可移植权限捕获到不透明 Memento。写入前准备或冲突错误会直接丢弃检查点，
不恢复也不覆盖更新内容。一旦开始写入尝试，Caretaker 对失败进行保守恢复；成功时则丢弃
检查点而不调用恢复。

Originator 私有保存不可变准备载荷，只返回已封印的不透明一次性令牌。提交或丢弃之前，
Caretaker 会校验检查点的校验和、所有者、活跃生命周期和对象标识。
回滚时，这些准入检查位于恢复错误边界内。准入失败会保留原始迁移错误与恢复错误；由于不能
安全应用检查点，完整新版文件可能保留。

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
文件系统都具有相同崩溃语义。权限在打开的临时文件描述符上设置，位于文件同步和改名之前；
如平台不支持描述符权限，则在文件仍打开时使用临时路径回退。
