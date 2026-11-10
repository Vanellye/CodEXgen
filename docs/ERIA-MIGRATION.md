# ERIA identity migration

## Decision

ERIA is the canonical product, documentation, interface, and Android package identity.
This change is isolated on `migration/eria-identity`; it does not rewrite commit
history or alter the repository slug.

## Canonical identifiers

| Surface | Canonical value |
|---|---|
| Product/display name | ERIA |
| Gradle root project | `ERIA` |
| Kotlin namespace | `com.vanellye.eria` |
| Android application ID | `com.vanellye.eria` |
| Git bridge Kotlin package | `com.vanellye.eria.gitbridge` |
| Android theme | `Theme.ERIA` |
| Git bridge private workspace | `git-bridge/ERIA` |

## Compatibility boundaries

- The GitHub repository remains `Vanellye/CodEXgen`; repository URLs and historical
  PR/commit links are provenance, not current product naming.
- The Android application ID changes from `com.vanellye.codexgen` to
  `com.vanellye.eria`. Android treats this as a distinct installed application;
  existing installs do not transparently upgrade to the new ID.
- The Android Keystore alias `codexgen_git_bridge_aes` is intentionally retained.
  Renaming it would strand tokens encrypted with the existing key. It is a storage
  compatibility key, not a public product identifier.
- SharedPreferences file/key names remain stable for the same reason.
- Historical provenance and snapshot documents retain original CodEXgen references;
  do not retroactively rename historical events or URLs.
- Old Android source package paths are removed after equivalent sources are created
  under `com/vanellye/eria`.

## Verification checklist

- [ ] Gradle root project and Android namespace/application ID use ERIA identifiers.
- [ ] Android source packages and paths agree.
- [ ] Generated Compose mirror packages match Android source packages.
- [ ] Git bridge and prompt-report Kotlin packages use ERIA.
- [ ] Manifest theme, theme resource, and launcher label agree.
- [ ] Pre-commit mirror source path points to the ERIA package directory.
- [ ] User-facing Git bridge labels use ERIA.
- [ ] Legacy Keystore alias and repository URL remain stable intentionally.
- [ ] Historical provenance references remain unchanged.
- [ ] Run Python syntax checks and Android Gradle compile/build before merge.

## Rollback

Revert this migration commit or close the pull request; do not delete or rewrite the
source branch history. If an ERIA APK has been distributed, remember that its
application ID is distinct from the former CodEXgen app ID.
