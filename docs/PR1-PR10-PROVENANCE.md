# PR #1 / PR #10 Integration Provenance Record

## Decision

Carry PR #10's evidence-before-integration principles forward while preserving the Android implementation recorded by PR #1. This record does not rewrite either history, change Android source, or claim that disconnected Git histories have been reconciled.

## Snapshot identities

- PR #1: https://github.com/Vanellye/CodEXgen/pull/1
- PR #1 recorded merge commit: `611db023ddb6ebbff58ed87a4e5fa0edb6ea22b0`
- PR #1 source head: `352199729ed100281b4c028cd0a46f5d596aade9`
- Current Main snapshot inspected: `a02629956deda7db4416cdbb1bc9b3c5badf90a0`
- PR #10: https://github.com/Vanellye/CodEXgen/pull/10
- PR #10 inspected head before this record: `99f7dd228f7ba26cf55f610ef0389a5f238090ec`

GitHub's compare endpoint reported no common ancestor between PR #1's recorded merge commit and the inspected Main snapshot. The cause is not established here. This record does not infer a history rewrite or attempt to join the graphs.

## File-level preservation check

The following PR #1 implementation files have identical Git blob hashes in the PR #1 merge tree and the inspected Main tree:

- `.githooks/pre-commit`
- `.gitignore`
- `app/build.gradle.kts`
- `app/src/main/AndroidManifest.xml`
- `app/src/main/java/com/vanellye/codexgen/CodeGenScreen.kt`
- `app/src/main/java/com/vanellye/codexgen/CodeGenUiState.kt`
- `app/src/main/java/com/vanellye/codexgen/CodeGenViewModel.kt`
- `app/src/main/java/com/vanellye/codexgen/MainActivity.kt`
- `build.gradle.kts`
- `compose/CodeGenScreen.kt`
- `compose/CodeGenUiState.kt`
- `compose/CodeGenViewModel.kt`
- `generated_modules/userprofile_module.py`
- `gradle/wrapper/gradle-wrapper.properties`
- `python/adaptive_governance.py`
- `python/code_generator.py`
- `python/semantic_vector_memory.py`
- `settings.gradle.kts`

The README differs between snapshots and is intentionally not overwritten. This is a file-level identity check, not proof that the two commit histories are the same.

## PR #10 principles carried forward

The companion `TWO-SNAPSHOT-SYNTHESIS.md` remains the detailed design record. Its principles apply to this integration:

1. Preserve source history, attribution, and provenance.
2. Keep independent branch identities intact; cross-reference rather than absorb.
3. Separate original records from corrections, interpretations, and derived views.
4. Treat proposed connections as reviewable suggestions, not commands or facts.
5. Require explicit authorization for consequential shared-state changes.
6. Use narrow interfaces, reproducible tests, and reversible additive changes.
7. Keep hypothetical and fictional material labeled; do not present it as scientific evidence.
8. A passing review gate does not itself grant merge authority.

## Validation snapshot

For PR #10 head `99f7dd228f7ba26cf55f610ef0389a5f238090ec`, GitHub Actions run `42727176146` reported:

- Android debug APK build: passed.
- Source integrity and whitespace: passed.
- Python syntax: failed while compiling the existing `hypotheticals/bio_resonance_fiction.py`.
- Python unit tests: skipped after the syntax step failed.

The malformed expressions are preserved as an unresolved legacy issue. No replacement values are guessed in this integration.

## Scope and non-claims

This integration is documentation-only. It does not change Android or Python source, repair the legacy syntax, establish runtime/device compatibility, or reconcile disconnected commit ancestry. The PR #1 Android implementation is preserved by verified file identity in the inspected Main snapshot; the differing README and ancestry gap remain visible for future review.

No force push, history rewrite, source deletion, or bulk branch merge is part of this record.
