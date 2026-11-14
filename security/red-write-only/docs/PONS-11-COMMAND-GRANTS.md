# PONS-11 Command Grants

## Implemented boundary

The PONS-11 module validates a proposed command invocation. It does **not**
launch a process, mint a grant, elevate privileges, bypass Android/Linux
permissions, or change repository files at runtime.

- Maximum grant lifetime: 660 seconds (11 minutes).
- Executable paths must be absolute and present in a trusted executable list.
- Executable plus the complete argument tuple must exactly match the grant.
- Working directory must be absolute, trusted, and explicitly included in scope.
- Human approval, signature verification, and current revocation checks are required.
- Root, deployment, and main-branch modification claims are rejected.
- Every authorization decision can be sent to a host-provisioned append-only audit sink.

## Trust boundary

The signature verifier and audit sink are injected by the host and must be
provided by trusted services. This module does not implement cryptographic
key custody, grant issuance, process isolation, or durable append-only storage.
A caller must audit both allowed and denied decisions.

## Not yet enabled

No shell or process execution is enabled by this change. The existing
red-write-only policy still denies shell execution and generated-content
execution. A separately reviewed isolated runner and a separately approved
policy amendment are required before command execution can be enabled.
