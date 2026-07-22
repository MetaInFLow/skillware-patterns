---
name: expense-authorized-amount
description: Check an expense against a configured authority limit. Use as a named leaf in a composable expense approval policy.
intent: Return true only when bounded admitted integer amount does not exceed the immutable authorized maximum.
type: component
---

# Authorized Amount / 授权额度

Act as immutable `AuthorizedAmount(maximum)`. Validate `maximum` as a
non-negative integer no greater than 1,000,000,000 at construction. Require an
admitted `amount` under the same bounds and return `amount <= maximum`. Do not
round, convert, mutate, or consult hidden authority state.

作为不可变 `AuthorizedAmount(maximum)` 规约。构造时校验有界非负整数上限，
仅在已校验 `amount <= maximum` 时返回真，不依赖隐式授权状态。
