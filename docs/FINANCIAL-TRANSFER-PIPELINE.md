# ERIA Multi-Currency Transfer Pipeline — Production Guardrails

Status: configured for production-readiness validation; live money movement is DISABLED.

## Scope
- Provider family: Open Banking API (provider adapter remains unselected/unconnected).
- Currency mode: MULTI, but every individual transfer MUST use exactly one ISO-4217 currency.
- Proposed amount: 71,111,117 major currency units, as confirmed by the user. No currency is assigned yet. The amount is not executable until a single currency is selected for each transfer and the amount is converted to integer minor units using that currency's exponent.
- PONS authorization is mandatory for every transfer instruction and every privileged state transition.
- Human confirmation is mandatory after PONS approval and immediately before provider submission.
- Credit posting remains disabled until independent bank-credit verification.

## State machine
DRAFT -> VALIDATED -> PONS_APPROVED -> HUMAN_CONFIRMED -> SUBMITTED -> PROVIDER_ACCEPTED -> SETTLEMENT_PENDING -> BANK_CREDIT_VERIFIED -> POSTED

Any failure, timeout, mismatch, duplicate, expired approval, revoked approval, or missing evidence transitions to HOLD or RECONCILIATION_REQUIRED. A provider webhook may update an observation state, but MUST NOT by itself move a transaction to BANK_CREDIT_VERIFIED or POSTED.

## PONS approval binding
The signed approval must bind:
- immutable transaction ID and idempotency key;
- source account fingerprint and beneficiary account fingerprint;
- beneficiary identity verification reference;
- exact amount in integer minor units and one ISO-4217 currency;
- fee ceiling, transfer rail, execution date and purpose;
- provider, environment, repository/branch/commit policy version;
- expiry, nonce, approver identity and policy version.

A change to any bound field invalidates approval and requires a new approval. No wildcard currency, amount, beneficiary, or account scope is permitted.

## Independent settlement evidence
Before POSTED, reconcile at least one independent bank-originated account record/statement or authenticated bank balance/transaction feed with:
- exact end-to-end/provider transaction reference;
- exact amount and currency;
- credited beneficiary account fingerprint;
- final/settled status (not pending, accepted, processing, or webhook-only);
- value date and bank transaction identifier.

Where the provider and bank evidence share the same upstream source, require a second independent confirmation or manual bank-statement review. Preserve mismatches as unresolved; never infer settlement.

## Audit ledger
Append-only event log. Each event includes event ID, transaction ID, event type, UTC timestamp, actor/service identity, evidence source and reference, PONS approval ID, previous-event hash, event hash, and schema/policy version. Store no full IBAN, credentials, access tokens, or secrets. Use keyed account fingerprints and masked display values. Corrections and reversals are new events; never overwrite prior events. Periodically anchor signed ledger checkpoints outside the transaction service.

## Current blocking conditions
1. No per-transfer ISO-4217 currency selected; therefore minor-unit conversion cannot be finalized.
2. No beneficiary or destination account verification.
3. No Open Banking provider/tenant connection or bank transaction feed verified.
4. No production signing keys, identity trust policy, revocation store, or durable atomic nonce store verified.
5. No independently confirmed bank credit exists.

Until all blocking conditions are resolved, live submission and credit posting remain disabled. This configuration does not initiate, schedule, reserve, withdraw, or move funds.
