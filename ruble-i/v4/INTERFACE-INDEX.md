# Ruble-I v4 Interface Index

- `history-index.json`: canonical event-type and lifecycle index.
- `allowance-list.json`: append-only logical list contract for scheduled attendance allowance proposals and governed allocation records.
- `integrity_check.py`: IC self-inspection runner; emits PASS/HOLD/FAIL findings and a machine-readable report.
- `tests/`: unit and IC contract tests.
- `reviewer-registry.example.json`: empty template only; not a trusted registry.

## Decision semantics
- **PASS**: inspected local integrity conditions hold.
- **HOLD**: required external evidence is absent, including real reviewer enrollment/signatures or production provider approval.
- **FAIL**: tampering, invalid provenance, policy-scope violation, failed tests, or a live-execution enablement attempt is detected.

IC cannot enroll people, create real signatures, approve proposals, or authorize money movement. Test identities and signatures must be explicitly synthetic and confined to test fixtures.

## Attendance allowance status
Attendance evidence is not yet connected to a trusted source. The list is empty. Scheduled occurrence preparation may produce a PREPARE_ONLY proposal after policy and attendance evidence are configured. It does not issue a grant.
