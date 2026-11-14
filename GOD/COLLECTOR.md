# GOD Collective ingestion contract

tools/god_collective.py is a standard-library Python ingestion engine. It reads
one regular file, computes SHA-256, stores bytes content-addressably, records
capture metadata, creates a collaboration reference, and appends a lineage event.

## Storage layout

- ORIGINAL_DATA/objects/<first-two-hex>/<sha256> — exact original bytes.
- SOURCE_PROVENANCE/records/<uuid>.json — capture metadata and parent IDs.
- LINEAGE/events.jsonl — append-only ingestion events.
- COLLABORATION/records/<uuid>/source-reference.json — collaboration pointer.

The source file is read only. Existing objects are verified and reused; they are
never truncated or replaced. Record metadata and collaboration references use
exclusive file creation. A changed source during capture is rejected.

## PONS boundary

The caller must provide a CapabilityGrant for capability god.ingest, with
requested and approved scope equal to the resolved absolute GOD vault path,
a non-empty approval reference, and verified_by_adapter=True. Missing,
expired, mismatched, or unverified grants must be rejected by the trusted PONS
adapter before this function is called.

The existing PONS model explicitly treats adapter verification as an upstream
assertion, not cryptographic proof. Do not construct grants from user-controlled
JSON or treat this module as an authorization service. Connect it to the trusted
ERIA/PONS runtime before enabling unattended ingestion.

## Usage from an ERIA service

The service should resolve a grant through its trusted PONS adapter, then call
ingest_file(source, vault, grant, source_label=..., parent_record_id=...).
Use verify_record(vault, record_id) for integrity checks.

This module does not watch directories continuously or run in the background. Batch collection scans only when explicitly invoked. It does not access networks,
modify Git, deploy code, or send email. Those integrations require separate
review and explicit capabilities. A Git branch is not an independent backup.


## Parent-validation engine

`tools/god_parent_validation.py` validates each supplied parent by exact
canonical UUID, strict provenance shape, content-addressed path, SHA-256,
byte length, parent/child type policy, and complete recursive ancestry. It
rejects missing records, ID mismatches, unsafe paths, symlinks, duplicate
parents, cycles, unavailable ancestors, and altered objects. The collector
runs validation before capture and again immediately before writing the child
provenance record. Accepted child records include a `validated_parents`
manifest containing each direct parent ID, digest, and byte length.

Multiple parents can be supplied with `parent_record_ids=[...]`; the older
single-parent `parent_record_id=...` argument remains supported. Supplying
both is rejected. `verify_record` now includes ancestry validity in its
overall `valid` result.

## Repository interpretation and representation forge

`tools/eria_repository_forge.py` creates an on-demand, read-only structural
representation of a selected Git worktree. It inventories tracked and
non-ignored untracked files, hashes eligible source bytes, classifies formats,
extracts supported syntax/document structure, and reports resolvable local
imports. It does not execute code, read sensitive-name files, follow symlinks,
or write inside the scanned repository.

Use:

```bash
python tools/eria_repository_forge.py . --output "$HOME/eria-repository-forge.json"
```

The output must be a new path outside the worktree. This is an explicit
snapshot command, not a watcher or unattended device-wide crawler. See
[Repository forge SOW](SOW/AUTONOMOUS_REPOSITORY_INTERPRETATION_REPRESENTATION_FORGE.md)
for the complete contract and limitations.
