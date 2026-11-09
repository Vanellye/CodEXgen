# CodEXgen

CodEXgen is a multi-layer Android and Python platform with two Android compatibility profiles.

## Platform profiles

| Profile | Module | Compile SDK | Target SDK | Minimum SDK |
|---|---|---:|---:|---:|
| Legacy baseline | `:legacy-android` | 29 | 29 | **11 (Android 3.0)** |
| Modern app | `:app` | 35 | 29 | 24 |

The API 11 profile uses native Android Views and app-private SQLite. It is kept separate
from the modern Jetpack Compose application because Compose and current AndroidX libraries
cannot run on Android 3.0. The modern app retains Compose, JGit, encrypted token storage,
and the C++17 native bridge.

## Build locally

Requires JDK 17, Android SDK platforms 29 and 35, Android Build Tools, and (for the modern
app) NDK 26.3.11579264 plus CMake 3.22.1.

Build the API 11 baseline APK:

```bash
./gradlew :legacy-android:assembleDebug
```

Build the modern app and native bridge:

```bash
./gradlew :app:assembleDebug
```

Run modern app lint:

```bash
./gradlew :app:lintDebug
```

Run Python validation and tests:

```bash
python -m compileall -q python tests generated_modules hypotheticals
python -m unittest discover -s tests -v
```

## Continuous integration

The GitHub Actions workflow `.github/workflows/android-build.yml` runs three independent
jobs on pushes, pull requests, and manual dispatch:

1. Python source compilation and unit tests.
2. API 11 baseline APK build and artifact upload.
3. Modern Android APK build, native C++ compilation, lint, and artifact upload.

Artifacts are retained for 14 days. A failed modern build does not prevent the independent
API 11 baseline APK from being uploaded, and vice versa.

## Architecture

- `legacy-android/` — API 11-compatible native Views application and local SQLite store.
- `app/` — modern Compose UI, Git Freedom Bridge, Data Resonance, and C++17 Olpirt bridge.
- `python/` — adaptive governance, code generation, vector memory, and stride engines.
- `tests/` — Python unit tests.
- `hypotheticals/` — explicitly exploratory/fictional models, not validated biological mechanisms.
