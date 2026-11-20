# Scheduled hybrid allowance bridge

## Behavior
- Scheduled occurrences produce expiring proposals only; this code does not install a timer or unattended worker.
- Each due occurrence requires fresh provider balance evidence, explicit reserves, configured pool/beneficiary/transfer/rolling-period caps, and verified account/permission evidence.
- Wise and Plaid remain separate provider identities and evidence sources.
- Duplicate funding-source references across providers are rejected to prevent counting the same underlying funds twice.
- Every proposal is hashed after its schedule and provider evidence are attached.
- Independent reviewer approval must sign the exact proposal digest and policy version through the existing Ed25519 verifier and externally governed registry.
- Approval is not live transfer permission. Allocation recording and transfers remain separately gated.
- All outputs remain PREPARE_ONLY; live submission is hard-disabled.

## Integration contract
A trusted provider connector must create `ProviderConnectionEvidence` only after independently checking authentication, account verification, provider permissions, eligible rails, and evidence provenance. This branch does not implement OAuth, API credentials, token storage, provider webhooks, or production network calls.

A scheduler may call `prepare_due_occurrence` at the configured interval. It must persist occurrence IDs idempotently, fetch fresh balances, call `prepare_cross_provider_allowance`, and route the resulting digest to an independent reviewer. It must not auto-approve or auto-submit.

## Current status
Connection evidence, keys, balances, beneficiaries, policy amounts, and schedule are not configured. The example remains a template. No real provider accounts are connected and no funds are moved.
