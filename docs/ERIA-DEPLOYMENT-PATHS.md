# ERIA deployment paths and release gates

This document separates verified build artifacts from installation and production
deployment. A successful build is not proof that an application is installed,
reachable, secure, or operational.

## 1. GitHub verification artifacts

Workflow: `.github/workflows/eria-verify-package.yml`

For changes to the ERIA source paths on `god/heritage-lineage`, the workflow:

- Compiles Python source files without executing application code or tests.
- Parses the GOD JSON schemas.
- Checks Termux shell-script syntax.
- Builds the Android debug APK with Gradle.
- Packages the Termux/Python source tree.
- Emits SHA-256 checksums and a manifest bound to the exact commit.
- Uploads the APK, source bundle, and integrity manifest as a GitHub Actions artifact.

This is an artifact/staging path. It does not install on a device, publish a store
release, merge branches, or deploy to a server. Tests remain intentionally
unexecuted while the GOD parent-validation test pause is in force.

## 2. Android installation path

The workflow produces `eria-debug-unsigned.apk`. It is a debug build for
controlled installation and evaluation, not a signed production release.

Before production distribution, ERIA needs a reviewed release build, externally
managed signing credentials, signing/verification checks, versioning, release
notes, and an explicitly approved distribution destination. Signing secrets
must not be committed to this repository or embedded in workflow source.

## 3. Termux local installation path

The workflow packages the repository's `tools/`, `termux/`, `pantheon/`,
`shared/`, `GOD/`, and `docs/` trees into `eria-termux-source.tar.gz`.

The documented local start command remains:

```sh
python tools/eria_conversation_server.py . --port 8765
```

The service is designed to bind to loopback. It is a local-device runtime path,
not a remotely reachable server deployment. Install and start it on the user's
Termux device after reviewing the artifact and its checksum.

## 4. Server deployment path — not yet configured

No production host, deployment destination, domain, TLS termination, service
manager, health-check URL, rollback mechanism, or approved deployment
credential is configured by this repository change.

A future server adapter must use a dedicated protected GitHub Environment,
least-privilege credentials, an explicit target and immutable commit, preflight
checks, health verification, audit output, and rollback instructions. It must
not accept arbitrary shell commands or bypass host permissions.

## 5. Integration and release gates

- `main` remains unchanged; this workflow is scoped to
  `god/heritage-lineage`.
- The branch's broad divergence from `main` must be reviewed before integration.
- No PR is automatically merged.
- No production signing key or server credential is provisioned here.
- A green artifact workflow does not establish runtime correctness or production
  readiness.
- Missing target configuration, failed verification, or missing authorization
  means HOLD.

## 6. Evidence to retain

For each candidate release, retain the source commit SHA, workflow run URL,
artifact names, SHA-256 manifest, validation results, reviewer/approval record,
target environment, deployment result, health-check evidence, and rollback
result if used.
