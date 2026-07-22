---
name: logged-configuration-migration
description: Log configuration changes without preserving restorable state. Use only to study why audit logs are not Mementos.
intent: Demonstrate that change descriptions cannot restore exact prior bytes, metadata, or a failed overwrite.
type: component
---

# Logged Configuration Migration Misuse

Read `version`, write the incremented JSON, and append a log entry containing
the old and new semantic values. If validation fails, report the log and ask an
operator to reconstruct the file.

This artifact intentionally has no Originator-owned snapshot operation, opaque
Memento, or Caretaker restore path. Do not use it for real migration.
