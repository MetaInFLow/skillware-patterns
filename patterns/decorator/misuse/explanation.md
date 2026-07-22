# Why this is not Decorator

The Skill repeats the base review procedure instead of holding and invoking a
Component. Its required input adds `approval_token`, and its result adds
`privacy_approved`, so it no longer implements `contract-review-v1`. A caller
cannot substitute it where the base Component or another decorator is
expected. Fixes to the base logic can also diverge between copies.

Adding a responsibility after copied steps is insufficient. Decorator requires
a Decorator participant that references a Component, delegates through the
same operation, preserves the Component interface and failure semantics, and
adds bounded behavior around that delegation. The constructive Privacy Check
and Citation Check Skills do so without changing `text`, `summary`, or
`findings` fields.
