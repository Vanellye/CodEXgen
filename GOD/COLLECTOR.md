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

This module does not scan directories, run in the background, access networks,
modify Git, deploy code, or send email. Those integrations require separate
review and explicit capabilities. A Git branch is not an independent backup.
