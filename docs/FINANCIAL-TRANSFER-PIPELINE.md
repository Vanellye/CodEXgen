# ERIA Multi-Currency Transfer Pipeline — Production Guardrails

Status: configured for production-readiness validation; live money movement is DISABLED.

## Scope
- Provider family: Open Banking API (provider adapter remains unselected/unconnected).
- Currency mode: MULTI, but every individual transfer MUST use exactly one ISO-4217 currency.
- Proposed amount: 71,111,117 major currency units. No currency is assigned. The amount is not executable until a single currency is selected for each transfer and converted to integer minor units using that currency's exponent.
- PONS is not part of the financial transaction authorization path. No PONS grant, PONS approval reference, PONS reviewer identity, or PONS capability may authorize, block, or advance a transfer.
- An authenticated account holder must explicitly confirm the exact transfer details immediately before any future provider submission. The confirmation receipt is transaction-specific and is not a PONS artifact.
- Independent provider controls, beneficiary verification, configured transaction/fee limits, idempotency, fraud controls, and independent bank-credit verification remain required.
- Credit posting remains disabled until independent bank-credit verification.

## State machine
DRAFT -> VALIDATED -> AWAITING_ACCOUNT_HOLDER_CONFIRMATION -> HUMAN_CONFIRMED -> SUBMITTED -> PROVIDER_ACCEPTED -> SETTLEMENT_PENDING -> BANK_CREDIT_VERIFIED -> POSTED

Any failure, timeout, mismatch, duplicate, expired confirmation, replayed confirmation, or missing evidence transitions to HOLD or RECONCILIATION_REQUIRED. A provider webhook may update an observation state, but MUST NOT by itself move a transaction to BANK_CREDIT_VERIFIED or POSTED.

## Account-holder confirmation binding
The confirmation receipt must bind:
- immutable transaction ID and unique idempotency key;
- authenticated account-holder identity/session reference;
- source account fingerprint and beneficiary account fingerprint;
- beneficiary identity verification reference;
- exact amount in integer minor units and exactly one ISO-4217 currency;
- fee ceiling, transfer rail, execution date, and purpose;
- provider, environment, and policy version;
- expiry, one-time nonce, confirmation timestamp, and user-visible confirmation-screen version.

The confirmation screen must display the source, beneficiary, amount, currency, fees, rail, date, and purpose before the account holder confirms. A change to any bound field invalidates the receipt and requires fresh confirmation. No wildcard amount, currency, beneficiary, or account scope is permitted. A stored receipt is evidence of a specific confirmation event, not blanket permission for future transfers.

## Independent settlement evidence
Before POSTED, reconcile at least one independent bank-originated account record/statement or authenticated bank balance/transaction feed with:
- exact end-to-end/provider transaction reference;
- exact amount and currency;
- credited beneficiary account fingerprint;
- final/settled status (not pending, accepted, processing, or webhook-only);
- value date and bank transaction identifier.

Where provider and bank evidence share the same upstream source, require a second independent confirmation or manual bank-statement review. Preserve mismatches as unresolved; never infer settlement.

## Audit ledger
Append-only event log. Each event includes event ID, transaction ID, event type, UTC timestamp, actor/service identity, evidence source and reference, account-holder confirmation receipt reference (when applicable), previous-event hash, event hash, and schema/policy version. Do not record PONS approval IDs or PONS reviewer artifacts in the transaction authorization record. Store no full IBAN, credentials, access tokens, or secrets. Use keyed account fingerprints and masked display values. Corrections and reversals are new events; never overwrite prior events. Periodically anchor signed ledger checkpoints outside the transaction service.

## Current blocking conditions
1. No per-transfer ISO-4217 currency selected; therefore minor-unit conversion cannot be finalized.
2. No beneficiary or destination account verification.
3. No Open Banking provider/tenant connection or bank transaction feed verified.
4. No authenticated account-holder confirmation implementation, replay-resistant receipt store, or production identity/session assurance verified.
5. No independently confirmed bank credit exists.

Until all blocking conditions are resolved, live submission and credit posting remain disabled. Removing PONS from this path does not enable transfers or waive the controls above. This configuration does not initiate, schedule, reserve, withdraw, or move funds.
