# OLPIRT / STRIDE integration reconciliation

**Status:** Candidate merge commit; validation required before adoption into `main`.

## Exact ancestry

- Target parent: `e7d3c67a3720f2cfbb5eb471ec260096dee8aade` (`main` at integration snapshot)
- Source parent: `ee3149a7fc9f2b47f87aaaf0bd6f16c1a88c26c4` (`olpirt/stride-next`)
- Shared ancestor: `3056c8ab167d6e02d711d404f09b4b16f9097cd5`
- Both original branch histories are retained as parents of the candidate merge commit.

## Resolution decisions

1. **ERIA identity wins at the integration boundary.** Keep main's `com.vanellye.eria` namespace, application ID, Compose activity, root Kotlin Gradle DSL, Gradle 8.9 wrapper, and modern Android Gradle plugin. The source branch's Gradle 5.4.1 / Android Gradle Plugin 3.5.4 / Java 6 application build cannot be combined with that toolchain as-is.
2. **Bring OLPIRT implementation into the modern app module.** Retain source Java bridge, consent, resonance, JOB, JNI, C++ and Pantheon files. Configure CMake and JGit from the modern app module build file. Keep the source Java activity separately declared and non-exported; the ERIA Compose activity remains launcher.
3. **Keep API 11 profile separate.** Preserve `legacy-android/` as an independent compatibility module, not included in the modern root settings. Its build profile must be validated independently before release.
4. **Manifest reconciliation.** Preserve ERIA theme and launcher identity; add INTERNET and the source localhost-only network security configuration; disable app backup for the integrated token-bearing application.
5. **Preserve main-side governance and provenance.** Keep main's ERIA README, TRUE NORTH architecture, generated-code identity, and quarantined fictional source byte-for-byte. Do not import the source branch's altered README or malformed-literal repair into canonical files.
6. **Do not infer runtime security from compilation.** The legacy TokenVault and JGit transport need independent cryptographic, lifecycle, TLS, and authorization review. A passing compile does not certify the token vault.

## Explicitly deferred

- No API 11 behavior is claimed for the modern ERIA application.
- No automatic Git push, force update, branch adoption, or tag promotion is enabled by this merge.
- No biological control is implied by frequency or biomarker metadata.
- The legacy Android workflow from the source branch is not copied because it targets an obsolete Gradle/JDK toolchain and is scoped to the source branch. Main's independent CI remains authoritative.

## Validation record

Validation results must be attached to the exact candidate merge SHA. Until Android, Python, native C++ and repository-integrity checks pass, this candidate remains review-only and must not be merged into `main`.
