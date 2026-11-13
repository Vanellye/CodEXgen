# ERIA Correction Runtime

## Scope

The runtime correction contract currently instruments the application's SKRIBED derivative operation, `SkribedDocument.derive()`. No other correction API was found in the inspected application source paths. Code generation is not classified as a correction and is not silently recorded as one.

## Required behavior

- Every call to `derive()` must receive a document constructed with an explicit `CorrectionLineageJournal`; there is no default in-memory journal.
- A correction tier is anchored to the immutable @11 commit `b60fac42ba0573c251cf7f7fe139bfa0f9c078f8`.
- Each tier records a unique correction ID, correction point, operation/version, change kind, source and output SHA-256 hashes, direct parent correction ID, and the ordered correction-ID lineage.
- A derivative is returned only after its tier has been appended successfully. A journal write failure aborts the operation.
- A correction cannot derive from a variant that is not present in the same document's journal.
- The original text remains immutable. Corrections are additive; existing journal records are never rewritten by this API.
- Git commit SHA remains null until a real repository commit is associated with that correction. Runtime code must not fabricate one.

## Application wiring

Use the application factory to place the journal in the app-private files directory:

```kotlin
val document = EriaCorrectionRuntime.document(
    context = applicationContext,
    originalText = sourceText,
    provenance = WritingProvenance(sourceRef = sourceReference)
)

val corrected = document.derive(
    kind = WritingVariantKind.CORRECTED,
    text = correctedText,
    operation = "editorial-correction",
    operationVersion = "1",
    changeKind = CorrectionChangeKind.REPLACE,
    correctionPoint = "editorial.review"
)
```

For a correction derived from a previous variant, pass `basedOn = priorVariant`. The runtime checks that the parent tier belongs to the same document and records the complete lineage. Do not create a second document to continue an existing correction chain.

The app-private journal is local to the installation. It is not network-dispatched or automatically synchronized. Backup, export, multi-device reconciliation, and signed approval attestations are not implemented by this change.

## Files

- `CorrectionLineage.kt` — immutable tier model and @11 anchor.
- `CorrectionLineageJournal.kt` — append-only journal interface, in-memory test journal, and durable file journal.
- `EriaCorrectionRuntime.kt` — application-private journal factory.
- `SkribedAndTransmission.kt` — instrumented `SkribedDocument.derive()`.
- `SkribedAndTransmissionTest.kt` — lineage, detached-parent rejection, immutability, and persistence tests.

## Verification boundary

Tests have been added but must run in CI or a local Gradle environment before this implementation is considered verified. This branch does not claim that every possible correction feature elsewhere in the repository has been wired: the repository's complete source tree and all correction call sites must be audited before making that broader claim.
