# Framework — Root Access Tablet

**Status:** policy contract for module and adapter boundaries.  
**Applies to:** module descriptors, adapters, data services, event flows, and platform bridges.

## Required declaration

Every module or adapter that touches a resource must declare the resource and operation separately:

- `READ(resource-id)`
- `WRITE(resource-id)`

A module that performs both must declare both. A module with undeclared side effects is non-conforming and must not be promoted to a trusted integration.

## Enforcement responsibilities

- Module registry: registration is not a permission grant.
- Pons: dependency resolution is not permission to read or mutate provider data.
- Velum: interface concealment is not an authorization boundary.
- Stride: orchestration must pass the caller's invitation and scoped grants; it may not mint grants.
- Pantheon: evaluates declared access requirements before execution.
- Platform adapters: enforce permissions again at the actual file, database, network, keystore, or device boundary.

## Data rules

Read access must be limited to the smallest resource and query scope needed. Write access must identify the operation and target. Delete, export, publish, rotate-key, and irreversible operations are separate consequential operations and must not be silently inferred from generic write access.

Unknown, missing, expired, revoked, or mismatched authorization means deny. Audit records must not contain credentials or secret payloads.

## Limitations

The tablet is not an OS sandbox, authentication provider, encryption system, or legal authorization service. Each adapter must implement and test its own enforcement. The shared policy does not claim that every module already consumes it.
