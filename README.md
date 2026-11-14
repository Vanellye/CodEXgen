# ERIA

ERIA is the canonical project identity for this codebase. The GitHub repository remains
`Vanellye/CodEXgen` during this migration so existing clone URLs, issues, pull requests,
and provenance links continue to resolve.

## NEXUS — WANT branch knowledge and direction

[NEXUS](docs/NEXUS.md) is the cross-reference contract for discovering relevant WANT
branches and connecting source-bound knowledge. It records **what is claimed**, **how
it is known**, **where the evidence lives**, and **what bounded direction may follow**.

The Kotlin reference implementation is
`app/src/main/java/com/vanellye/eria/evolution/WantBranchIntelligence.kt`.
It provides deterministic ranking of supplied branch candidates, explicit evidence
statuses, and typed knowledge relationships. It is read-only: live GitHub enumeration,
persistent storage, UI, and adoption adapters remain future work. A match score is
triage guidance, not proof or authorization.

## Android identity

- Gradle root project: `ERIA`
- Kotlin namespace: `com.vanellye.eria`
- Android application ID: `com.vanellye.eria`
- Display name and theme: `ERIA`

The application ID change creates a distinct Android package identity. Existing
installations signed under `com.vanellye.codexgen` will not update in place as the
same app; distribute this as a new app identity unless a separately reviewed
migration strategy is adopted.

## Build

Requires JDK 17 and Android SDK (platform 35).

```bash
export JAVA_HOME=/path/to/jdk17
echo "sdk.dir=/path/to/android-sdk" > local.properties
./gradlew assembleDebug
```

Debug APK: `app/build/outputs/apk/debug/app-debug.apk`

## Layout

- `app/` — Android application module (source of truth for Compose UI)
- `compose/` — generated mirror of the three `CodeGen*.kt` files
- `python/` — extracted Python demos and deterministic code generator
- `generated_modules/` — deterministic output of `python/code_generator.py`
- `docs/NEXUS.md` — knowledge lineage, branch detection, and direction data contract

## Pre-commit hook

Enable versioned hooks once per clone:

```bash
git config core.hooksPath .githooks
```

The hook regenerates `generated_modules/`, synchronizes `compose/` from the Android
sources, runs Python syntax checks, and stages generated mirrors. Set
`SKIP_GRADLE=0` to request the optional offline Kotlin compile.

## Code ethics and rehabilitation

- [ERIA Code Ethics](docs/CODE-ETHICS.md) defines authorization, provenance, privacy, reversibility, and accountability requirements.
- [ÆĀÄÂ Code Rehabilitation](docs/AEAA-CODE-REHABILITATION.md) defines the detect-to-verify repair lifecycle.
- `bash tools/aeaa-scan.sh .` runs the read-only advisory scanner; findings are review prompts, never automatic repairs.

## Compatibility and provenance

See [ERIA migration record](docs/ERIA-MIGRATION.md). Historical CodEXgen names in
commit records, provenance documents, repository URLs, and the Android Keystore
alias are intentionally retained where changing them would rewrite history,
break existing references, or make previously encrypted tokens unreadable.
