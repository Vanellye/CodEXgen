# ERIA Filesystem Extraction — Download Package

This export contains a copy of the read-only filesystem inventory implementation,
its unit tests, and its implementation contract.

## Provenance
- Repository: https://github.com/Vanellye/CodEXgen
- Source branch: `feature/eria-filesystem-understanding`
- Source commit: `2ac27689683046c1befaa7f4ab388475db39cec9`
- Source paths are preserved below this export directory.
- The copies here do not replace or rewrite the authoritative source files.

## Contents
- `app/src/main/java/com/vanellye/eria/filesystem/FileSystemUnderstanding.kt`
- `app/src/test/java/com/vanellye/eria/filesystem/FileSystemUnderstandingTest.kt`
- `docs/ERIA-FILESYSTEM-FOR-UNDERSTANDING.md`

## Boundaries
This is source-code packaging, not a scan of the device. The capability is read-only
and bounded. It does not grant Android storage permission, persist scan reports,
upload files, execute files, or modify inspected content. To inspect a device folder,
the Android app must separately implement a user-mediated Storage Access Framework
selection and grant lifecycle.

The archive is intended to be copied into the Android device's `Download` folder
by the user. No direct write to the phone's storage is performed by this GitHub action.
