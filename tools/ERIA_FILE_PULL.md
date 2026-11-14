# ERIA Automated File Pull & Database Organization

This module ingests eligible UTF-8 text files from two independently tracked sources:
the local working tree and the configured GitHub remote branch.

## Configuration
- Repository: inferred from `git remote get-url origin`.
- Remote branch: `ERIA_REMOTE_BRANCH`; defaults to the current local branch.
- Schedule: `ERIA_PULL_INTERVAL_MINUTES`; defaults to 60; set to 0 to disable periodic runs.
- Private GitHub access: optional read-only `GITHUB_TOKEN` or `GH_TOKEN` environment variable.

## API
- `GET /api/pull/status`: source refs, counts, history, and recent jobs.
- `POST /api/pull` with `{}`: manual local + GitHub synchronization.

Startup synchronization runs in a background thread so the HTTP listener can start immediately.
The HTML console includes a **Pull local + GitHub** button.

## SQLite
- `pull_blobs`: deduplicated UTF-8 content by SHA-256.
- `pull_files`: latest state by source and repository path.
- `pull_file_versions`: append-preserving content/version records.
- `pull_jobs`: per-run counts, branch/ref, commit SHA, and timestamps.
- `pull_audit`: append-only event log protected against UPDATE and DELETE.

Local and GitHub records are separate source namespaces. Missing files are marked
`missing`; previous blobs and version rows remain available. Each version retains
source path, source ref, commit SHA, category, content hash, and import time.

## Scope and safety
Only text files with recognized source/document/config/data extensions and at most
2 MiB are ingested. Binary files, likely secrets, credentials, and common build/cache
directories are skipped. Symlinks are not followed in local scans.

The GitHub side uses read-only REST/raw HTTP requests. The service does not run
checkout, fetch, pull, merge, commit, push, reset, clean, or write repository files.
It snapshots the local working tree (with current branch and HEAD as provenance)
and the remote branch separately. This is not a complete Git object/history mirror;
Git history itself remains authoritative and untouched.
