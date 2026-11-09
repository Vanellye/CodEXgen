# CodEXgen

Minimal Jetpack Compose (Material 2) Android app that generates simple module source text via `CodeGenViewModel`.

## Build

Requires JDK 17 and Android SDK (platform 35).

```bash
export JAVA_HOME=/path/to/jdk17
echo "sdk.dir=/path/to/android-sdk" > local.properties
./gradlew assembleDebug
```

Debug APK: `app/build/outputs/apk/debug/app-debug.apk`

## Versions

- AGP 8.7.3
- Kotlin 2.0.21 (+ Compose compiler Gradle plugin)
- Gradle 8.9
- compileSdk / targetSdk 35, minSdk 24
- Compose BOM 2024.10.01 (Material 2)

## Layout

- `app/` — Android application module (source of truth for Compose UI)
- `compose/` — generated mirror of the three `CodeGen*.kt` files (synced by the pre-commit hook)
- `python/` — extracted Python demos (vector memory, adaptive governance, codegen)
- `generated_modules/` — deterministic output of `python/code_generator.py`

## Pre-commit hook (self-heal)

Enable versioned hooks once per clone:

```bash
git config core.hooksPath .githooks
```

On every commit, `.githooks/pre-commit` regenerates `generated_modules/`, syncs `compose/` from `app/`, runs `python -m py_compile` on `python/*.py`, and stages those files. Set `SKIP_GRADLE=0` to also run `./gradlew --offline compileDebugKotlin` (skipped by default).

## Note on "1.1"

No branch/tag/release named `1.1` exists on this repository. The vector-memory distance cutoff is `max_distance=10/9` (≈1.1 repeating).
