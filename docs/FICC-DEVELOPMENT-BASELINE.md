# Financial Freedom Command Center (FICC) — Development Baseline

**Status:** Initial development baseline  
**Repository:** `Vanellye/CodEXgen`  
**Baseline branch:** `feature/ficc-development-baseline`  
**Base:** `main` at `4412dc714bf35296a9e751e2b8c30e0cd6cadede`

## 1. Purpose and compatibility

FICC is an additive development track inside ERIA. The existing Kotlin/Gradle Android application remains intact and authoritative for the current ERIA app. This baseline does not replace the Android application, its authentication components, its Git bridge, or existing data and migration history.

New FICC capabilities must be isolated behind their own packages/modules and documented interfaces. Do not rename, delete, or repurpose existing ERIA components as a shortcut.

## 2. Repository authorization decision

The PONS repository-write gate is **revoked** for this FICC development track. PONS approval is not a prerequisite for creating or updating files on this feature branch.

This revocation is scoped to repository-write gating for the FICC development workflow. It does not grant permission to merge into `main`, change branch protections, publish or deploy software, access production financial accounts, or execute financial transactions. Normal repository permissions, review, CI, and branch-protection controls remain applicable.

PONS may still be integrated as an optional, auditable domain-authorization service. It must not silently reintroduce the revoked repository-write prerequisite.

## 3. Demonstration identities and authorization model

Provide deterministic local demonstration identities, never mapped to real people or provider accounts:

| Identity | Demonstration permissions |
| --- | --- |
| `DEMO_OWNER` | Full access within the isolated demo workspace; manage demo users and configuration |
| `DEMO_ADMIN` | Manage demo entities, users, roles, and workspace configuration; no production authority |
| `DEMO_ACCOUNTANT` | Create and inspect synthetic ledger entries, journals, payables, receivables, and reconciliations |
| `DEMO_AUDITOR` | Read-only access to demo records, evidence, and audit history |

Authorization must be enforced in the service/domain layer, not only in the UI. Demo identities cannot acquire production authority through role changes or identifier substitution.

## 4. Synthetic financial dataset

Seed a reproducible, clearly fictional dataset containing:

- Personal checking and savings examples.
- Investment-account and portfolio examples using fictional balances and holdings.
- Business checking, accounts payable, and accounts receivable.
- At least ten fictional business entities with ownership relationships.
- Intercompany transactions, multi-currency examples, forecasts, and reconciliation cases.
- Double-entry journals with balanced debit/credit validation.
- Audit events, evidence references, exception queues, and blocker/work-round examples.

Every synthetic financial record must carry explicit provenance, for example:

```json
{
  "data_classification": "DEMO",
  "source_type": "SYNTHETIC",
  "verified": false,
  "provider_connected": false
}
```

Synthetic values must not be presented as actual balances, verified assets, or statements from a financial institution.

## 5. Provider integration posture

Do not hard-code a blanket prohibition on provider integrations. Design provider adapters behind replaceable interfaces and support local fixtures first, followed by official provider sandbox environments.

Initial baseline:
- Local synthetic adapters: enabled.
- Provider adapter interfaces and configuration surfaces: enabled.
- Official provider sandbox connections: permitted when separately configured with sandbox credentials.
- Live provider credentials and live financial operations: not enabled by this baseline; require explicit, separate authorization and environment-specific safeguards.
- No real account is to be connected as part of establishing this baseline.

Provider credentials must never be committed, seeded into demo data, or written to logs. Separate sandbox and production configuration, storage, and execution paths.

## 6. Mutations, lossy actions, and recovery

FICC must not reject legitimate capabilities merely because an action can be lossy. Support authorized edit, replace, archive, delete, and reconciliation-correction workflows where appropriate.

For destructive or difficult-to-reverse actions:
1. Show the exact target, scope, and expected effect.
2. Require an explicit user authorization at the point of action.
3. Preserve provenance and append an audit event.
4. Offer a backup, export, undo, or recovery path when technically possible.
5. Clearly identify when an action is irreversible or recovery is unavailable.

Do not silently discard records or turn real-provider records into synthetic records. Any future production-grade financial action requires its own authorization and safety design; this baseline does not authorize execution.

## 7. Audit and provenance

Audit records should identify actor, role, action, target, timestamp, source classification, before/after references where appropriate, authorization evidence, result, and recovery status. Protect audit history from ordinary demo-user mutation. Keep secrets and authentication tokens out of audit payloads.

## 8. Acceptance criteria for the baseline

- The FICC baseline is documented on this feature branch, not on `main`.
- Existing ERIA Kotlin/Gradle sources remain untouched by this baseline commit.
- Four local demonstration identities and their server-side permissions are specified.
- Synthetic dataset requirements and record provenance are specified.
- Double-entry balancing and reconciliation validation are test requirements.
- Provider adapters are extensible; local fixtures and official sandbox paths are allowed.
- Live connections and live financial operations remain separately gated by explicit authorization.
- Lossy workflows are supported with clear confirmation, audit, and recovery semantics.
- No production credentials, real account records, or live transactions are introduced.

## 9. Change boundary

This commit establishes architecture and governance requirements only. It does not claim that the authentication service, ledger, provider adapters, dashboards, database schema, or tests have already been implemented. Those are subsequent, separately reviewable implementation steps.
