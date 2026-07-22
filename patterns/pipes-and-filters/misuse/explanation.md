# Why this is not Pipes and Filters

A prose sequence or one monolithic function does not create independent
Filters. A stage cannot be addressed, replaced, or tested through the common
record contract, and hidden shared state bypasses the Pipe. Failures cannot be
attributed to a validated stage boundary.

A valid pipeline owns topology outside the Filters, transfers a complete
versioned record through explicit Pipes, and permits one compatible Filter to
be replaced without rewriting its neighbors.

单体函数或仅有文字顺序的流程缺少独立 Filter 与显式 Pipe，因此不是管道-过滤器模式。
