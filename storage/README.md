# ERIA compiled storage

This directory holds derived, compiled copies produced only when an operator
explicitly invokes Æị's compile command or the local interface's
"Compile copy to storage" action.

## Layout

- `compiled/`: JSON snapshots of Æị inspection results.
- `manifests/`: provenance manifests with source and artifact SHA-256 digests.

A compiled snapshot is a structured interpretation, not a byte-for-byte source
backup. The source file remains at its original path and is never modified,
moved, or deleted by this feature. SQLite sources are inspected in read-only
mode. Artifacts and derived interpretations remain NON_AUTHORITATIVE.

Each compile creates a unique artifact; existing artifacts are never replaced.
Credential-like paths are refused. Runtime artifact files are excluded from Git
by the local .gitignore so private or changing data is not accidentally
committed. Back up this directory separately if compiled records need durable
retention.
