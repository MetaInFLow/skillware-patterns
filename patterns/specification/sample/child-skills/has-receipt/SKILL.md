---
name: expense-has-receipt
description: Check the exact receipt boolean for an expense. Use as a named leaf in a composable expense approval policy.
intent: Return true only when the admitted Candidate has receipt equal to the boolean true.
type: component
---

# Has Receipt / 已附票据

Act as the immutable `HasReceipt` Specification. Require exactly the admitted
boolean field `receipt`; return true only for `True`. Do not coerce `1`, strings,
or missing data. Emit the observed boolean in explanations and do not mutate the
Candidate.

作为不可变 `HasReceipt` 规约，仅当已校验的 `receipt` 是布尔真值时返回真，
不进行类型强制转换，不修改 Candidate。
