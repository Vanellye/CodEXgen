# ERIA Code Aura .glob

The .glob faculty performs deterministic, read-only repository discovery. It accepts relative POSIX glob patterns, returns sorted paths and metadata, and skips sensitive-looking filenames, symlinks, and generated/vendor directories.

## API
- GET /api/glob/status
- POST /api/glob/scan with patterns, optional excludes, and bounded limit
- POST /api/glob/bootstrap/request with exact new-file manifest and purpose
- POST /api/glob/bootstrap/confirm with request_id, scope_sha256, and exact phrase
- POST /api/glob/bootstrap/apply with one-time grant_id

## Bootstrap boundary
New-file bootstrap is separate from ordinary source-patch approval. It is create-only, limited to 20 UTF-8 text files, 512 KiB each / 2 MiB total, and refuses existing paths, sensitive filenames, traversal, main/master, and stale branch/HEAD provenance. Exact paths and SHA-256 content hashes are approved with a one-time phrase. It does not stage, commit, execute, push, merge, deploy, or modify source databases.

Run tests with: python -m unittest tests.test_eria_glob
