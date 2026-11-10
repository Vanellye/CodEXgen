# Pantheon — Root Access Tablet

**Status:** executable C++11 access-decision contract added in this branch; production identity/evidence adapters remain required.  
**Applies to:** Pantheon runtime modules and their declared resource operations.

## Authority

This tablet is the local access-policy reference for Pantheon. The repository-root [ACCESS-TABLET.md](../ACCESS-TABLET.md) defines the shared policy. A more restrictive domain tablet may narrow these rights; it may not silently widen them.

## Read and write are distinct

- `READ(resource)` permits observing the exact named resource.
- `WRITE(resource)` permits changing the exact named resource.
- Neither right implies the other.
- No wildcard resources, implicit inheritance, startup grants, or grant from module registration are supported.
- A read grant cannot authorize a write; a write grant cannot authorize a read.

## Runtime enforcement

`include/pantheon/access_tablet.hpp` and `src/access_tablet.cpp` provide exact-match, default-deny evaluation. The request is bound to subject, resource, operation, invitation ID, source revision, and expiry. All declared requirements must pass.

Modules declare access requirements through the runtime contract. The ordinary execution path rejects modules with non-empty requirements. The authorized path checks every required operation before invoking the module. Controlled modules must additionally pass the existing 38/38 control gate and owner-approval adapter.

## Trust boundary

The C++ access tablet evaluates grant records; it does not authenticate who issued them, verify cryptographic signatures, implement OS filesystem permissions, or isolate malicious in-process code. A production host must authenticate the invitation source, verify approval and revocation state, supply trusted time, and constrain adapters at the actual storage/network/device boundary.

## Provider mapping

| Provider | Read right | Write right | Default |
|---|---|---|---|
| Pons | Resolve only explicitly registered interfaces | Register/replace/clear bindings | Host setup only; no self-grant |
| Secretum | Read exact secret alias | Create/rotate/delete exact alias | Deny without scoped grant |
| Via | Subscribe/read exact channel | Publish exact channel | Deny without scoped grant |
| Datorum | Read exact record/query scope | Insert/update/delete exact record scope | Deny without scoped grant |
| Modulus | Inspect registered command metadata | Dispatch exact command | Deny without scoped grant |
| Stride 2 | Read declared context and state | Mutate only declared workflow/resource | Deny without scoped grant |
| Pantheon | Inspect module descriptors and evidence | Invoke controlled or state-changing modules | Separate access and control gates |

This mapping is a policy target. It does not claim each provider is currently wired to the tablet.

## Required tests

- Missing, expired, unapproved, wrong-subject, wrong-resource, wrong-operation, wrong-invitation, and wrong-source-revision grants deny.
- Read-only grants cannot write; write-only grants cannot read.
- Multiple requirements are conjunctive: one denial blocks execution.
- Existing 38/38 control authorization remains an independent gate.
