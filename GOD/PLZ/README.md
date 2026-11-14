# PLZ — Preservation & Lossless Zone fingerprints

A PLZ is a compact, append-only evidence record created whenever a need or required capability is unmet: missing authorization, unavailable dependency, failed persistence, invalid metadata, connectivity loss, rejected transmission, or unresolved data request.

PLZs represent the need and its unmet condition; they do not grant permission or bypass controls.

## Fingerprint fields
- plz_id: unique event ID
- created_at: UTC timestamp
- need: concise requested capability or resource
- status: unmet | pending | resolved | waived_by_authorized_actor
- reason_code and safe diagnostic detail
- affected_record_ids and parent/source IDs
- input/output SHA-256 digests where applicable
- authorization reference and policy decision
- retry_count, next_retry_at, and resolution_event_id
- notification_state: queued | sent | failed | suppressed

Do not place secrets, access tokens, credentials, or unnecessary personal data in fingerprints. Keep diagnostics minimal and redact sensitive payloads. Append a new resolution event; do not erase the original unmet-need fingerprint.

## Notification policy
Notify the configured recipient for actionable unmet needs, repeated failures, and resolved incidents when configured. Deduplicate repeated alerts by PLZ ID and escalation window. Email delivery is best-effort and must itself produce a delivery receipt or a new PLZ if it fails.
