# CodEXgen Legacy Android profile

This is a separate, dependency-light Android application module intended to preserve
an API 11 (Android 3.0) minimum without changing the modern Compose application.

## Profile
- compileSdk 29
- targetSdk 29
- minSdk 11
- Java 7 source/target
- Native Android Views; no Compose, AndroidX, Kotlin runtime, coroutines, or JGit
- App-private SQLite observations
- C++11 JNI status bridge
- ABI targets: armeabi-v7a and x86

## Build
Run:

```bash
./gradlew :legacy-android:assembleDebug
```

The first build requires Android SDK platform 29, Build Tools, NDK, and CMake 3.22.1.

## Deliberate limitations
The API 11 profile does not enable GitHub token storage or Git transport. Android Keystore
is not available on API 11, and the modern JGit/Compose dependency stack is excluded.
Do not store GitHub credentials in this legacy build. The modern `:app` module remains
separate and unchanged.

This module is an initial compatibility shell, not yet a feature-complete port of the
modern application. Verify on an API 11 emulator/device before claiming runtime support.
