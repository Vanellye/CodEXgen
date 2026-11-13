# ERIA / TRUE NORTH — Branch Implementation Status

**Snapshot:** 2026-11-10\
**Repository:** `Vanellye/CodEXgen` (historical remote name)\
**Scope:** Implementation wave 1. Branches remain independent; this record is not merge authorization.

> Orient by truth. Move by purpose. Never mistake momentum for direction.

## Integration rules

- Preserve each branch's commit ancestry, purpose, and branch-specific constraints.
- Apply contracts in the language and runtime already used by that branch.
- Keep raw values and provenance; do not silently repair malformed data.
- A successful signature, tag, CI run, or branch promotion does not authorize adoption.
- Prefer additive commits and pull requests. No branch was force-pushed, deleted, or merged as part of this implementation wave.
- The legacy hypothetical source `hypotheticals/bio_resonance_fiction.py` remains unchanged where present. CI verifies its pinned blob and compiles the remaining Python files separately.

## Branch-by-branch implementation record

| Branch | Implementation in this wave | Verification |
|---|---|---|
| `leveled-consciousness` | Python TRUE NORTH data-envelope package; strict schema, timestamp, provenance, authorization, quality, canonical bytes and SHA-256; seven tests | [CI success](https://github.com/Vanellye/CodEXgen/actions/runs/42736501019) |
| `main` | ERIA Kotlin data envelope, JUnit tests, Android unit-test gate before APK build | [CI success](https://github.com/Vanellye/CodEXgen/actions/runs/42738273668) |
| `main-11-of-38` | Kotlin data envelope and JUnit tests; preserved quarantined legacy source in CI | [CI success](https://github.com/Vanellye/CodEXgen/actions/runs/42738537701) |
| `build-speed` | Kotlin data envelope and JUnit tests; Android unit-test and APK gates | [CI success](https://github.com/Vanellye/CodEXgen/actions/runs/42736752617) |
| `Vanellye-patch-1` | Kotlin data envelope and JUnit tests; CI now preserves the quarantined legacy file and tests non-quarantined sources | [CI run](https://github.com/Vanellye/CodEXgen/actions/runs/42739575106) — Android build in progress at snapshot |
| `edify` | Kotlin data envelope and JUnit tests; CI quarantine check added | [CI run](https://github.com/Vanellye/CodEXgen/actions/runs/42739580501) — Android build in progress at snapshot |
| `heroes-raw` | Kotlin data envelope and JUnit tests; CI quarantine check added | [CI run](https://github.com/Vanellye/CodEXgen/actions/runs/42739587832) — Android build in progress at snapshot |
| `history` | Kotlin data envelope and JUnit tests; CI quarantine check added | [CI run](https://github.com/Vanellye/CodEXgen/actions/runs/42739598013) — Android build in progress at snapshot |
| `knowledge-recycle-foundation` | Kotlin data envelope and JUnit tests | [CI success](https://github.com/Vanellye/CodEXgen/actions/runs/42738910277) |
| `mold` | Kotlin data envelope and JUnit tests | [CI success](https://github.com/Vanellye/CodEXgen/actions/runs/42738951976) |
| `cognitive-layer-2` | Append-only memory entries map into the shared envelope with UNKNOWN evidence quality and no action authorization; CI preserves the legacy quarantine | [CI run](https://github.com/Vanellye/CodEXgen/actions/runs/42739317301) — Python tests passed; Android build in progress |
| `hypotheticals` | Explicit hypothesis record contract; assumptions, unknowns, source and unvalidated status preserved; maps to UNKNOWN, non-authorizing envelope | [CI success](https://github.com/Vanellye/CodEXgen/actions/runs/42739003957) |
| `fiction-body` | Branch-bound fiction artifact provenance; cannot self-promote to empirical evidence | [CI success](https://github.com/Vanellye/CodEXgen/actions/runs/42736851594) |
| `fiction-creation` | Branch-bound fiction artifact provenance; cannot self-promote to empirical evidence | [CI success](https://github.com/Vanellye/CodEXgen/actions/runs/42736860914) |
| `fiction-mind` | Branch-bound fiction artifact provenance; cannot self-promote to empirical evidence | [CI success](https://github.com/Vanellye/CodEXgen/actions/runs/42736841640) |
| `integration/channel-router-main` | Strict finite canonical JSON payload encoding; preservation tests for zero, false, null and empty values | [CI success](https://github.com/Vanellye/CodEXgen/actions/runs/42737519272) |
| `integration/git-freedom-router` | Read-only workspace URI permission; full preflight conflict scan; exclusive file creation; pure-Java import-policy tests | [CI success](https://github.com/Vanellye/CodEXgen/actions/runs/42738002074) |
| `olpirt/stride-next` | C++11 data-envelope contract and CTest target; shared in-memory SQLite fix for JOB store; regression test | [CI success](https://github.com/Vanellye/CodEXgen/actions/runs/42737110372) — CTest 3/3 passed; Python reference tests passed |
| `pantheon/divergence-adoption` | Adoption workflow now opens a review-only PR; no auto-merge; receiver approval remains a separate gate; quarantined source preserved | [Branch Horizon CI success](https://github.com/Vanellye/CodEXgen/actions/runs/42737618679) · [Independent CI success](https://github.com/Vanellye/CodEXgen/actions/runs/42737618608) |
| `pantheon/source-digest-engine` | Versioned source catalog manifest with canonical SHA-256 digest and provenance counts | [CI success](https://github.com/Vanellye/CodEXgen/actions/runs/42737478432) |
| `pantheon/signed-package-exchange` | Read-only Ed25519 package verifier with external key fingerprint pinning, canonical manifest, file inventory, path/symlink rejection and resource limits | [CI success](https://github.com/Vanellye/CodEXgen/actions/runs/42739158457) |
| `pantheon/cpp-html-consent-engine` | Kotlin data envelope and JUnit tests; CI quarantine guard added | [CI run](https://github.com/Vanellye/CodEXgen/actions/runs/42739634457) — pending at snapshot |

## Reviewed without copying code

| Branch | Assessment |
|---|---|
| `pantheon/branch-horizon` | Existing read-only branch comparison and review workflow already fit the no-automatic-adoption boundary. Its branch CI passed: [run](https://github.com/Vanellye/CodEXgen/actions/runs/42735454183). |
| `repair/quarantine-legacy-python-syntax` | Quarantine/repair documentation branch; no additional shared runtime code copied. |
| `review/legacy-syntax-quarantine` | Review-focused branch; preserve its distinct review scope rather than importing unrelated runtime code. |
| `review/two-snapshot-synthesis` | Snapshot/provenance documentation branch; no active shared runtime interface identified in this pass. |
| `zero-dissipation-anchor` | Governance/audit documentation branch; no distinct executable interface identified in this pass. |

## Explicit limitations

- Kotlin validation checks envelope metadata and JSON-compatible payload values; it is not a complete serializer or authorization engine.
- The C++11 envelope preserves payload JSON text verbatim; parsing and canonical serialization remain host-adapter responsibilities.
- The Git Freedom importer prevents overwrite but is not a whole-tree transaction. A provider failure may leave newly created files from earlier in the import.
- The signed-package verifier handles directory bundles only. It does not implement archive extraction, sandboxing, dependency resolution, receiver approval UI, installation, activation, or rollback.
- Fiction and hypothesis labels prevent classification drift in these record types; they do not assess scientific truth.
- CI proves only the paths and tests actually executed.

## Next wave

1. Complete outstanding Android unit-test and APK jobs on the branches marked in progress.
2. Review the remaining documentation/audit branches for any new executable interfaces before changing them.
3. Add branch-specific adapters only where the actual source tree supports them.
4. Record every test result, limitation, and reviewer decision before proposing any cross-branch integration.

**TRUE NORTH is a reference, not a command to converge.**
