# Why this is not Specification

A single opaque eligibility function may return the same boolean for one case,
but its rules have no independent identity. Callers cannot reuse the receipt
rule, combine department exclusion with another policy, inspect a structured
failure, or test one domain rule through the common Specification interface.

A valid DDD Specification names each rule, evaluates one bounded Candidate
without side effects, and composes And, Or, and Not objects that retain the
same boolean contract.

不透明单体函数缺少独立的 Specification 身份、组合边界与结构化解释，
因此不是规约模式。
