# Two-Snapshot Synthesis: Evidence Before Integration

## Compared snapshots

- Main snapshot: `a02629956deda7db4416cdbb1bc9b3c5badf90a0`
- Stride snapshot: `a8c6a90efc09e27afbead0f07191e17bf4faa431`
- Repository: `Vanellye/CodEXgen`
- Common ancestor reported by GitHub compare: `a02629956deda7db4416cdbb1bc9b3c5badf90a0`
- Relationship: divergent; Stride snapshot is 285 commits ahead and 3 commits behind the Main snapshot in this comparison.

This is a comparison record, not a merge. Neither history is rewritten, and neither snapshot is declared the owner of the other.

## What the evidence says

### Main snapshot

The Main snapshot is a smaller Android Compose/Kotlin baseline with its own Gradle Kotlin DSL configuration. It includes the legacy hypothetical Python module with malformed numeric expressions.

### Stride snapshot

The Stride snapshot contains a much broader implementation trail, including:

- Android API 11 native Views/Java compatibility work and JNI/C++ bridge work
- Git Freedom bridge and workspace import
- Pantheon C++ runtime and contract tests
- portable framework and host simulator
- Geometry knowledge/laboratory material
- local-first Stride JOB lifecycle, transfer, history, and reconciliation
- Holified Inception contextual reader and evidence distinctions
- consent review and stewardship documentation
- independent branch CI and provenance/legacy-peering guidance

These are observed repository contents and commit subjects, not a claim that every feature is production-ready.

## Important divergence: Android build architecture

The Stride snapshot removes the Kotlin/Compose Gradle Kotlin DSL files and introduces Groovy Gradle configuration and a Java Views application entry point. The Main snapshot still has Kotlin/Compose source and Kotlin DSL build configuration.

Therefore, copying the router or the whole Stride tree into Main without an integration plan risks a mixed or inconsistent Android build. The router must be evaluated against the target build system and API profile, not simply copied because it exists on the Stride side.

## Important divergence: legacy syntax

The Stride history includes a later edit to `hypotheticals/bio_resonance_fiction.py` that changes the malformed expressions to:

- `range(0, 16, 2)`
- `int(level * 20)`
- `level * 1.1`

That makes the expressions syntactically valid, but the chosen numeric semantics are assumptions. The module itself identifies its content as fiction. The Main snapshot retains the malformed glyphs. Preserve both states as evidence; review the intended values and fictional output semantics before proposing a repair to Main.

## Shared principles that can be carried forward without merging code

1. Preserve source history and provenance.
2. Treat branches as independent contributors; map and test interfaces before peering.
3. Keep proposed interpretations separate from original recorded events.
4. Require explicit authorization for consequential writes.
5. Prefer reversible, additive changes and independent validation.
6. Keep speculative or fictional content clearly labeled; do not promote it to scientific evidence.
7. Keep human review and user consent visible at integration boundaries.

## Integration sequence

1. Review this comparison and confirm the intended target build architecture.
2. Validate the router in isolation, including Android compile, authentication lifecycle, transport, and workspace overwrite behavior.
3. Decide which Stride components have clear interfaces with Main; do not bulk-merge 285 commits.
4. For each selected component, make a small additive peering change with provenance, tests, and a rollback path.
5. Keep the legacy syntax repair separate until intended numeric semantics are confirmed.
6. Re-run CI on the exact candidate head and review each result before merge.

## Truth statement

A branch being newer, larger, or more capable does not make it universally correct. A baseline being called Main does not make it the owner of every contribution. The defensible synthesis is the set of claims that survive provenance checks, interface review, reproducible tests, and human scrutiny.

**No merge, deletion, force update, or source rewrite is performed by this synthesis record.**
