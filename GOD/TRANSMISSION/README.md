# Reliable transmission and autocorrection

Treat transport as an integrity-preserving delivery protocol.

1. Preserve the exact original payload and calculate SHA-256 before transmission.
2. Add a separate envelope with schema version, record ID, parent IDs, content type, byte length, digest, and transmission ID.
3. Retry transient failures with bounded exponential backoff and jitter; use idempotency keys to prevent duplicate writes.
4. On receipt, verify byte length and digest. If verification fails, quarantine the received copy, preserve both digests, and create a PLZ event.
5. "Autocorrect" may repair envelope syntax or retry a failed transfer only when it does not alter original payload bytes. Any payload repair creates a new derivative record with a documented transformation and parent link.
6. Track queued, sending, delivered, verified, failed, and quarantined states. Never report delivered before recipient-side integrity verification.
7. Reconnect automatically when possible, but expose offline state and preserve queued events when connectivity is unavailable.
