# BED — Buffered Event Data / Sleep–Wake State

BED is ERIA's automatic persistence lifecycle. "Sleep" means entering a quiescent state after flushing durable state; "wake" means recovery and reconciliation. It is not a biological sleep tracker unless a separately authorized sensor integration is added.

## State machine
ACTIVE -> QUIESCING -> FLUSHING -> CHECKPOINTED -> DORMANT -> RECOVERING -> RECONCILING -> ACTIVE.

If a flush fails, remain in a recoverable pending state and create a PLZ fingerprint. Never mark data saved until the durable write and integrity verification succeed.

## Autosave rules
- Checkpoint on meaningful state changes and on a configurable periodic cadence.
- Write to a temporary object, fsync where supported, verify byte count and SHA-256, then atomically publish the checkpoint.
- Keep the prior verified checkpoint until the new one is confirmed.
- Use a write-ahead journal for events that arrive during sleep or disconnection.
- On wake, replay idempotently from the last verified checkpoint; deduplicate by event ID.
- Do not silently autocorrect original bytes. Corrections are separate derived payloads with before/after hashes and explicit transformation metadata.

## Connectivity
Use bounded exponential backoff with jitter, heartbeat/health status, queued delivery, and explicit offline/online transitions. "Always connected" is a goal, not a guarantee: network loss must never cause data loss or false success.
