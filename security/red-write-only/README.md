# ERIA Red Write-Only Ethical Tools

**Status:** Draft security implementation; defensive, synthetic-fixture-only.

## Meaning of “write-only”

The toolkit may create new, narrowly scoped security reports, evidence manifests, and remediation proposals. It must not silently read secrets, modify existing source files, overwrite or delete records, execute generated content, or dispatch network/hardware/biological actions.

This is not a claim that a scanner can assess a target without reading any target data. Any future read/scan capability must be a separate, explicitly authorized, read-only component with its own scope and data-minimization rules. The write-only component itself only emits approved artifacts.

## Allowed output roots

- `reports/` — findings and test summaries
- `evidence-manifests/` — hashes and provenance metadata for non-secret evidence
- `proposals/` — human-reviewable remediation diffs or plans

Create-new only. Existing files are never overwritten or deleted.

## Shared execution boundary and storage enforcement

- `tools/validate_policy.py` is the pure path/operation policy validator.
- `tools/execution_boundary_guard.py` defines the shared provider-neutral `ExecutionBoundaryGuard`. It requires an explicit, operation-specific, scoped, time-bounded, non-revoked human grant and an injected trusted grant verifier.
- `tools/storage_adapter.py` is the actual filesystem mutation boundary. It requires a pre-opened trusted output-root directory descriptor and an append-only audit sink. It traverses pre-existing directories using directory descriptors and no-follow flags, then creates files with `O_CREAT | O_EXCL | O_NOFOLLOW` and owner-only mode `0600`. Existing targets, symlink traversal, invalid scopes, and unverified grants fail closed.
- `tests/test_storage_adapter.py` exercises the real adapter against temporary synthetic directories. No production repository files are targets.
- `.github/workflows/eria-write-only-boundary.yml` runs this suite in isolated CI.

The injected grant verifier is a required integration point, not a placeholder authorization scheme: production wiring must validate an authentic approval issued by the trusted human-approval authority and check current revocation state. The adapter does not mint grants. The host must provision the output root and the append-only audit sink securely. This code is not a complete OS sandbox and does not make arbitrary host processes safe.

## Explicitly denied

- Source-tree modification, overwrite, delete, chmod, and writes outside the three output roots
- Secret reads/extraction, credential harvesting, token dumping, and secret fingerprinting
- Shell execution, dynamic evaluation, and exploit-payload operations
- Network/webhook dispatch and hidden execution
- Hardware activation and biological intervention

The adapter treats artifact content as inert bytes; it never interprets or executes content. A separate scanner or reader is not included.

## Evidence discipline

Findings are hypotheses until verified. Record the source revision, test method, limitations, and evidence status. Do not place secrets or secret-derived fingerprints in reports. Preserve original artifacts; append corrections rather than rewriting history.

Glyphs, symbolic energy annotations, `Ŷ`, a test pass, or a finding are never authorization.
