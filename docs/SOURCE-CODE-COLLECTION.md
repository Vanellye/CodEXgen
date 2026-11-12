# ERIA Source-Code Collection

**Status:** First implementation slice on `transmission`. The collector is an in-memory intake adapter, not a repository crawler, durable archive, or transmission service.

## Implemented

`app/src/main/java/com/vanellye/eria/source/SourceCodeCollector.kt` accepts source text supplied by a caller and produces a `CollectedSourceCode` record containing:

- repository identity, source ref, full commit object ID, repository-relative path, and language;
- the exact supplied source text;
- a SHA-256 digest of the UTF-8 source bytes;
- an observed-at timestamp and the existing TRUE NORTH `DataEnvelope`;
- the scoped approval reference and validation markers.

The collector requires an authorization record with status `AUTHORIZED`, scope `source.collect`, and a non-empty approval reference. This is a contract check, not an identity provider or authorization issuer; callers must obtain the approval through a separately governed mechanism.

## Deliberate limits

- **Read-only:** the input is never rewritten.
- **No execution:** imported source is treated as data, never run or evaluated.
- **No network:** this adapter does not fetch Git repositories or contact a provider.
- **No filesystem scan:** the caller supplies the content; the collector does not traverse local paths.
- **No durable storage:** the result remains an in-memory value. SQLite or another persistence adapter requires a separate design and retention approval.
- **Bounded input:** source text is limited to 1 MiB by default.
- **Path safety:** absolute paths and parent-directory traversal are rejected.
- **Provenance:** symbolic refs are not accepted as commit identity; a full 40- or 64-character object ID is required.
- **No implied dispatch:** collection approval does not authorize export, webhook delivery, deployment, or actuation.

The digest establishes content identity for the supplied UTF-8 text. It does not establish authorship, signer trust, repository authenticity, or that the source is safe.

## Tests

`SourceCodeCollectorTest` covers exact-text preservation, SHA-256 calculation, provenance capture, missing/wrong authorization, path traversal, symbolic commit refs, empty content, and the size limit.

Run:

```bash
./gradlew --no-daemon :app:testDebugUnitTest
```

A successful local or CI test run validates only the tested behavior. Durable storage, UI wiring, GitHub/provider adapters, and external transmission remain unimplemented and unauthorized.
