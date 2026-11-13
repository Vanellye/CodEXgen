# ERIA Filesystem for Understanding

## Status

Initial read-only implementation on `feature/eria-filesystem-understanding`.
This is a bounded local inventory and preview capability, not an autonomous agent,
a filesystem mount, a permission broker, or an execution environment.

## Purpose

Give ERIA a factual, reproducible view of files that a caller is explicitly
authorized to inspect. The inventory can support source comprehension, code
review, provenance analysis, and later adapters without granting write authority.

## Contract

- **Explicit scope:** the caller supplies one existing directory. Android UI
  integrations must obtain access through a user-mediated Storage Access Framework
  selection or use app-private storage.
- **Read-only:** no create, update, rename, delete, chmod, execute, or dispatch API.
- **Bounded traversal:** configurable depth, file-count, per-file byte, aggregate
  byte, and preview-character limits.
- **No symlink traversal:** symbolic-link roots and children are rejected/skipped;
  canonical paths must remain under the selected root.
- **Sensitive-path exclusion:** credential stores, environment files, private-key
  formats, build output, dependency caches, and common secret directories are
  excluded from content inspection.
- **Content minimization:** only an allowlist of text/source extensions receives a
  preview. Binary files receive metadata and a digest only. Credential-like strings
  are redacted in previews.
- **Provenance:** each inspected file record carries its root-relative path, size,
  extension, and SHA-256 digest when bytes were read.
- **No persistence by default:** results exist only in the caller's process unless a
  separately reviewed persistence adapter is added.

## Output interpretation

A digest identifies the exact bytes read; it does not establish authorship,
integrity of the wider system, trustworthiness, or correctness. A preview is
truncated and redacted, so it is not a complete representation of the file.
Excluded, oversized, unreadable, or unrecognized content must remain visibly
unknown rather than being described as understood.

## Integration sequence

1. Keep this capability isolated behind a read-only API.
2. Add an Android SAF adapter only after UI consent and URI-grant lifecycle tests.
3. Connect ERIA correction-lineage and multi-omics review flows through explicit
   adapters; do not let the inventory itself trigger ingestion or repair.
4. Require independent tests and human review before adding persistent indexes,
   file writes, automatic scanning, or background execution.

## Safety boundary

Filesystem discovery is not authorization to interpret sensitive personal data,
upload content, execute code, alter source files, or publish findings. Any such
operation requires a separate purpose, explicit permission, data-minimization
review, and auditable approval.
