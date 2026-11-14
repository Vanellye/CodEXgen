# ERIA PONS Exact-Scope Approval Screen

## Termux interface
The Qualitative Storage panel includes a PONS human-authorization screen:
1. Load the existing quality proposals.
2. Select one proposal and create a PONS request.
3. Review the complete scope: repository root, branch, HEAD commit, report identity, target paths, SHA-256 fingerprints, and prohibited adjacent actions.
4. Type the exact phrase displayed for that scope and confirm.

The confirmation is bound to the canonical JSON scope digest. The server independently verifies the current Git branch and HEAD and re-hashes every target file before recording a grant. Any mismatch, unavailable Git provenance, missing field, or incorrect phrase leaves the request on HOLD.

## Storage
PONS requests and grants are stored separately at
`~/.eria/qualitative/pons_approvals.sqlite3`. Both tables are append-only and have
SQLite triggers that reject update/delete operations. Existing ERIA source/chat
SQLite data and the qualitative report/finding history are not migrated or replaced.

## Authorization semantics
The first grant is `repository.patch.prepare`: it permits patch preparation only. A second human confirmation grants `repository.source.modify` for the SHA-256 of the complete unified diff, bound to the parent grant, exact target paths, branch, HEAD, and original source fingerprints. The required phrase is `AUTHORIZE PATCH <12 hex characters>`. Patch requests and grants are append-only. Any changed patch byte, out-of-scope path, changed branch/HEAD, or changed source fingerprint fails closed.

## Hard boundary
This milestone records authorization only. It does not implement a patch executor,
write repository source files, create commits, push, merge, deploy, or mutate source
database records. A future executor must call `verify_patch_grant` with the exact approved patch bytes immediately before any write, revalidate source state, and remain restricted to the approved paths. No executor is enabled in this milestone. The local
Termux screen is a human-confirmation interface, not an OS identity provider or
cryptographic signature service.
