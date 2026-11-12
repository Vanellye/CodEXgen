# ERIA Transmission Suspension Thread

**Status:** Reviewable domain contract; not a deployed service.

## Purpose

Create a traceable suspension thread from an immutable transmission origin. Preserve source identity, received time, payload fingerprint, append-only event history, and evidence-labelled cross-references.

## Suspension thread

- TransmissionOrigin retains transmission ID, source reference, receive time, and payload digest.
- SuspensionThread is an immutable state model with ACTIVE, SUSPENDED, and CLOSED states.
- Events are appended to returned state; callers must persist them in an append-only journal before treating them as durable.
- Resume requires a human-confirmation assertion, a non-empty approval reference, and exact scope `suspension.resume:<threadId>`.
- Cross-references retain VERIFIED, INFERRED, or UNKNOWN evidence states. VERIFIED requires an evidence reference.
- Corrections add new events and references. They do not rewrite the originating transmission.

## Boundaries

No installed-player adapter, player-specific proposal, process modification, media command, audio routing, background service, JNI bridge, or automatic resume is included. Provider-neutral external integrations belong to the shared OTTO trigger contract and require separate quality qualification, target allowlisting, authenticated approval, and a host-supplied adapter.

## Verification and production gaps

The unit tests cover origin preservation, hold/resume scope checks, and cross-reference evidence states. They do not authenticate a human approver or prove the truth of a source reference.

Before production use, add a durable append-only event store with integrity protection, authenticated approval verification, timestamp parsing, replay/ordering protections, and recovery tests. No runtime activation is enabled.
