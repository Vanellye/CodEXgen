# FICC demonstration implementation

**Branch:** `feature/ficc-development-baseline`  
**Package:** `com.vanellye.eria.ficc`  
**Implementation:** Kotlin domain/service layer inside the existing Android app module.

## Demonstration identities

`DemoIdentityDirectory` exposes four fixed local principals:

- `demo-owner` / `DEMO_OWNER`
- `demo-admin` / `DEMO_ADMIN`
- `demo-accountant` / `DEMO_ACCOUNTANT`
- `demo-auditor` / `DEMO_AUDITOR`

The directory is a deterministic demo-principal selector, not a production authentication system. It does not implement passwords, login, session issuance, MFA, identity proofing, or account recovery. Do not use it to authenticate real people.

## Authorization matrix

| Permission | Owner | Admin | Accountant | Auditor |
| --- | --- | --- | --- | --- |
| Workspace read | Yes | Yes | Yes | Yes |
| Workspace manage | Yes | Yes | No | No |
| Entity read | Yes | Yes | Yes | Yes |
| Entity manage | Yes | Yes | No | No |
| Ledger read | Yes | Yes | Yes | Yes |
| Ledger post | Yes | Yes | Yes | No |
| Ledger reconcile | Yes | Yes | Yes | No |
| Ledger delete | Yes | No | No | No |
| Audit history read | Yes | Yes | No | Yes |

Authorization is enforced in `DemoAuthorizationService` and again at ledger operation boundaries. Principals must match the fixed directory entry, remain in `ficc-demo-workspace`, and operate only on `DEMO` records. Attempts are written to the audit log as allowed or denied decisions.

Audit history is read through `DemoAuditReader`, which checks `AUDIT_READ`; callers are not given a public unguarded history reader.

## Synthetic ledger fixtures

`DemoLedgerFactory.create()` seeds:

- 10 fictional business entities in the `US-DEMO` jurisdiction.
- 6 accounts per entity: cash, receivables, payables, contributed capital, revenue, and operating expense (60 accounts total).
- 3 balanced journals per entity (30 journals total): opening capital, service invoice, and vendor bill.
- USD-only sample data with `BigDecimal` amounts.
- Provenance on each entity, account, journal, reconciliation, and audit event.

Every synthetic record is `DEMO` + `SYNTHETIC`, unverified, and marked `providerConnected=false`. Provider-origin or verified records are rejected by this fixture ledger.

## Ledger invariants and operations

- Journals require at least two positive-value lines.
- Debits and credits must balance independently for each currency.
- Journal lines must reference accounts belonging to the same entity.
- Line currency must match the referenced account currency.
- Reconciliation compares a synthetic statement fixture with the account's calculated ledger balance and records a reconciliation event only when they match.
- Deletion is deliberately lossy: only the owner can delete, and the operation requires explicit confirmation of the exact journal ID plus a non-empty reason. A deletion audit event is appended.

## Runtime and persistence limits

The current implementation is an in-memory local demonstration engine. Data and audit events reset when the process is recreated; this is not yet a durable accounting database. The audit log is append-only through its exposed interface, but in-memory storage is not tamper-proof against a compromised process or device.

No provider SDK, network client, live account connection, payment, transfer, production credential, or external transaction path is included.

## Tests

`FiccDemoLedgerTest.kt` covers role catalog, fixture counts, balanced posting, unbalanced rejection, auditor write rejection, provenance isolation, workspace isolation, exact deletion confirmation, audit visibility, real/provider record rejection, reconciliation match/mismatch, and cross-entity journal rejection.

Run on the feature branch:

```bash
./gradlew --no-daemon :app:testDebugUnitTest
./gradlew --no-daemon :app:assembleDebug
```

CI status must be checked on the commit under review; adding test source does not itself prove that tests passed.
