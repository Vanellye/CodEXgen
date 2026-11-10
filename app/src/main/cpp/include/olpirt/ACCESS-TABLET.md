# Olpirt Provider Interfaces — Access Tablet

**Status:** provider-interface policy; concrete provider enforcement pending.  
**Applies to:** `IConfiguratio`, `ISecretum`, `IVia`, `IDatorum`, and `IModulus` in `contracts.hpp`.

| Interface | Existing method | Right required | Resource scope |
|---|---|---|---|
| `IConfiguratio` | `read(key)` | READ | Exact configuration key |
| `ISecretum` | `readSecret(alias)` | READ_SECRET | Exact secret alias |
| `IVia` | `publish(channel, payload)` | PUBLISH | Exact event channel; separate from READ |
| `IDatorum` | `get(key)` | READ | Exact record/key |
| `IDatorum` | `put(key, value)` | WRITE | Exact record/key |
| `IModulus` | `execute(input)` | EXECUTE | Exact registered command identity and input contract |

## Required provider behavior

1. Receive a trusted caller context and invitation reference from the host.
2. Check the exact resource and operation before touching data or dispatching work.
3. Deny by default on missing, expired, revoked, mismatched, or unverified authority.
4. Do not log secret values or payload contents.
5. Keep READ, WRITE, PUBLISH, and EXECUTE distinct.
6. Return a structured denial without partially applying a write.
7. Preserve provenance and provide append-only correction or recovery records.

## Current implementation boundary

`contracts.hpp` currently declares provider interfaces but does not carry an access context or enforce rights. Pons dependency resolution does not grant provider access. The shared Pantheon access tablet is an enforcement primitive, but these provider interfaces are not yet wired to it. This file records the required contract; it does not claim provider-level enforcement.
