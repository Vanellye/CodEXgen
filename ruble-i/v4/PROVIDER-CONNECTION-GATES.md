# Wise + Plaid connection gates

Status: **NOT CONNECTED — PREPARE_ONLY**

This repository contains adapter contracts and parameter templates, not authenticated provider integrations.

## Wise Platform portal
1. Register/complete Wise Platform partner onboarding through the official Developer Hub.
2. Obtain sandbox credentials first; store secrets only in the deployment secret manager.
3. Configure OAuth/client authentication and required scopes for the approved Wise product/region.
4. Verify account ownership, account identifiers, supported currency/rail, beneficiary status, quote/fee, and transfer status through provider responses.
5. Complete Wise production review/onboarding and obtain production credentials separately.
6. Test webhook authenticity, idempotency, duplicate delivery, pending/failed/returned states, and reconciliation before any live feature can be considered.

## Plaid portal
1. Configure the Plaid app and sandbox environment in the Plaid Dashboard.
2. Request the Transfer product and complete Plaid's production review and eligibility checks.
3. Verify Link/processor-token or Transfer authorization flows appropriate to the approved integration.
4. Verify account, routing/rail eligibility, ownership/authorization, recipient/beneficiary, limits, and account status.
5. Configure webhook verification, idempotency, transfer lifecycle reconciliation, and return handling.
6. Obtain production approval and production credentials separately.

## Independent reviewer registry
- Registry must be published and signed by a governance authority independent of the operator and transfer initiator.
- Reviewer identity and role must be verified out of band.
- Each Ed25519 key must have an owner, key ID, validity interval, rotation history, and revocation state.
- Reviewer signature must cover the exact intent digest, policy version, provider, rail, source account reference, beneficiary, asset, amount, fee ceiling, expiry, and nonce.
- Reject self-review, expired keys, revoked keys, replayed nonces, stale approvals, and changed intents.
- Private keys remain with reviewers in their approved signing environment. Never commit private keys or secrets.

## Live-launch HOLD checklist
Every item must have durable evidence and an independent checkpoint:
- Wise production onboarding and account verification
- Plaid production approval and account/transfer eligibility
- provider credentials present only in secret manager
- beneficiary ownership and destination verification
- signed, current, externally governed reviewer registry
- valid independent signature for each exact intent
- configured pool, reserve, per-beneficiary, per-transfer, and rolling-period limits
- fresh balance and provider status evidence
- webhook signature validation and idempotent reconciliation
- independent destination-credit/finality evidence
- fresh CI, security review, and explicit human live-launch approval

No item in this checklist is asserted complete by this document. Live submission remains disabled.
