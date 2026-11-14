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
The PONS capability is `repository.source.modify`. A successful human confirmation
returns `REVIEW_READY` for that exact scope only. The grant is not a blanket repository
permission. A changed branch, commit, or target fingerprint invalidates the request;
prepare a new proposal and request instead of expanding the old grant.

## Hard boundary
This milestone records authorization only. It does not implement a patch executor,
write repository source files, create commits, push, merge, deploy, or mutate source
database records. A later executor must consume and revalidate the exact grant and
must remain restricted to the listed paths and separately reviewed patch. The local
Termux screen is a human-confirmation interface, not an OS identity provider or
cryptographic signature service.
