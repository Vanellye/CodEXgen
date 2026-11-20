# Android dependency update automation

## Purpose

ERIA uses GitHub Dependabot to check the Android Gradle project and GitHub Actions
for available dependency updates. Dependabot opens reviewable pull requests; the
existing Independent Branch CI workflow validates each pull request by running
the Android unit tests and building the debug APK.

## Automated cycle

1. Dependabot checks Gradle dependencies and GitHub Actions every Monday.
2. Available updates are proposed as pull requests against `main`.
3. The pull-request CI runs the repository's existing integrity, Pantheon,
   Python, and Android validation jobs.
4. A human reviews the diff, release notes, compatibility, CI result, and
   requested permissions before merging.

## Authority and limits

- This automation updates dependency proposals; it does not autonomously merge.
- It does not edit application source files, delete data, change repository or
  Android permissions, publish releases, deploy builds, or dispatch external
  actions.
- Android OS/firmware updates on a device are outside this workflow's scope.
- CI has read-only repository contents permission. No package publishing,
  signing, deployment, or secret access is added.
- Failed, skipped, or unavailable checks must remain visible; a green result
  must not be inferred from a missing run.

## Validation

The current CI workflow is the qualification gate for Dependabot pull requests.
At minimum, its Android job runs:

- `./gradlew --no-daemon --stacktrace :app:testDebugUnitTest`
- `./gradlew --no-daemon --stacktrace :app:assembleDebug`

A dependency update is not considered accepted until a human reviews and merges
its pull request. This preserves source provenance and keeps update proposal
separate from authorization to integrate.

## Configuration

See [`.github/dependabot.yml`](../.github/dependabot.yml) for the schedules
and ecosystems. See [Independent Branch CI](../.github/workflows/independent-branch-ci.yml)
for the validation workflow.
