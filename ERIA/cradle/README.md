# ERIA Cradle

**Cradle** is the guarded transformation and build-entry layer for ERIA. Gradle remains
the Android build engine and the checked-in Gradle Wrapper remains authoritative for
the Gradle distribution version.

## Transmission path

`Cradle → Gradle Wrapper → reviewed Gradle task → test/build result`

Cradle does not replace Gradle, rewrite build files, change dependency versions, publish
artifacts, deploy applications, or transmit data to an external destination.

## Supported operations

Run from the repository root:

| Command | Operation |
|---|---|
| `bash ./cradle.sh test` | Run Android debug unit tests |
| `bash ./cradle.sh assemble` | Assemble the debug APK |
| `bash ./cradle.sh verify` | Run unit tests, then assemble the debug APK |
| `bash ./cradle.sh tasks` | List Gradle tasks |

Only these reviewed operation groups are accepted. Extra arguments and unknown
operations are rejected; arbitrary Gradle task injection is not exposed.

## Governance

- The Gradle Wrapper and its pinned distribution remain the build authority.
- Cradle records the selected operation in standard output.
- No repository write, branch mutation, publication, deployment, or external dispatch
  is performed by Cradle.
- Gradle may access configured dependency repositories to resolve build dependencies.
- CI remains read-only with respect to repository contents and runs on the pushed branch.
- Changes to Gradle versions, plugins, dependencies, signing, release, or deployment
  require separate review.

## Current boundary

Cradle is a thin, local orchestration wrapper—not a new build engine or a permission
grant. It does not yet implement MULTIPLY or SPREAD repository operations.
