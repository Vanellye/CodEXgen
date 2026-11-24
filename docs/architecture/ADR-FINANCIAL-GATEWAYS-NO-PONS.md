# ADR: Remove PONS from Financial Gateway Runtime

**Status:** Proposed architecture baseline  
**Scope:** ERIA / ASH Financial Tunnel on `feature/eria-financial-tunnel`  
**Decision:** PONS is not a dependency, authority, middleware, policy engine, or approval hop in any financial gateway request path.

## 1. Meaning of this change

“Purge PONS from gateways” means removing PONS coupling from gateway architecture and implementation. It does **not** mean deleting PONS from the wider repository, rewriting its history, or removing transaction safeguards.

The current repository search did not identify an implemented ERIA financial gateway or a PONS-backed financial gateway request path. Therefore, there is no existing gateway integration to claim has been removed. This ADR establishes the required architecture before gateway implementation begins.

## 2. Prohibited gateway dependencies

Financial gateways and provider adapters MUST NOT:

- import, instantiate, call, or link PONS Issuer, PONS Verifier, PONS policy services, or PONS MCP endpoints;
- require a PONS token, verdict, signature, approval record, database, environment variable, or network service to start or process a request;
- delegate authorization decisions to PONS or treat a PONS response as a provider credential;
- use PONS as a fallback when the independent authorization service is unavailable;
- expose PONS-specific types in public gateway contracts, provider interfaces, event schemas, or persistence models.

These rules apply to both TypeScript and Kotlin MCP gateways and every banking, payment, crypto, custody, and blockchain adapter.

## 3. Independent transaction authorization remains mandatory

Removing PONS does not authorize unattended movement of funds. The gateway must enforce an independent, narrowly scoped transaction-authorization boundary.

Before any live financial mutation, require a fresh user confirmation bound to an immutable transaction preview containing, as applicable:

- provider and operation;
- source account or wallet identifier;
- destination/recipient;
- asset and network;
- exact amount and currency;
- quote or exchange-rate reference;
- fees and maximum fee;
- expiration time and unique idempotency key;
- preview digest and the identity of the confirming user.

The authorization must be single-use, expire, resist replay, and fail closed on any mismatch. A changed amount, recipient, network, fee ceiling, provider, or quote requires a new preview and new confirmation. Provider-native authentication, account permissions, and risk checks remain independently required.

Read-only operations may use separately scoped read permissions. Simulation must never be interpreted as authorization for a live operation.

## 4. Runtime request path

```text
Client
  -> ERIA Financial MCP Gateway
  -> Input/schema validation
  -> Capability and scope checks
  -> Independent Transaction Authorization (live mutations only)
  -> Provider Adapter
  -> Provider API / approved testnet
  -> Ledger + receipt + reconciliation
  -> Audit event
```

PONS does not appear in this path. AVS may operate as an independent evidence/validation component, but it is not a substitute for user authorization and is not a gateway dependency unless separately justified and reviewed.

## 5. Provider configuration

Provider selection is explicit and capability-based. A provider cannot silently replace another provider for a transfer, withdrawal, trade, or broadcast. Uncertain outcomes must be reconciled with the original provider before any retry.

Default execution mode remains `SIMULATION_ONLY`. Live execution remains disabled until provider-specific sandbox tests, security review, and explicit operational enablement are completed.

Secrets belong in a dedicated secret store; never commit credentials, API keys, access tokens, private keys, or seed phrases.

## 6. Acceptance criteria

- [ ] TypeScript and Kotlin gateway modules compile without PONS packages or imports.
- [ ] Gateway startup and read-only tests run with all PONS services unavailable.
- [ ] Provider adapters have no PONS-specific configuration, schemas, headers, RPC calls, or event fields.
- [ ] Static dependency scan finds no PONS references in gateway runtime source or gateway manifests.
- [ ] Live mutation tests reject missing, expired, replayed, or mismatched user authorization.
- [ ] Changing a material transaction field invalidates the prior authorization.
- [ ] Provider-native authentication and permission checks remain enforced.
- [ ] Simulation tests cannot reach live provider endpoints.
- [ ] Ledger, receipt, provenance, idempotency, and reconciliation tests pass.
- [ ] Main and existing ERIA application behavior remain unchanged.

## 7. Migration and preservation

This is an additive decision record. It does not delete PONS source, PONS evidence, historical records, or unrelated repository integrations. Any future gateway code must be created or changed only on `feature/eria-financial-tunnel`, with changes reviewed against this ADR. No merge to `main` is authorized by this record.
