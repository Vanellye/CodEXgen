# ₽.ı v4 — prepare-only multi-rail transfer coordinator

Status: **PREPARE MODE ONLY**. Live submission is hard-disabled. This package contains no provider credentials, network client, bank API calls, wallet signing, or withdrawal operation.

## Provider adapters

- `WisePlatformAdapter`: prepares a normalized IBAN/international-payment request using an opaque provider beneficiary reference.
- `PlaidTransferAdapter`: prepares a normalized US bank-transfer request using an opaque Plaid account/recipient reference.
- Both adapters expose the same prepare/submit boundary. `submit()` always raises `LiveExecutionDisabled` in this release.

These are adapter contracts and local preparation stubs, not completed or connected Wise/Plaid integrations. Production onboarding, provider consent, credentials, endpoint implementation, sandbox certification, and legal/compliance approval remain outstanding.

## Bounded withdrawal approval

A transfer is eligible for approval only when a separately configured policy supplies:
- allowed provider and rail;
- allowed currency/asset;
- allowed beneficiary IDs;
- per-transfer maximum;
- rolling 24-hour maximum;
- per-beneficiary rolling 24-hour maximum;
- maximum fee;
- policy version and expiry.

Missing limits, unknown beneficiary, unsupported asset, expired policy, exceeded cap, or missing evidence => HOLD. A limit is a ceiling, not permission to withdraw. Every transaction still requires a fresh independent human approval bound to the canonical transfer-intent digest. The injected verifier must verify reviewer identity, signature, exact scope, freshness, and revocation. No historical PONS/AVS decision is accepted as a v4 grant.

The repository ships with all live flags false and no production limits configured. Do not turn them on in source code to make a transfer work.

## IBAN and wallet handling

An IBAN is a destination identifier only. It is never searchable authorization, proof of ownership, or consent to debit. Store only a provider-issued beneficiary reference and minimal masked display metadata. Never log raw IBAN, bank account/routing numbers, passwords, API secrets, wallet private keys, or seed phrases.

Wallet routes must bind chain/network, asset, and token contract where applicable. A wallet address alone is not proof of ownership or authorization.

## State machine

`DRAFT -> PREPARED -> AWAITING_INDEPENDENT_APPROVAL -> AUTHORIZED -> SUBMISSION_DISABLED`

Provider and settlement states are modeled for future adapters, but cannot be entered by this release. No transfer can become SETTLED through this package.

## Tests

From repository root:

    python -m unittest discover -s ruble-i/v4/tests -v

Tests use synthetic data and stub verifiers. They do not call providers or move money.
