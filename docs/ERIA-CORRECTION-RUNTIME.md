# ERIA Correction Runtime

## Anchors

Two commit anchors have distinct purposes and must not be conflated:

- Historical source anchor (@11): `b60fac42ba0573c251cf7f7fe139bfa0f9c078f8`. This remains the immutable origin for source provenance.
- Future marker anchor: `712961866e615ff4db9e90cd40bece78a45afe39` (short SHA `7129618`). Every newly created correction tier retains this anchor for future markers.

The future marker anchor does not replace, rewrite, or rename the historical @11 source anchor. Legacy v1 journal records have a null future-marker anchor because that marker did not exist when they were recorded; their provenance is not retroactively altered.

## Correction operations

The runtime instruments `SkribedDocument.derive()`. Every derivative is written to an explicit `CorrectionLineageJournal` before it is returned. A failed journal append aborts the operation.

Each new tier records:
- unique correction ID and correction point;
- operation and operation version;
- change kind and explicit direction (`FORWARD` or `REVERSE`);
- from/to SHA-256 hashes;
- direct parent correction ID and ordered lineage;
- historical @11 source anchor and future marker anchor;
- optional resulting Git commit SHA, left null until a real commit exists.

The original source remains immutable. Corrections are append-only records; reversing a correction never deletes or edits its forward record.

## From → to / to → from alternator

Forward operation records `fromSha256 → toSha256`.

Reverse operation is explicit through `reverseTo(prior, targetText, operationVersion)`. It records `prior.toSha256 → prior.fromSha256` as a new tier. The supplied target text must hash exactly to the prior tier's `fromSha256`; the runtime does not guess or synthesize an inverse.

A reverse tier retains the forward tier ID as its parent and extends the lineage. A mismatch, detached parent, missing prior variant, or journal failure is rejected.

Example:

```kotlin
val document = EriaCorrectionRuntime.document(
    context = applicationContext,
    originalText = sourceText
)

val forward = document.derive(
    kind = WritingVariantKind.CORRECTED,
    text = correctedText,
    operation = "editorial-correction",
    operationVersion = "1",
    changeKind = CorrectionChangeKind.REPLACE,
    correctionPoint = "editorial.review"
)

val reverse = document.reverseTo(
    prior = forward,
    targetText = sourceText,
    operationVersion = "1",
    correctionPoint = "editorial.rollback"
)
```

Both tiers remain in the journal. The reverse operation is a new correction record, not a destructive rollback.

## Persistence and boundaries

- `CorrectionLineage.kt` — immutable tier model, historical source anchor, future marker anchor, and direction.
- `CorrectionLineageJournal.kt` — append-only journal; v2 records store direction and marker anchor; v1 records remain readable with no retroactive marker attribution.
- `EriaCorrectionRuntime.kt` — application-private journal factory.
- `SkribedAndTransmission.kt` — instrumented correction operations and reverse alternator.
- `SkribedAndTransmissionTest.kt` — anchor, forward/reverse, hash-match, lineage, and persistence tests.

The app-private journal is local to the installation. It is not network-dispatched or automatically synchronized. Backup, export, multi-device reconciliation, signed approval attestations, and a full audit of all future correction call sites are not implemented by this change.

## Verification boundary

Tests have been added but have not been run. The PR remains draft until CI or a local Gradle build verifies the implementation.
