# ERIA Filesystem Generation — Proposal

**Status:** Design-only workstream; no generator or filesystem mutation is enabled.
**Related concept:** [STAR — Steady TAG Algo Rhythm](STAR-STEADY-TAG-ALGO-RHYTHM.md)

## Purpose
Specify a deterministic, reviewable way to generate a directory tree from an explicit manifest. This is distinct from filesystem understanding/inventory: generation creates proposed outputs; understanding observes an explicitly supplied root. Neither capability grants access to arbitrary device storage.

## Manifest contract
A future implementation should accept a versioned manifest containing a caller-supplied output root; relative directory and file paths; file contents or content references; declared encoding and line-ending policy; expected byte lengths and SHA-256 hashes where applicable; and an explicit overwrite policy defaulting to **deny**.

STAR glyph tokens may appear as ordinary UTF-8 metadata or filenames only after normal path validation. They are never executable instructions.

## Required validation
Reject a plan before writing if it contains:
- absolute paths, drive prefixes, NUL bytes, or `..` traversal segments;
- duplicate or case-colliding destinations where the target filesystem is case-insensitive;
- symlink traversal or a destination escaping the approved root;
- unbounded file counts, file sizes, or aggregate output size;
- ambiguous encodings or invalid UTF-8 where UTF-8 is required; or
- overwrite/delete requests without separate, explicit authorization.

## Execution boundary
The intended lifecycle is **manifest → validation → deterministic preview → explicit approval of target root and plan hash → staging → verification → publish**.

The initial implementation should be plan-only. A later writer adapter must be a separate reviewed component with bounded quotas, staging isolation, no-follow path handling, collision checks, and a tested recovery path. It must not run merely because a manifest was discovered or a trigger fired.

## Provenance and recovery
Record the manifest hash, source references, generator version, target root, planned paths, output hashes, authorization scope, and result. Keep source artifacts distinct from generated derivatives. On failure, report exactly which staging artifacts were created; never perform broad cleanup outside the run-owned staging directory.

## Acceptance criteria for a future implementation
- Identical manifest and generator version produce identical plans and hashes.
- Invalid paths and quota violations fail before any write.
- Preview mode performs no filesystem mutation.
- Default behavior never overwrites existing files.
- Tests prove root containment, symlink rejection, quota enforcement, and recovery.
- No device-wide scan, external dispatch, or hardware action is introduced.
