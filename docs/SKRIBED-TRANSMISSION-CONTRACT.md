# SKRIBED and Internal Transmission Contracts

**Status:** Initial platform-native implementation on the feature branch. This is not a claim of repository-wide adoption or production audio/hardware integration.

## SKRIBED writing contract

The original authored string is retained as an immutable source value and UTF-8 byte sequence. No normalization, transliteration, spelling correction, punctuation cleanup, or formatting rewrite occurs during capture. Corrections, interpretations, translations, and other edits are represented as separately typed derivatives with an operation name, version, and output SHA-256 digest.

The contract preserves exact valid Unicode sequences, including combining marks and non-ASCII punctuation. It does not claim to preserve arbitrary malformed UTF-16 surrogate sequences; callers should provide well-formed Unicode text.

## Internal transmission transceiver

The initial transceiver is deliberately in-process and closed-loop:

`Source → Capture → Encode → Internal Transceiver → Local Endpoint → Return Receipt`

Each frame carries a transmission ID, correlation ID, source reference, exact payload bytes, and SHA-256 digest. Payloads are defensively copied. Integrity is checked before endpoint delivery. The receipt retains the same source and correlation identifiers and records request/response digests.

## Security and execution boundary

- No network sockets, webhooks, Bluetooth, installed-player routing, external dispatch, or physical actuators are implemented by this contract.
- Detecting or receiving a frame does not authorize a consequential action.
- The endpoint is an explicitly supplied in-process callback; it must not be treated as a permission grant.
- Missing integrity, identity, or scope must fail closed.
- Hardware, network, and OS audio integrations require separate adapters, threat models, consent, authorization, and integration tests.

## Verification

Unit tests cover exact Unicode preservation, separation of source and derivative, rejection of ORIGINAL as a derivative kind, defensive payload copying, and correlated in-process round-trip behavior.
