# Android API 11 compatibility profile

## Build contract

- compileSdk 29
- targetSdk 29
- minSdk 11
- Android Gradle Plugin 3.5.4 / Gradle 5.4.1
- Java source and bytecode compatibility 1.6
- Android NDK r16b (16.1.4479499)
- CMake 3.10.2
- C++11
- ABI: armeabi-v7a

The app uses framework Android Views and platform SQLite APIs. Compose, Kotlin, AndroidX Lifecycle, Activity Compose, DocumentFile, and coroutines are removed from the application module.

## Preserved functionality

- Git Freedom Bridge: local repository initialization, branch checkout, status/review, selected-file commit, fast-forward-only pull, normal feature-branch push, and draft pull-request creation (remote operations require API 21+).
- Local repository path remains under app-private files/git-bridge/CodEXgen.
- Data Resonance uses the same data_resonance.db database name and observations table columns, so existing rows are retained when the app is updated in place.
- OLPIRT/Pons native dependency audit remains available through JNI.
- CodeGen has a native Views screen for local scaffold generation.

## Compatibility boundaries

- JGit 3.7.1 is used because the JGit 3.7 line retained a Java 5/6-era baseline. Newer JGit releases require newer Java runtimes.
- JGit 3.7.1 is an old dependency with published security advisories. The app restricts remote URLs to GitHub HTTPS and sets core.symlinks=false before checkout/merge to mitigate the known symlink checkout class of issue. It does not expose JGit's repo-manifest parser or Amazon S3 transport. This is risk reduction, not a claim that the old dependency is fully patched; use only repositories you trust and obtain a security review before production deployment.
- Remote HTTPS Git operations are runtime-gated below API 21. The stock TLS stack on Android 3.0/API 11 cannot be assumed to negotiate modern GitHub HTTPS. Local repository operations remain available.
- Android Keystore APIs are not available on API 11. The API-11 profile encrypts the saved token using a user-entered passphrase, PBKDF2-HMAC-SHA1, AES-CBC, and HMAC-SHA256. The passphrase is not stored; the token must be unlocked for each app session. This is not hardware-backed Keystore protection.
- The previous Keystore token format is not migrated. Re-enter and re-encrypt the token in this profile.
- Native output is restricted to armeabi-v7a to retain the API 11 native platform baseline. 64-bit-only devices are not supported by this ABI profile.
- Workspace-folder import through Android's Storage Access Framework is not available on API 11; the active profile uses app-private local repository storage.\n- The old legacy-android module remains in the repository as historical scaffolding but is no longer included in the active Gradle settings.

## Build

Use JDK 8 with Gradle 5.4.1. Install Android platform 29, Build Tools 29.0.3, CMake 3.10.2, and NDK 16.1.4479499.

Run: ./gradlew :app:assembleDebug

The GitHub Actions workflow performs this build. A successful source commit is not itself proof of a successful APK build; use the workflow result as the build verification.
