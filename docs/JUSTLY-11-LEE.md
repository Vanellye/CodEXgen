# JUSTLY 11 (LEE)

## Original merge — preserved at @11

This record names and preserves the SKRIBED and transmission-audio integration merged into `main`.

- Original Main anchor: `9dfa9c1be99818b876df0a25f11986794e6daa6e`
- Integration pull request: [#38](https://github.com/Vanellye/CodEXgen/pull/38)
- Original merge commit (@11): `b60fac42ba0573c251cf7f7fe139bfa0f9c078f8`
- Integrated change set: 7 files, 445 additions, 0 deletions
- Preserved archive branch: `archive/justly-11-merge`, pointing to the original merge commit above

## Correction-lineage rule

Every correction point in ERIA must have a visible, traceable tier line back to the original source tier (@11). A correction is an additive descendant; it must never replace, absorb, obscure, or rewrite its source.

**Prohibited:** detached corrections, overwritten origins, and silent merges. No correction may be accepted as lineage-complete unless its source tier, direction of change, resulting tier, and full ancestry are recorded. A merge must explicitly identify all parent commits and the review/approval that authorized the merge. If any required fact is unavailable, mark the record **pending** and do not represent the correction as fully traced or merged.

Each correction record must state:

1. **Original source tier:** the @11 merge commit, or the exact descendant source commit from which this correction was made, with an explicit ancestry path to @11.
2. **Correction point:** the affected path, contract, behavior, or decision and the exact change made.
3. **Direction of change:** an explicit `from` state/contract/value and `to` state/contract/value, plus whether the change adds, removes, replaces, or constrains behavior. Do not describe direction with an ambiguous label such as “updated.”
4. **New correction tier:** the resulting commit SHA and branch/ref, once created.
5. **Full provenance:** ordered lineage from @11 through each source/parent commit to the new correction commit; all merge parent SHAs; authorizing review or approval reference when applicable; and links to related changes and test evidence.

For a correction spanning multiple paths, record each affected path under the same correction-point ID and describe the direction of change for each path. If a source, parent, approval, or resulting SHA is not known, mark that field **pending**; never invent or infer a commit identifier. Preserve prior entries append-only: corrections amend the record by adding a new entry, not by erasing or overwriting an earlier origin. No correction-lineage entry grants runtime permission, external dispatch, or automatic execution.

### Correction-lineage entry template

```yaml
correction_id: "ERIA-CORR-<unique-id>"
original_source_tier:
  ref: "archive/justly-11-merge"
  commit: "b60fac42ba0573c251cf7f7fe139bfa0f9c078f8"
correction_point:
  paths: []
  change: "<specific change>"
direction_of_change:
  from: "<prior state or contract>"
  to: "<resulting state or contract>"
  operation: "<add | remove | replace | constrain>"
new_correction_tier:
  branch: "<branch>"
  commit: "pending"
provenance:
  lineage_from_at_11:
    - "b60fac42ba0573c251cf7f7fe139bfa0f9c078f8"
    - "<each exact intermediate/source commit, in order>"
  source_commit: "<exact parent/source SHA>"
  merge_parents: []
  review_or_approval: "pending"
  tests: "not-run"
runtime_authorization: "none"
```

## Recorded correction tiers

The following entries record known Main-line documentation corrections after @11. They are historical records, not a claim that each marker changed application runtime code. The listed commits are known descendants; exact intermediate ancestry and merge-parent details must be expanded in a correction entry when documenting a specific future change.

| Correction point | Change / marker | New correction tier | Source lineage |
|---|---|---|---|
| #991 | Main documentation designation | `0a3bcbd5190c39d0142e8e6b843e2cfa393eb390` | Descends from @11 |
| 11th commit ahead | JUSTLY 11 (LEE) designation | `c5a882efd1f471c57ebd93e08352fd9dfc5b1b06` | Descends from @11 |
| Marker pair | `Ðôn̈ 2 Mâƙëṛ`; `ÐŒM 2 MARKER` | `e0dd0cf38f3e7070d1ea26bf38cd6a14de6036a1` | Descends from @11 |
| Marker | `MÆṛƙêŕ` | `da87211bb64566aa0934f346cd93bee9a4ed247e` | Descends from @11 |

## Main-line designation

- `#991` identifies the preceding Main documentation update.
- The historical designation commit was the 11th commit ahead of the requested Main anchor at the time it was created.
- Commit message: `11th commit ahead — JUSTLY 11 (LEE)`.
- This designation is recorded in repository history; it is not a Git tag and does not rewrite the original merge commit.

## Additional history markers

- **Ðôn̈ 2 Mâƙëṛ** — marker label preserved exactly as supplied.
- **ÐŒM 2 MARKER** — companion marker label preserved exactly as supplied.
- **MÆṛƙêŕ** — third independent marker, preserved exactly as supplied.

These are repository history labels recorded in this document. They do not alter the original merge commit or independently authorize runtime actions.

## Included paths in the original @11 integration

- `app/src/main/java/com/vanellye/eria/contracts/SkribedAndTransmission.kt`
- `app/src/main/java/com/vanellye/eria/contracts/TransmissionAudioPlayer.kt`
- `app/src/main/java/com/vanellye/eria/contracts/WavAudioTransmission.kt`
- `app/src/test/java/com/vanellye/eria/contracts/SkribedAndTransmissionTest.kt`
- `app/src/test/java/com/vanellye/eria/contracts/WavAudioTransmissionTest.kt`
- `docs/SKRIBED-TRANSMISSION-CONTRACT.md`
- `docs/TRANSMISSION-AUDIO.md`

## Boundary and verification

The merged implementation supports local PCM16-to-WAV generation and explicit local playback. It does not enable external network dispatch, webhook delivery, Bluetooth routing, or automatic playback on receipt. Tests were added but were not reported as executed at merge time.

This file is a provenance record; it does not alter the historical merge commit. Future correction points must append a complete correction-lineage entry rather than overwrite prior entries.
