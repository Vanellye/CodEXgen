# Push & Pull Airways — Communication and Action Routing Specification

**Status:** Initial gameplay and systems architecture specification  
**Repository:** `Vanellye/CodEXgen`  
**Branch:** `cognitive-layer-2`  
**Related work:** Debt of Creation, Character Integrity & Seriousness, Cognitive Layer 2, Zero-Dissipation Anchor, Seven Pillars, Seven Seeds, Skern, Returning Coil, Ever-Creation  
**Date recorded:** 2026-11-09

## 1. Purpose

Define a connected communication system through which characters, realms, devices, and game systems can send (**push**) and request or receive (**pull**) information and authorized actions.

**Airways are virtual communication channels in the game architecture.** They are not biological airways, and this specification makes no claim that messages or game code physically travel through a person's body.

The system should make connection visible while preserving boundaries: being connected does not mean being authorized to control another character, realm, or system.

## 2. Core rule

**Every consequential push or pull is an attributable, permission-checked event.**

- **Push:** An authorized sender publishes a message, signal, event, offer, or action request to a channel or recipient.
- **Pull:** An authorized recipient requests available information, events, or an offered action from a source.
- **Accept:** A recipient explicitly accepts an action request when consent or a state change is required.
- **Acknowledge:** A receiver confirms receipt; acknowledgement alone does not imply acceptance.
- **Route:** The channel system delivers an event only to eligible endpoints.
- **Resolve:** Delivery failures, conflicts, revocations, and rejected requests are recorded without silently rewriting history.

Push and pull are separate operations. A pull request must not secretly grant the requester write access. A push must not silently execute a consequential action on the recipient's behalf.

## 3. Channel topology

A channel is a named, typed connection between authorized endpoints. Endpoints may include:

- Characters and character groups.
- Realms, regions, and dimensional stages.
- Game services such as quest, inventory, world-state, and narrative systems.
- Player-controlled devices or local clients.
- Read-only archives and provenance services.

Channels may be direct, group, realm-wide, or system-to-system. Each channel declares its participants, direction, message types, permissions, retention policy, and routing rules.

A channel graph can branch and reconnect. Routes must not assume that every connected endpoint trusts every other endpoint. Each hop rechecks authorization and destination policy.

## 4. Event envelope

Each push, pull, acceptance, acknowledgement, or routing result should carry:

- Unique event ID and idempotency key.
- Event type and schema version.
- Sender and intended recipient or channel.
- Origin realm, endpoint, and originating event reference.
- Creation time and optional expiry time.
- Permission or consent reference.
- Payload type and integrity metadata.
- Correlation ID for related requests and responses.
- Delivery state and retry count.
- Parent event or lineage references where applicable.

Avoid placing secrets or unnecessary personal information in message payloads. Validate payload size, type, schema, and destination before routing.

## 5. Lifecycle

1. **Discover** — An endpoint learns that a channel exists and sees its declared purpose and permissions.
2. **Join** — The endpoint or its authorized controller opts in.
3. **Push** — A permitted sender publishes a typed event or request.
4. **Pull** — A permitted receiver requests available events or data within its read scope.
5. **Validate** — The router checks identity, channel membership, schema, scope, expiry, and authorization.
6. **Deliver** — The event is routed to eligible recipients; retries use the same idempotency key.
7. **Acknowledge or decline** — Receipt, acceptance, and refusal are distinct outcomes.
8. **Reconcile** — Duplicate, delayed, conflicting, or out-of-order events are surfaced for deterministic handling.
9. **Revoke or leave** — Access can be withdrawn; future delivery stops while historical records remain subject to the declared retention policy.
10. **Remember** — Preserve permitted provenance and delivery history without retaining payloads beyond the channel's declared policy.

## 6. Action semantics and safety boundaries

- Messages, requests, and executable actions are different event types.
- Consequential actions require explicit authorization at the point of execution.
- A character may mute, leave, decline, or block a channel without unrelated punishment.
- No channel may bypass another endpoint's consent or permission checks.
- Realm-wide broadcasts require explicit publisher authority and rate limits.
- High-impact actions require a confirmation step and a visible summary of effects.
- Emergency gameplay signals may use a narrowly defined, pre-authorized protocol; they do not create general control authority.
- A failed or revoked request must not be retried as a new authorization.
- No hidden channel may be used for coercion, harassment, surveillance, or manipulation.

## 7. Reliability and conflict handling

- **At-least-once delivery:** Duplicate delivery is possible; consumers must be idempotent.
- **Ordering:** Preserve order within a declared channel partition where required; do not promise global ordering across independent channels.
- **Expiry:** Expired events are not executed. Their expiry may be recorded as metadata.
- **Retries:** Use bounded backoff and a dead-letter/review queue after the retry limit.
- **Offline endpoints:** Queue only within the channel's retention and expiry rules.
- **Conflicts:** Concurrent state-changing requests require a domain-specific conflict policy; never resolve by silently discarding source events.
- **Backpressure:** Apply quotas and rate limits so one endpoint cannot overwhelm a realm or system.
- **Observability:** Expose delivery, rejection, expiry, and failure states without leaking protected payloads.

## 8. Relationship to other gameplay systems

### Debt of Creation

A push may offer a loan, resource, service, or obligation. A pull may request one. The obligation is created only after the recipient has reviewed and accepted its terms. The benefit and obligation commit atomically. A message offering debt does not itself create debt.

### Character Integrity & Seriousness

Character profiles may record observable channel behavior: whether a character communicates delays, respects refusals, honors accepted requests, and repairs mistakes. A missed delivery caused by network failure is not treated as a voluntary betrayal. Rumor or inference is not verified evidence.

### Cognitive Layer 2

The router may emit provenance references to a game-owned event log. It must not directly mutate the protected ECCL evidence ledger. A documented, read-only adapter may expose approved channel history.

### Seven Seeds, Skern, Returning Coil, and Ever-Creation

These remain narrative and ethical frameworks. Channels can carry their authored lore and multiple interpretations with source lineage intact. A new interpretation adds a linked record; it does not overwrite the original declaration.

## 9. Initial interface proposal

The first implementation should expose narrow interfaces rather than a global unrestricted bus:

- `ChannelRegistry`: discover channels and endpoint membership.
- `PermissionPolicy`: authorize publish, read, subscribe, accept, and administer operations.
- `PushPublisher`: publish a typed event with an idempotency key.
- `PullReader`: retrieve events within a declared cursor and read scope.
- `DeliveryRouter`: validate, route, retry, expire, and report delivery.
- `EventJournal`: append event metadata and provenance references.
- `ConsentController`: record join, accept, decline, mute, leave, and revoke decisions.

The interfaces are proposals only. They are not yet implemented by this document.

## 10. Acceptance tests

1. Unauthorized publishers cannot push to a protected channel.
2. A pull request cannot write or execute actions.
3. Receipt acknowledgement does not count as consent.
4. Declining or leaving a channel does not cause unrelated penalties.
5. Duplicate event delivery does not execute a consequential action twice.
6. Expired events are not executed.
7. Revoked permissions prevent future delivery and execution.
8. A failed delivery remains distinguishable from a recipient's refusal.
9. Conflicting or out-of-order events remain traceable.
10. One endpoint cannot exceed channel quotas or bypass backpressure.
11. Debt is recorded only after informed acceptance, in the same transaction as its benefit.
12. Character integrity indicators distinguish voluntary conduct from technical failure.
13. Channel history retains provenance while respecting declared retention and privacy rules.
14. The system can be disabled or rolled back without deleting original source records.

## 11. Implementation sequence

1. Define event schemas and channel permission vocabulary.
2. Implement an in-process local router with a small test channel graph.
3. Add idempotency, expiry, and append-only event metadata.
4. Add pull cursors and bounded retry handling.
5. Add consent, revoke, mute, and leave behavior.
6. Add realm-to-realm routing behind explicit allowlists.
7. Add integration tests for Debt of Creation and Character Integrity.
8. Review privacy, retention, abuse controls, and migration before any network deployment.

Do not begin with unrestricted cross-realm broadcast or autonomous action execution.

## 12. Preservation declaration

This document is an additive architecture proposal. It does not modify existing channel behavior, execute network operations, or grant new permissions. Implementation requires separate reviewed code, tests, and explicit authorization. Existing source history remains intact.

**Channel covenant:** Push only what you are authorized to send. Pull only what you are permitted to receive. Ask before acting for another. Preserve the origin of every consequential event, and keep connection distinct from control.


## 13. Local reference implementation

The first local reference implementation is in `python/channel_router.py`.

It provides:
- SQLite-backed channel registry and explicit owner-managed membership grants.
- Separate publish and read permissions.
- Local push and pull operations; no sockets or cross-realm transport.
- Idempotency keys that reject reuse with different event content.
- Per-recipient delivery states and explicit accept/decline decisions.
- Revocation that blocks future pulls and marks pending deliveries revoked.
- Durable event history and database reopen/recovery behavior.
- Append-only triggers for event and decision records.

Automated coverage is in `tests/test_channel_router.py`, including authorization, push/pull delivery, idempotency, consent, decline, revocation, recovery, and bounded pull limits.

**Boundary:** This implementation records and routes action requests; it does not execute arbitrary payloads. A future domain-specific executor must independently revalidate permission and acceptance immediately before performing a consequential state change. Realm-to-realm networking remains disabled and out of scope until the local tests pass and a separate security review approves the transport design.
