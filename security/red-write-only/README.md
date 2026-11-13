# ERIA Red Write-Only Ethical Tools

**Status:** Draft security design; defensive, synthetic-fixture-only.

## Meaning of “write-only”

The toolkit may create new, narrowly scoped security reports, evidence manifests, and remediation proposals. It must not silently read secrets, modify existing source files, overwrite or delete records, execute generated content, or dispatch network/hardware/biological actions.

This is not a claim that a scanner can assess a target without reading any target data. Any future read/scan capability must be a separate, explicitly authorized, read-only component with its own scope and data-minimization rules. The write-only component itself only emits approved artifacts.

## Allowed output roots

- `reports/` — findings and test summaries
- `evidence-manifests/` — hashes and provenance metadata for non-secret evidence
- `proposals/` — human-reviewable remediation diffs or plans

Create-new only. Existing files are never overwritten or deleted.

## Explicitly out of scope

- Credential collection, secret extraction, token dumping, or secret fingerprinting
- Exploit payloads, persistence, stealth, evasion, lateral movement, or privilege escalation
- Shell execution, dynamic code evaluation, command dispatch, or network callbacks
- Changes to source, CI workflows, branch protections, secrets, permissions, or deployment settings
- Hardware activation or biological intervention

## Shared authorization

All future adapters must call the provider-neutral `ExecutionBoundaryGuard`. A glyph, symbolic energy annotation, `Ŷ`, test pass, or finding is not authorization. Approval must be explicit, operation-specific, scoped, time-bound, revocable, and recorded.

## Evidence discipline

Findings are hypotheses until verified. Record the source revision, test method, limitations, and evidence status. Do not place secrets or secret-derived fingerprints in reports. Preserve original artifacts; append corrections rather than rewriting history.

## Current implementation

- `policy.json`: machine-readable deny-by-default policy.
- `tools/validate_policy.py`: pure path/operation policy validator; no filesystem writes or network calls.
- `test-vectors.json`: synthetic allow/deny cases.
- `tests/test_red_write_only_policy.py`: unit tests for policy decisions.

The validator is a policy helper, not a sandbox or a complete security boundary. Enforce filesystem permissions and authorization again at the actual storage adapter.
