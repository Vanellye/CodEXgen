# FICC development baseline

## Implemented milestones

The feature branch now contains the initial local FICC domain and the first integrated demonstration workspace:

- Four fixed demonstration principals and service-layer role authorization.
- Ten fictional entities, sixty accounts, and thirty balanced seed journals.
- App-private SQLite persistence for synthetic entities, accounts, journal headers/lines, and audit events.
- Transactional journal persistence with role, provenance, balance, entity, and currency checks.
- SHA-256 chained local audit records with integrity verification.
- Fixed demo-role selection with a 30-minute local session expiry and explicit logout.
- Jetpack Compose integration from the existing ERIA code-generation route.
- A provider adapter contract and deterministic local sandbox; live-provider mode is explicitly rejected.

## Security and scope boundary

The session selector is not real authentication. SQLite and a local hash chain are not tamper-proof against a compromised device. All data remains synthetic and local. No real bank or wallet connections, production credentials, payment initiation, transfers, or external financial transactions are implemented.

## Remaining work

- Execute Android unit tests and debug APK build on the current branch and inspect the actual job logs.
- Add forward-only SQLite migrations when schema changes are introduced.
- Add richer entity, journal, reconciliation, and audit screens, including controlled journal entry creation and reconciliation.
- Add encrypted backup/export only after a separate threat model and explicit approval.
- Keep any future real-provider integration outside this demo milestone, behind a separately reviewed security boundary and separate authorization.
