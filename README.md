# ERIA

ERIA is the canonical project identity for this codebase. The GitHub repository remains
`Vanellye/CodEXgen` during this migration so existing clone URLs, issues, pull requests,
and provenance links continue to resolve.

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

## Pre-commit hook

Enable versioned hooks once per clone:

```bash
git config core.hooksPath .githooks
```

The hook regenerates `generated_modules/`, synchronizes `compose/` from the Android
sources, runs Python syntax checks, and stages generated mirrors. Set
`SKIP_GRADLE=0` to request the optional offline Kotlin compile.

## Compatibility and provenance

See [ERIA migration record](docs/ERIA-MIGRATION.md). Historical CodEXgen names in
commit records, provenance documents, repository URLs, and the Android Keystore
alias are intentionally retained where changing them would rewrite history,
break existing references, or make previously encrypted tokens unreadable.
