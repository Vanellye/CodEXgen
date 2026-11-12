# ERIA Internal Sound Signal Pathway

Status: proposed architecture; documentation only. This document does not enable microphone access, speaker playback, background capture, external networking, or hardware actuation.

## Purpose

Define a closed-loop, provider-neutral pathway that carries sound data between authorized ERIA modules and returns a result to the originating source for verification or an explicitly authorized local playback action.

The pathway is internal to ERIA. It is not an internet streaming service, webhook, installed-player integration, or permission bypass.

## Signal lifecycle

`Source → Capture → Encode → Internal Transport → Processing Module(s) → Return Path → Source Verification`

1. **Source identity** — assign a stable source ID and a per-operation correlation ID. Preserve the original source record unchanged.
2. **Capture** — accept sound only from an explicitly authorized source and operation. A proposal may be submitted without capture permission; capture itself remains gated.
3. **Encode** — describe the payload format explicitly: codec/container, sample rate, channel count, sample format/bit depth, frame sequence, and duration where known.
4. **Internal transport** — route only to named, registered ERIA module endpoints. Use bounded queues, backpressure, cancellation, and explicit hop limits.
5. **Processing** — modules receive an immutable input reference and produce a separately identified derivative. Each transformation records module identity, version, parameters, and input/output digests.
6. **Return path** — route the derivative or verification result to the original source endpoint using the correlation ID. Do not overwrite the original.
7. **Source verification** — compare source identity, sequence continuity, payload digest, and transformation lineage. Mark missing, reordered, duplicated, or mismatched frames as incomplete or invalid.
8. **Optional local playback** — playback is a separate side effect requiring its own explicit scope and user-visible approval. A successful return does not imply permission to play.

## Envelope contract

Each signal envelope should contain:

- `schema_version`
- `signal_id` and `correlation_id`
- `source_id` and `return_endpoint_id`
- `created_at` and monotonic `sequence_number`
- `media_type`, `codec`, `sample_rate_hz`, `channels`, and `sample_format`
- `payload_length_bytes` and cryptographic `payload_digest`
- `parent_signal_id` for derived signals
- `transform_chain` with module/version/parameter references
- `authorization_ref` and approved operation scopes
- `hop_count`, `max_hops`, and expiry/deadline metadata

Do not put credentials, access tokens, or unnecessary personal metadata in signal envelopes or logs.

## Authorization boundaries

Use separate, least-privilege scopes:

- `sound.propose` — submit a proposed route or processing plan; does not capture or transmit sound.
- `sound.capture` — acquire sound from a named source.
- `sound.route.internal` — deliver a specified signal to named internal module endpoints.
- `sound.process` — run a named, approved transformation.
- `sound.return` — return a result to the originating internal endpoint.
- `sound.playback.local` — play returned audio through a named local output.
- `sound.export` — export outside the ERIA boundary; disabled by default and separately authorized.

A proposal is not an authorization. Executive privileges may review, coordinate, approve a narrowly scoped request, suspend, revoke, and audit; they do not silently grant blanket capture, playback, export, or execution rights. Root governance remains non-overridable by executive or module code.

No trigger, schedule, webhook, background worker, successful integrity check, or returned signal grants permission by itself. Missing, expired, mismatched, or ambiguous authorization fails closed.

## Loop and integrity protections

- Enforce a maximum hop count and reject repeated signal IDs in a processing chain.
- Require bounded payload size, bounded queue depth, timeouts, and cancellation.
- Detect duplicate, missing, and out-of-order frames.
- Verify payload digests before and after each module boundary.
- Keep source and derivative records distinct; never silently replace the source.
- Treat malformed metadata, unknown endpoints, and digest mismatches as rejection conditions.
- Ensure return routing cannot be redirected by payload content or a processing module.
- Keep diagnostic logging metadata-only by default; do not copy raw audio into logs.

## Failure and recovery

On failure, stop forwarding the affected signal, preserve the original source record, record the failure reason and last verified stage, and return a typed error to the source when possible. Retry only under an explicit bounded retry policy; retries must be idempotent and must not create duplicate playback or external dispatch.

## Verification plan

Before runtime integration, add tests for:

- missing, wrong-scope, expired, and mismatched authorization;
- unknown source and return endpoints;
- payload digest mismatch and malformed audio metadata;
- duplicate, missing, and out-of-order frames;
- hop-limit and cycle detection;
- queue saturation, timeout, and cancellation;
- preservation of original source bytes across transformations;
- return correlation to the exact originating source;
- proof that internal routing does not invoke network, webhook, export, or playback APIs;
- separate approval required for local playback and external export.

## Implementation boundary

This specification defines contracts and safeguards only. Runtime adapters, audio capture, codecs, DSP, local playback, and persistence must be implemented and reviewed separately. Until those controls and tests exist, the pathway is a proposal and must not be represented as operational.
