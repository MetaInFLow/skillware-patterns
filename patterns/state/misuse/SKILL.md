---
name: conditional-vendor-phases
description: Choose vendor steps from conditional text. Use only to demonstrate phase labels without persisted State ownership or recovery.
intent: Show a State near miss that branches on conversational phase words without a durable record, ConcreteStates, or restart behavior.
type: workflow
---

# Conditional Vendor Phases

If the conversation sounds like a new vendor, ask for verification details. If
it mentions that verification happened, ask someone to approve. If approval is
mentioned, activate the vendor.

Treat the most recent phase word as current. Keep no state record, define no
schema or revision, and let this root prompt choose every branch. There are no
separately owned State or ConcreteState operations. After restart, infer the
phase again from available conversation. If an impossible action is requested,
respond conversationally rather than returning a stable error or preserving a
known record.
