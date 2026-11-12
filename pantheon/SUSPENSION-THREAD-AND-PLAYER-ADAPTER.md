# ERIA Suspension Thread and Provider-Neutral Trigger Integration

**Status:** Reviewable domain contracts. No provider connection or background trigger is active.

## Suspension thread

- TransmissionOrigin retains transmission ID, source reference, receive time, and payload digest.
- SuspensionThread is an immutable state model with ACTIVE, SUSPENDED, and CLOSED states.
- Events are appended to the returned thread state; callers must persist them in an append-only journal before treating them as durable.
- Resume requires a human-confirmation assertion, a non-empty approval reference, and the exact scope `suspension.resume:<threadId>`.
- Cross-references retain their evidence state. A VERIFIED link requires an evidence reference; INFERRED and UNKNOWN remain explicitly distinct.
- Corrections add new events and references. They do not rewrite the originating transmission.

## Provider-neutral trigger families

The former installed-player-specific adapter and proposal path are removed from this integration branch. No player is treated as the default or exclusive target.

One trigger/request contract now covers:
- webhooks;
- HTTP callbacks;
- notifications;
- message queues;
- generic provider APIs.

Each request carries its channel, target identity, action key, source thread/event, canonical payload digest, narrow approval scope, and idempotency key. A provider-specific adapter is supplied by the host for the selected channel; no endpoint, credentials, provider SDK, or network call is embedded here.

## Trigger quality gate

A rule must pass all six evidence checks before it can produce an external-action request:
1. source integrity verified;
2. event order verified;
3. payload schema verified;
4. destination identity verified;
5. replay check passed;
6. policy checks passed.

The quality report exposes a percentage and explicit hold reasons. The dispatch threshold is 100%; a lower score produces a held rule and no request. These evidence values are assertions supplied by the host and are not themselves cryptographic proof. Production integration must bind them to authenticated verifiers and durable audit records.

## Approval and dispatch boundary

Detection creates a request only. Dispatch requires:
1. an allowlisted channel-and-target pair;
2. an authenticated human approval verifier;
3. exact approval scope and request digest match;
4. recomputed payload digest, request ID, and idempotency-key integrity;
5. a host-supplied provider adapter.

The provider adapter must implement durable idempotency and return a receipt. This interface alone cannot guarantee exactly-once delivery across crashes or provider retries. No webhook, callback, notification, queue, generic API, credentials, player control, Git mutation, publishing, payment, device actuation, or background trigger is connected by this change.

## Verification and production gaps

Tests cover bounded OTTO repetition, source-lineage preservation, quality holds, all supported channel contracts, channel/target allowlisting, approval scope, payload tampering, and request-only trigger behavior. Targeted Gradle tests and provider-specific integration tests remain required. A caller-supplied approval reference or quality Boolean is not proof; host verifiers are the trust boundary.
