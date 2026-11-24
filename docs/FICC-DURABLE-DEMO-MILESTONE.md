# FICC durable demonstration milestone

**Branch:** `feature/ficc-development-baseline`  
**Scope:** local demonstration data only; no live financial provider or transaction capability.

## Persistence

`FiccSqliteStore` uses Android's app-private SQLite database. It persists the ten fictional entities, sixty chart-of-account records, thirty balanced seed journals, journal lines, and audit events. Seeding is idempotent and performed in a database transaction. New journal insertion validates the demo identity's posting permission, synthetic provenance, positive amounts, per-currency debit/credit balance, account ownership, and currency consistency; journal rows, lines, and the corresponding audit event commit atomically.

Audit events are chained with SHA-256 hashes and can be checked with `verifyAuditChain()`. This detects accidental or unsophisticated modification but is not a secure external anchor: a device owner or compromised process can rewrite the local database and recompute the chain. SQLite is device-local and is not a production accounting system. The schema uses SQLiteOpenHelper versioning; future schema changes must add forward-only migrations and must never drop audit or ledger data.

## Demo sessions

`FiccDemoSessionManager` stores a selected fixed demo principal and a 30-minute expiry in app-private preferences. The user can end the session explicitly. This is a role-selection convenience for the demonstration UI, not authentication, identity proofing, MFA, password management, or production access control. It must never be used to authorize real accounts or external transactions.

## ERIA UI integration

The existing Compose code-generation route now links to a FICC demonstration screen. The screen exposes role selection, local ledger counts, audit-chain verification, fictional entity names, and the deterministic provider sandbox. The original code-generation route remains available.

## Provider adapter boundary

`FiccProviderAdapter` and its snapshot/capability types define a provider seam. `DeterministicProviderSandbox` is the only implementation. It returns fixed synthetic account and transaction fixtures. `FiccProviderPolicy` rejects `LIVE_PROVIDER` mode. No provider SDK, HTTP client, bank or wallet connection, credential collection, payment, or transfer has been added.

## Verification

- Existing ledger unit tests remain in `FiccDemoLedgerTest.kt`.
- `FiccProviderSandboxTest.kt` covers deterministic data, provenance, unknown-account rejection, and live-mode denial.
- Run `./gradlew --no-daemon :app:testDebugUnitTest` and `./gradlew --no-daemon :app:assembleDebug` on this branch. Do not infer success from a workflow that only submits dependency snapshots.
