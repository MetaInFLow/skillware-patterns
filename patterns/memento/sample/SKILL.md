---
name: configuration-migration
description: Migrate a bounded JSON configuration with exact rollback. Use when a failed version change must restore the precise prior file.
intent: Coordinate opaque capture, atomic migration, validation, exact restoration, and checkpoint disposal without inspecting Originator state.
type: workflow
---

# Configuration Migration / 配置迁移回滚

## Trigger

Use this root Skill when a `service-configuration-v1` file must increment its
version atomically under
[`configuration-memento-v1`](references/configuration-memento-contract.md).
Preparation and conflict failures discard without restoration; write-attempt or post-write validation failures restore exact prior bytes.

## 中文触发约定

写入前的准备或冲突失败只丢弃检查点，不执行恢复；只有开始写入尝试后的失败或写后校验失败才
恢复精确原始字节。

## Participants

This root workflow is the **Caretaker**. The Configuration Originator child
Skill is **Originator**. The opaque exact-byte checkpoint is **Memento**.
Agent Host and Agent Runtime are execution context, not Memento participants.

## Agent mode

1. Give the target to the Originator. Reject missing, non-regular, symbolic
   link, oversized, non-UTF-8, invalid JSON, duplicate-member, unknown-field,
   wrong-type, non-finite, lone-surrogate, empty-endpoint, and version-boundary
   inputs before any write.
2. Capture exactly one opaque Memento before mutation. The Caretaker controls
   its timing and lifecycle but never reads or alters its state.
3. Ask the Originator to capability-check active ownership, target, and
   checksum, then prepare `version + 1` and validate that the target still
   equals the capture without writing. The Originator retains an immutable
   prepared payload privately; the Caretaker receives only an opaque one-use
   token. If preparation or conflict validation fails, checksum-validate and
   expire the checkpoint and token without restore, preserving current content.
4. After successful preparation, begin the write attempt. Apply captured mode
   on the open same-directory temporary file, fsync the file, atomically
   replace, fsync the directory, then reread and validate the exact bytes.
   A platform without descriptor-mode support may apply mode by temporary path
   while it remains open, still before the file fsync and rename.
5. On any write-attempt or post-write validation failure, conservatively ask
   the Originator to restore because replacement may have occurred. Re-raise
   the original failure only after exact restore verification. If restore or
   its owner, lifecycle, identity, target, or checksum admission check fails,
   report both the original and restoration failures and do not claim recovery.
   The complete migrated file may remain because restore was impossible; keep
   the checkpoint active for a trusted retry when its integrity permits one.
6. On successful validation, expire and discard the Memento **without** calling
   restore, but only after validating checksum, owner, active lifecycle, and
   object identity. Reject reused, foreign-Caretaker, integrity-corrupted, or
   cross-target checkpoints and tuple-style, forged, tampered, or reused
   preparation tokens.
7. Return only deterministic status, old version, new version, endpoint, and
   `restored: false`. Never include checkpoint contents or target-specific
   absolute paths.

## Demo mode and root harness

The standard-library Python oracle models Originator/Memento/Caretaker
collaboration; it does not interpret these Skill files. From `sample/`, run:

```bash
python3 scripts/run_demo.py
python3 -m unittest discover tests -v
```

The repository root harness automatically copies this record to an isolated
directory, runs the focused tests, and runs the default demo. The default demo
migrates a temporary fixture copy and does not modify the repository fixture.

## Ontology boundary

Behavioral Source -> Skill Artifact -> Skillware Unit -> Agent Host -> Agent Runtime -> Execution Trace -> Task Outcome

The Memento roles belong to the pattern mapping. Agent Host and Agent Runtime
remain execution context and are not reclassified as Memento participants.

## Limits

This is a single-cooperative-writer model. Atomic replacement prevents partial
file content but is not a lock and cannot promise identical crash durability on
every filesystem. The no-write preparation check cannot close a race with an
uncooperative writer between validation and replacement. Originator privacy and
Memento opacity are trusted-code
contract boundaries, not security isolation: in-process reflection,
monkeypatching, direct file access, and memory inspection can bypass them. Mode
preservation does not cover ACLs, ownership, extended attributes, or labels.

## Anti-pattern

A workflow that logs before/after semantic values but has no exact restoration
path is not Memento. See `../misuse/SKILL.md`.
