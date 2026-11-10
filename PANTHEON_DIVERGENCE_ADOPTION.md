# Pantheon Divergence Garden — Automatic Adoption

Status: opt-in, fail-closed adoption proposal; no automatic adoption is active until this workflow is merged into the default branch.

## Warden Principle

This workflow is governed by [PANTHEON_WARDEN_PRINCIPLE.md](PANTHEON_WARDEN_PRINCIPLE.md). The Warden observes and enforces boundaries; it owns no branch, tag, source, or unclaimed state. Absence is not consent, zero is not deletion, and observation is not permission. Tags never independently authorize adoption. Every adoption remains explicitly authorized, provenance-bound, validated, receiver-controlled, and subject to repository protections.

## Intent

Divergence is a capability, not a defect. A branch may explore an independent implementation without surrendering its identity. When its owner explicitly opts into automatic adoption, a narrow set of eligible improvements can be proposed to the default branch.

**Adoption is not permission to overwrite.** The system uses a pull request and GitHub auto-merge; it never writes directly to the target branch, force-pushes, bypasses branch protection, or rewrites history.

## Opt-in

Only branches beginning with `divergence/auto/` are candidates. Ordinary feature branches, existing Pantheon branches, and all other branches remain outside automatic adoption.

The branch must still point to the exact SHA that completed Branch Horizon successfully. A later push invalidates the earlier observation and requires a new successful run.

## Initial automatic-adoption scope

The first policy version is deliberately narrow. Only additive or modified changes to these paths are eligible:

- `tools/branch_horizon.py`
- `PANTHEON_BRANCH_HORIZON.md`

The candidate must be based on the current target branch, contain no deletions or renames, change no more than two files, and stay within 500 added-plus-removed lines. Workflow files, dependency manifests, lockfiles, build configuration, secrets, permissions, authentication, and all other paths are outside the allowlist and require ordinary human review.

## Validation and adoption sequence

1. A branch under `divergence/auto/` receives a push.
2. Branch Horizon completes successfully for that exact commit.
3. The trusted default-branch workflow checks that the branch still points to the observed SHA.
4. The trusted adoption gate verifies ancestry, additive diff shape, allowlisted paths, and resource limits.
5. Baseline Branch Horizon tests from the trusted default branch run against the candidate implementation.
6. If every gate passes, the workflow opens or reuses a pull request to the default branch and enables GitHub auto-merge.
7. GitHub's configured branch rules, required checks, and merge policy remain authoritative. If auto-merge is disabled or a required rule blocks the PR, adoption stops rather than bypassing it.

The privileged job checks out only the default branch. Candidate code is evaluated in a separate read-only validation job with no write token or repository secrets.

## Failure behavior

Any missing evidence, stale SHA, non-descendant history, unsupported diff record, binary file, deletion, rename, out-of-scope path, failed test, or unavailable auto-merge capability blocks adoption. A blocked candidate remains on its source branch and can be reviewed normally.

## Sacred invariant

- Preserve exact source SHA and branch identity.
- Never force-push or rewrite ancestry.
- Never bypass branch protection or required checks.
- Never auto-adopt workflow, dependency, build, security, secret, or permission changes.
- Keep the pull request and validation run as an auditable adoption record.
- No automatic forwarding to another branch or repository.

## Current boundary

This is a proposed mechanism, not a claim that any branch has been adopted. The workflow only becomes active after it is merged into the repository's default branch. It does not enable auto-adoption for existing PRs or branches that have not explicitly opted in.
