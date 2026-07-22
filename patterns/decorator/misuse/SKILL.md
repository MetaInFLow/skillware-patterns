---
name: copied-contract-review-enhancement
description: Copy base review logic and return a changed contract. Use only to demonstrate an implementation that is not Decorator.
intent: Show a Decorator near miss that replaces rather than wraps the Component and requires a new output field.
type: workflow
---

# Copied Contract Review Enhancement

Copy the Base Contract Review procedure into this Skill. Run the copied base
steps, then inspect email addresses. Accept `{text, approval_token}` and return
`{summary, findings, privacy_approved}`.

Do not invoke a wrapped Component. Require `approval_token` before review and
make `privacy_approved` mandatory for every caller. Future fixes to Base
Contract Review must be copied here separately.
