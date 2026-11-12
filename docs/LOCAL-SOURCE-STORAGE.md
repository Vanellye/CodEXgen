# ERIA Local Source Storage

## Pipeline

`SourceCodeInput → SourceCodeCollector → DataEnvelope → LocalSourceCodeStore → read-back verification`

- Intake requires an authorization record scoped to `source.collect`.
- Persistence requires a second explicit authorization scope: `source.store`.
- The storage approval must carry the same `approvalRef` as the collection envelope.
- Read-back requires `source.read`; the record's SHA-256 digest and envelope are checked again.
- Writes use a temporary file, flush and fsync, then rename within the same app-private directory. Existing record IDs are never overwritten.
- A failed read-back verification attempts to remove the just-written record and reports failure.
- Pass the Android application's private `Context.filesDir` as the store root. Do not pass shared/external storage.
- The record preserves repository, ref, full commit ID, relative path, language, exact UTF-8 source bytes, digest, timestamp, and approval reference.

## Explicit boundaries

This implementation does not fetch source from Git or the network, crawl directories, execute imported code, modify repository files, publish, or dispatch externally. No trigger can cause an external action.

The binary local record is **not encrypted at rest** in this version. App-private storage restricts access under Android's application sandbox, but it is not a substitute for encryption against device compromise or backup exposure. Encryption with Android Keystore is a separate reviewed step.

SHA-256 detects content changes relative to the recorded digest; it does not prove authorship, signer identity, repository authenticity, or code safety. The approval object is an application-level authorization assertion and is not a cryptographic identity proof.

## Approval scopes

Use separate, narrowly scoped approvals:
- collection: `source.collect`
- persistence: `source.collect` + `source.store`, with the same approval reference
- retrieval: `source.read`

No approval scope implies network, export, execution, publication, or repository mutation.
