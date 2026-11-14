# Below Pantheon — Routing, Execution, and Results

This layer exists **after** Pantheon has evaluated a proposal. It performs only the operation authorized by the decision and returns evidence about what happened.

## Responsibilities

1. Receive a Pantheon decision and its scoped authorization.
2. Confirm that the requested module, adapter, and operation match the approved scope.
3. Route only to eligible, authorized, safe gateways.
4. Execute the minimum permitted operation; default to local and reversible behavior.
5. Capture result, errors, provenance, and side effects.
6. Return a result record to the review/evidence layer above Pantheon.

## Output contract

A downstream result should carry:
- originating JOB and decision identifiers;
- selected module and gateway;
- exact authorized operation and scope;
- execution status and timestamps;
- changed resources and side effects;
- test or measurement evidence, limitations, and errors;
- rollback or recovery information where available.

## Prohibited shortcuts

- A downstream module cannot upgrade WARDEN or FALL to RISE.
- A route score cannot override authorization or safety.
- A downstream result cannot rewrite the contributor's purpose or consent.
- No remote publication, destructive write, device action, or private-data transmission without specific authorization.
- Failure, partial completion, and uncertainty must be reported rather than disguised as success.

**Handoff:** Below-Pantheon components return outcomes as evidence. They do not decide the next human purpose or silently start another consequential action.
