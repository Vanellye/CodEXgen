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

## Verification amendment — source remediation committed

- **Commit:** [`791dddf`](https://github.com/Vanellye/CodEXgen/commit/791dddf6ee88a0d6d74f5b3ff5fc6356db151b79) corrected the Android Faculty JSON literal and the API 21 importer constructor, aligned Gradle and CI on SDK CMake 3.22.1, and added a real HTTP bridge persistence/recovery test.
- **Follow-up:** [`8443fbb`](https://github.com/Vanellye/CodEXgen/commit/8443fbba754ef14c2bce2d1697fc3ef31f1fe821) corrected test resource handling after confirming the Python JOB store opens short-lived SQLite connections rather than exposing a close method.
- **Current state:** source remediation is committed; no successful post-remediation CI result or APK artifact has yet been recorded. The CMake 3.22.1 / NDK r16b combination remains an explicit compatibility question until the APK build runs.
- **Next evidence to append:** CI run URL and conclusion; Python end-to-end test result; Android Java compile result; APK path, package/application ID, version, and SHA-256 digest; whether the APK installs and launches on the declared API range.


## Verification amendment — second CI pass exposed legacy API drift

- **Source run:** [CI #231](https://github.com/Vanellye/CodEXgen/actions/runs/42708468400), commit `791dddf6ee88a0d6d74f5b3ff5fc6356db151b79`.
- **Observed:** the HTTP integration test reached the Geometry endpoint but asserted the wrong response nesting; the endpoint correctly returns the artifact object directly. The test fixture also initially attempted to close a `JobStore` that owns no long-lived connection.
- **Android Java compile evidence:** `MainActivity.java` imported `InputType` from the wrong Android package. The app also called JGit `Repository.findRef`, which is absent from the pinned JGit 3.7.1 API.
- **Remediation:** assert the direct Geometry artifact response, use short-lived SQLite connection lifecycle in the test, import `android.text.InputType`, and use JGit 3.7's `Repository.getRef` API.
- **Status:** these corrections are source changes awaiting the next CI run; no APK success is claimed.

## Verification amendment — restore the legacy CMake toolchain correctly

- **Source run:** [CI #231](https://github.com/Vanellye/CodEXgen/actions/runs/42708468400), API 11 build job.
- **Observed:** CMake 3.22.1 installed, but the pinned Android Gradle Plugin 3.5.4 could not parse the SDK CMake binary's version string `3.22.1-g37088a8` (`Revision.parseRevision` raised `NumberFormatException`). This failed before native compilation.
- **Correction:** return the project pin to CMake 3.10.2 and install its exact SDK package identifier `cmake;3.10.2.4988404` rather than the incomplete package identifier `cmake;3.10.2`. This retains the legacy project's intended CMake generation while fixing the package lookup.
- **Status:** correction committed for the next build attempt; APK assembly remains unverified until CI produces and inspects the artifact.

## Verification amendment — Java bridge client wiring

- **Source run:** [CI #232](https://github.com/Vanellye/CodEXgen/actions/runs/42708912309), commit `eb5071499e85ece0ad51541b65958dc7b7f7e473`.
- **Passing evidence:** 27 Python tests, including the end-to-end HTTP bridge/persistence/recovery case; browser automation; Node.js runtime contract; native C++11 and portable framework tests.
- **Observed Android compile defect:** `MainActivity` referenced `StrideEngineClient` from the `.jobs` package without importing it. The Java source job reported four unresolved-symbol errors at the four bridge calls.
- **Remediation:** add the explicit import. Extend the Android workflow to inspect package ID, minimum SDK, packaged `armeabi-v7a` JNI library, APK signature, and SHA-256 before uploading the APK and checksum.
- **Status:** pending next CI verification. This is a source correction and verification gate, not yet an APK success claim.
