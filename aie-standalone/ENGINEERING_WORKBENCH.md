# Æị AI Engineering Workbench — permission boundary

## Requested policy
- Scope: repository + authorized ERIA runtime files.
- Write mode: proposal first; explicit human approval for each write.
- \`main\` and \`master\` are protected. No force-push, history rewrite, deletion, or automatic commit/push.
- SQLite databases, WAL/SHM files, secrets, build outputs, \`.git\`, and symlink targets are outside this module's file access policy.
- Source rows and provenance are not editable through this workbench.

## Implemented in this change
\`engineering.py\` provides a local policy-enforcement core:
1. Enumerate tracked text-source files.
2. Read a tracked UTF-8 source file with SHA-256 and current branch.
3. Stage a replacement proposal in a private local approval directory.
4. Apply a proposal only after explicit approval, on the same non-protected branch, if the target hash has not changed.

It uses atomic replacement and preserves target file mode. Applying a proposal does not create a Git commit or push. Review the resulting diff and commit separately.

## Not connected yet
No AI model/provider, ERIA runtime file adapter, database reader, Pantheon adapter, GitHub write API, or UI endpoint is connected by this module. Live ERIA API contracts and runtime filesystem boundaries have not been verified. Do not expose this module over a network or claim UI write access until an authenticated local API wrapper and tests are added.

## Integration gate
Before wiring UI actions:
- Verify the Termux repository root and active branch from the running process.
- Define a strict allowlist for ERIA runtime configuration/code paths (never DB files).
- Add authenticated loopback-only HTTP routes for list/read/propose/approve.
- Add request size limits, CSRF/origin controls, audit records, and tests.
- Verify actual model-provider request/response schema; treat model output as an untrusted draft.
- Test path traversal, symlinks, protected branches, stale hashes, DB denial, and missing approval.
