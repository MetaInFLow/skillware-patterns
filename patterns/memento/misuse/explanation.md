# Why this is not Memento

The misuse records semantic changes only after parsing and overwriting the
configuration. A log can say that `version` changed from 1 to 2, but it cannot
recover original whitespace, key order, final newline, encoding bytes,
permissions, or unlogged fields. It also owns no atomic restore operation.

Memento requires an Originator-created state capture and a Caretaker-managed
path that returns that exact state to the Originator. Logging without exact
restoration is audit history, not Memento.
