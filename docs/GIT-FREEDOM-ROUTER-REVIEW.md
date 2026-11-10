# Git Freedom Router — integration review

## Branch and scope

This candidate is based directly on `main`, not on `olpirt/stride-next`.
It introduces the Android Git bridge as an isolated integration candidate:

- `GitFreedomBridge.java`: local repository operations, selected-file commits, normal push, fetch, fast-forward-only pull, and draft PR creation
- `TokenVault.java`: encrypted token persistence
- `Api21WorkspaceTreeImporter.java`: Storage Access Framework workspace import, loaded reflectively
- JGit dependency pinned to the bridge's declared compatibility checkpoint

No existing Kotlin screen or application flow is wired to the bridge in this PR candidate. That keeps the router independently reviewable before UI integration.

## Validation boundary

The branch is intended to trigger the Android Java compile job. A successful compile validates source/dependency compatibility only; it does not prove runtime GitHub authentication, TLS negotiation across devices, filesystem-provider behavior, or end-to-end remote operations. Those require targeted tests and device/provider verification.

## Review findings to resolve before production use

1. `TokenVault` uses AES-CBC with a separate HMAC and PBKDF2-HMAC-SHA1. Review cryptographic policy and platform-provider compatibility before release.
2. The vault enforces a 12-character passphrase on save but only 8 characters on read; align or document this inconsistency.
3. `writeLocalFile` checks canonical path containment but is not gated by the configured feature-branch guard; review whether file editing should require the same branch authorization.
4. **Addressed in the current branch:** workspace import now scans the complete selected tree before copying and refuses the import if any file would overwrite an existing path. It requests read permission only and uses exclusive file creation as a second conflict check. A provider/read failure can still leave newly created files from earlier in the copy; whole-tree rollback is not yet implemented.
5. The shared bridge singleton retains the unlocked token in process memory. Review lifecycle and explicit lock behavior.
6. Remote transport is intentionally disabled below API 21. This is a compatibility restriction, not proof of successful TLS on every API 21+ device.

## Safety properties present in this candidate

- No force-push path is exposed.
- Pull is fast-forward-only.
- Push targets the configured feature branch.
- Mutating Git operations require the current branch to match the configured feature branch.
- Dirty working trees are rejected before branch switching or pull.
- Selected commit paths are checked against current changed paths.
- Workspace imports skip repository metadata and common build/editor folders.

## Explicitly not included

- No merge into `main`.
- No automatic UI integration.
- No force update, history rewrite, or automatic branch deletion.
- No claim of runtime/device validation until CI and device tests complete.


## TRUE NORTH importer hardening

The API 19+ workspace importer now:
- takes a read-only persistable URI grant;
- performs a full conflict scan before the first write;
- rejects the entire import if an existing file would be replaced;
- verifies canonical destination containment;
- uses exclusive file creation to catch conflicts introduced after preflight;
- deletes a newly created partial file if that file's stream copy fails.

**Remaining limitation:** the import is not a whole-tree transaction. If the document provider fails after several new files have been copied, those newly created files may remain. The importer does not overwrite pre-existing files, but an operator may need to review and clean up a partial import.
