# ₽.ı live-transfer integration boundary

Status: design contract / prepare-only. No provider is connected and no live transfer can be submitted by this repository module.

## Intended tools

1. **Beneficiary registry** — store a stable local beneficiary ID and a provider-issued beneficiary token/reference. Verify ownership and destination details with the bank/payment provider through its approved hosted flow. Do not store online-banking passwords, full card data, full account/routing numbers, wallet seed phrases, or private keys in the ledger.
2. **Transfer-intent builder** — create a canonical intent containing source account reference, beneficiary ID, exact amount in integer minor units, ISO-4217 currency or explicit chain/token asset, fee ceiling, idempotency key, expiry, and purpose.
3. **Authorization verifier** — require a new independent human approval bound to the hash of the complete intent, including source, beneficiary, amount, asset, fees, expiry, nonce, and policy version. Check reviewer identity, signature, exact scope, freshness, and revocation. Historical PONS/AVS approvals are not reusable grants.
4. **Provider adapter** — future provider-specific implementation must be separately reviewed and must use provider-hosted authorization/consent and beneficiary verification. This repository contains no adapter credentials or live API calls.
5. **Settlement verifier** — distinguish CREATED, SUBMITTED, ACCEPTED, PENDING, SETTLED, FAILED, RETURNED, and REVERSED. Only independently verified provider/bank/network settlement evidence can mark SETTLED. A webhook or submission response alone is insufficient.
6. **Append-only history** — write intent, approval reference, submission reference, status transitions, evidence digest, and compensating events. Never overwrite the original event.

## Routing and wallet references

- Bank routing/account information should be represented by provider-issued opaque tokens or encrypted vault references, not copied into source code, chat, logs, or the history index.
- Wallet addresses are public identifiers, but must be bound to an explicit network and asset. Validate address format/checksum and destination ownership using the relevant provider/wallet workflow. Never request or store seed phrases or private keys.
- A wallet address without a chain/network and token contract (where applicable) is incomplete.
- Do not infer beneficiary ownership from an account number, routing number, email, or wallet address.
- Never silently convert assets. Require an explicit, unexpired quote and disclose fees and rounding.

## Required state machine

DRAFT -> AWAITING_APPROVAL -> AUTHORIZED -> SUBMISSION_PENDING -> SUBMITTED -> PENDING_SETTLEMENT -> SETTLED

Any failed or uncertain verification moves to HOLD or FAILED, never to SETTLED. Returns and reversals are new linked events; history is not deleted.

## Release gates before any real-money adapter

- Provider sandbox integration and provider-specific security review.
- Independent reviewer, signature, scope, freshness, and revocation verification.
- Beneficiary verification and account ownership checks through the provider.
- Idempotency and duplicate-submission protection.
- Limits, fraud/sanctions controls, fees, cutoffs, and error handling.
- Reconciliation against independent bank/network settlement evidence.
- Threat model, audit retention, key management, privacy review, and external ledger checkpoint.
- Explicit human confirmation of each exact transfer intent.

Until every gate is independently evidenced, the only supported action is preparing and validating a transfer intent; execution is disabled.
