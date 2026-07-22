---
name: expense-department
description: Match an expense department to a configured value. Use as a named leaf or negated leaf in a composable approval policy.
intent: Compare one bounded NFC-normalized department with an immutable expected department using exact case-sensitive equality.
type: component
---

# Department / 部门

Act as immutable `Department(expected)`. Validate and NFC-normalize the
non-blank expected value at construction. Require one admitted department under
the root contract and use exact case-sensitive equality. Do not mutate the
Candidate. Compose `~Department("restricted")` to exclude that department.

作为不可变 `Department(expected)` 规约。构造时校验并进行 NFC 规范化，
对已校验部门名进行区分大小写的精确比较。用 `~Department("restricted")`
表示排除该部门。
