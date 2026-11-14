# Faculty endpoint correction runtime policy

## Required state transition

The policy is deliberately three-stage and fail-closed:

1. **Validation** checks the exact endpoint, resource, operation manifest, and every capability-specific correction point. Any missing, failed, unknown, or conflicting point blocks the request.
2. **Eligibility** is a separate derived decision. It is available only after validation passes. Eligibility is not permission to activate.
3. **Activation authorization** requires an unexpired, non-revoked, independently verified Faculty grant bound to the exact request, capability, endpoint/resource, and scope, plus a durable audit record. This stage only returns an authorization decision; it does not execute or dispatch anything.

No stage can be skipped. There is no bypass path, automatic retry with expanded scope, or inferred consent.

## Correction points

- External dispatch: authenticated provider, allowlisted destination, payload/purpose review, consent, replay protection, endpoint identity and health.
- Hardware: documented device API, device identity, bounded command manifest, operator confirmation, safety interlock, emergency stop, endpoint identity and health.
- Biological research: literature/provenance review, model assumptions and uncertainty, approved or synthetic data, non-interventional scope, endpoint/model validation.

**Biological intervention remains prohibited.** Passing checks can qualify a non-interventional computational simulation, not wet-lab action or biological actuation.

## Runtime status

`FacultyEndpointCorrectionPolicy` implements `validate`, `evaluateEligibility`, and `authorizeActivation` as separate methods. Every result has `actionTaken=false`. A concrete external, device, or research execution adapter is not invoked by this policy. Any future handler must be separately reviewed and must enforce this decision at its own call boundary.
