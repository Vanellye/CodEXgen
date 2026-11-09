# Seed Pits — protected failure and recovery record

## Purpose

The Seed Pits preserve failures, defects, near misses, rejected assumptions, recovery evidence, and the lessons that make future work safer and more reliable. They are a learning archive, not a blacklist, punishment mechanism, or public ranking of contributors.

**A failure is retained as evidence; a person is never reduced to a failure.** Records must distinguish observed facts, hypotheses, impact, remediation, verification, and remaining uncertainty. Corrections append a new record or linked amendment; they do not erase the original evidence.

## Entry SP-STRIDE-ANDROID-BRIDGE-001 — Android bridge and APK verification

- **Scope:** Stride Android JOB dashboard, Python bridge, Faculty Engine, Geometry Laboratory artifact persistence and recovery, Android API 11 Views build.
- **Observed CI evidence:** GitHub Actions run [#230](https://github.com/Vanellye/CodEXgen/actions/runs/42707572413), commit `ba42cabab3adfa0f36098abd2bffd6d795cd3fc2`.
- **Passing lanes in that run:** Geometry Laboratory browser automation; Python compatibility compilation and reference tests; Pantheon Node.js 11 runtime contract; Pantheon native C++11 host tests; platform-independent framework C++11 contracts.
- **Android Java source failure:** `Api21WorkspaceTreeImporter.java` declared a constructor named `Api19WorkspaceTreeImporter`, so Java treated it as an invalid method declaration. The dashboard's default Faculty JSON literal also contained doubled backslash escapes that Java rejected.
- **Android APK build failure:** SDK Manager could not find the pinned `cmake;3.10.2` package. The failure occurred before NDK setup and before APK assembly; no APK was produced by that job.
- **Impact:** bridge client and dashboard Java compilation were not verified; no claim of a working APK was justified. Existing Python/Geometry/native successes did not cover Android runtime behavior.
- **Remediation seeded:** correct the constructor name; correct the Java JSON string; use the available Android SDK CMake package `3.22.1` consistently in Gradle and CI; add HTTP-level tests that import an Android JOB, run Faculty, attach Geometry, list artifacts, restart the service against the same SQLite database, export a snapshot, and recover it into a fresh database.
- **Verification gate:** require the bridge end-to-end tests, Python suite, Android Java compile, full `:app:assembleDebug`, and inspection/upload of the resulting APK artifact to pass before declaring this work verified.
- **Remaining uncertainty until CI completes:** whether CMake 3.22.1 is compatible with the pinned NDK r16b and legacy Android Gradle Plugin 3.5.4; whether the Android app compiles and assembles after the Java corrections; whether the end-to-end test passes against the current Faculty Engine implementation.
- **Stewardship:** retain this entry even after remediation passes. Append the successful run ID, commit, test counts, APK artifact name and digest as a verification amendment. Do not rewrite this observed failure as if it never happened.

## Required record format for future entries

1. Stable record ID and affected subsystem.
2. Timestamp and exact source (run, commit, test, report, or reproducible command).
3. Observed behavior, with logs or minimal reproduction.
4. Expected behavior and impact.
5. Facts separated from interpretation and unknowns.
6. Remediation proposal and responsible review.
7. Independent verification evidence and remaining limitations.
8. Linked amendment, never silent replacement.

## Governance

- Preserve provenance and the minimum necessary evidence; redact secrets, personal data, and sensitive operational details.
- No automated score may turn Seed Pit entries into a measure of a contributor's worth or trustworthiness.
- Repeated defects may justify stronger technical controls, not humiliation or permanent exclusion.
- A lesson is portable; ownership of the lesson is not transferred by sharing it.
- The Main indexes these records but does not own them.
