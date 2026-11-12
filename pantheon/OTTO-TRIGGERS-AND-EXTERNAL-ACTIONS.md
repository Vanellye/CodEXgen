# OTTO Integration: Bounded Cycles and External-Action Triggers

**Status:** Reviewable contracts. No trigger is registered against a live external provider by default.

## OTTO role

OTTO coordinates recognition of reusable patterns, evidence qualification, source-lineage preservation, and reviewable next steps. It does not silently replicate or distribute code.

The bounded rinse-and-repeat cycle is:
1. Observe the transmission or suspension event.
2. Account for source identity, digest, dependencies, and destination.
3. Reflect on the evidence and prior result.
4. Refine the candidate without rewriting its origin.
5. Restore the last verified state when a check fails.
6. Reconcile lineage, dependencies, and destination.
7. Repeat only within an explicit cycle bound.

A failed qualification holds the cycle. The implementation requires a source reference, SHA-256 payload fingerprint, reusable-pattern reference, passing tests, resolved dependencies, and verified destination. It reports qualification; it does not copy files, create branches, publish packages, or merge changes.

## Trigger model

OttoTriggerEngine matches a configured SuspensionEventType to a named action and target. It produces an ExternalActionRequest bound to the ERIA thread, source event, action key, target identifier, canonical payload digest, narrow approval scope, and idempotency key.

Detection creates a request only. It never calls a provider or dispatches an action.

## External-action dispatch gate

A host must explicitly supply:
1. an allowlist of target identifiers;
2. an ExternalActionApprovalVerifier that authenticates the human approver and verifies exact scope and request digest;
3. an ExternalActionDispatcher for one documented provider/action.

The gate denies unlisted targets, mismatched approval scopes, mismatched payload digests, and unverified approvals. Dispatch is possible only after those checks. The dispatcher must implement durable idempotency for the supplied key and return a receipt; this interface alone cannot guarantee exactly-once delivery across crashes or provider retries.

No provider, credentials, webhook, notification service, player control, Git mutation, publishing, payment, device actuation, or background trigger is connected by this change. A caller-supplied approval reference is not proof; the host verifier is the trust boundary.

## Verification

Unit tests cover bounded repeat behavior, qualification holds, source-lineage preservation, trigger request creation without dispatch, exact approval scope/digest checks, allowlisting, and dispatcher invocation only after the gate passes.

Targeted Gradle tests and provider-specific integration tests remain required before production use.
