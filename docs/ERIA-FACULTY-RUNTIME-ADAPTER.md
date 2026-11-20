# ERIA Faculty runtime adapter

## Runtime integration boundary

`FacultyRuntimeAdapter` is an authorization preflight component for the Android/Pantheon runtime. It is designed to be called immediately before a separately reviewed capability adapter. It does not invoke handlers, perform I/O, launch processes, read secret values, send network requests, operate devices, or control biological systems.

## Contract

Every request is bound to a request ID, requester, capability, exact scope, resource reference, purpose, and consent assertion. A grant must match all of those fields and include a distinct approver, approval reference, expiry, non-revoked state, and signed approval verified by an injected trusted verifier.

The verifier is responsible for authenticating the grant and checking authoritative revocation state. The adapter does not mint or trust UI-generated grants. Every decision is sent to an injected audit sink; if the sink fails or throws, the result is changed to `DENIED_AUDIT_UNAVAILABLE`.

## Capability controls

- Secret-manager handle: approved secret manager and least privilege. Secret material is never accepted as request data.
- Visible process: visible process, explicit user confirmation, and resource bounds.
- Dispatch: authenticated channel, destination allowlist, consent, and replay protection.
- Hardware: documented device API, operator confirmation, safety interlock, and emergency stop.
- Biological research: literature grounding, synthetic or approved data, and non-interventional simulation only.

The result `AUTHORIZED_PREFLIGHT_ONLY` is not an execution command. `actionTaken` is always false. No concrete provider, process, hardware, or biological adapter is registered by this change.

## Validation

Unit tests cover successful preflight, missing grants, mismatched scope/resource, self-approval, expiry, revocation, signature failure, missing safety controls, audit failure, and verifier failure.

## Integration status

This is a reusable runtime authorization boundary, not end-to-end deployment. Existing PantheonRuntimeGate remains a review-only envelope gate. Wiring a production handler requires a separately reviewed adapter implementation and tests proving that every call path passes this preflight. No external actions are enabled by this PR.
