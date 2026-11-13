# Add Cloud — bđyt record storage and synchronization

**Status:** provider-neutral contract; no cloud provider connected  
**Default policy:** uploads disabled; no background synchronization  
**Metadata profile:** 747 Hz (descriptive metadata only; no signal generation or device output)

## Scope

Cloud storage is designed for three immutable record classes:

1. **SOURCE** — original bđyt source records, retaining their origin identity and SHA-256.
2. **DERIVED** — transformed values, retaining parent record IDs and method version.
3. **EXECUTION_RECEIPT** — operator results, review findings, and terminal receipts.

Each record carries a stable record ID, kind, payload, SHA-256 digest, parent IDs, method version, and creation timestamp. A provider must support idempotent writes keyed by record ID and digest. Conflicting content under an existing ID must be reported, never silently overwritten.

## Implemented contract

- `BdyCloudObjectStore` is the provider-neutral cloud object-store boundary.
- `BdyLocalRecordStore` exposes pending local records and records successful remote receipts.
- `BdyCloudSyncCoordinator` validates record integrity and scoped authorization before calling a provider.
- `BdyUploadGrant` is short-lived, scoped to record kinds, and created only from an affirmative explicit-consent result.
- The coordinator is pull-free and non-scheduled: it runs only when explicitly invoked by its caller.
- A provider response must echo the record ID and SHA-256 before a record is marked synchronized.

## Upload authorization invariant

**Uploads are disabled by default.** A coordinator created without a grant returns `UPLOADS_DISABLED` without calling the cloud adapter. Declined consent cannot create a grant. Expired grants and records outside the grant's kind scope are blocked. The grant is an in-memory capability and is not persisted.

No UI currently issues grants, and no cloud provider implementation, endpoint, credential, or network permission is added in this change. Therefore this PR adds the storage/sync contracts and guarded coordinator—not a connected cloud account or live remote backup.

Before enabling uploads in a future change:
- select and review a provider;
- add provider-specific authentication using the platform secure credential store;
- present the exact record classes, destination, retention, and data volume to the user;
- obtain a fresh, affirmative, action-specific consent;
- add cancellation, retry/backoff, conflict handling, and audit receipts;
- test that revoked/expired grants stop all subsequent writes.

Downloads and bidirectional conflict resolution are intentionally not enabled yet. They require their own explicit policy and tests.

## Example integration

Construct `BdyCloudSyncCoordinator(localStore, provider)` with no grant: upload is blocked. Only after a user-facing consent flow should the app construct a short-lived `BdyUploadGrant` scoped to the selected record kinds and pass it to the coordinator.

## Frequency metadata

The requested **747 Hz** value is stored as descriptive project metadata only. It is not interpreted as a command, audio tone, electromagnetic output, timer, or hardware actuation.

## Verification

Unit tests cover default-deny behavior, scoped explicit consent, expired grants, and declined consent. No cloud transfer is claimed or performed by this implementation.
