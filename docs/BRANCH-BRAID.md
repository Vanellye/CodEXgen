# Branch Audit and Counter-Clockwise Braid

**Repository:** `Vanellye/CodEXgen`  
**Audit snapshot:** 2026-11-09  
**Reference branch:** `main`  
**Working branch for this document:** `olpirt/stride-next`

## Safety and interpretation

This document is an inventory and logical integration map. It does **not** merge branches, move refs, delete branches, rewrite history, or imply that paired branches have identical content. Every original branch remains an independent source of truth until a separately reviewed integration change is approved.

“Counter-clockwise” is represented as a deterministic traversal order in this document. Git itself has no spatial direction; the order is a human-readable convention. Pairing means two preserved source branches occupy one logical display strand, not that their histories are combined.

## Eleven logical strands from thirteen branches

Starting at `fiction-mind`, traverse counter-clockwise in this order:

| Logical strand | Preserved source branch(es) | Traversal within pair |
|---:|---|---|
| 1 | `fiction-mind` + `fiction-body` | fiction-mind → fiction-body |
| 2 | `fiction-creation` + `hypotheticals` | fiction-creation → hypotheticals |
| 3 | `heroes-raw` | independent |
| 4 | `history` | independent |
| 5 | `main` | independent |
| 6 | `main-11-of-38` | independent |
| 7 | `mold` | independent |
| 8 | `olpirt/stride-next` | independent |
| 9 | `Vanellye-patch-1` | independent |
| 10 | `build-speed` | independent |
| 11 | `edify` | independent |

This is 11 logical display strands while retaining all 13 source branches. The pairings are presentation/integration candidates only. No source history is discarded.

## Branch relationship audit

Comparisons below are against `main`. “No common ancestor” means Git's compare endpoint could not establish a merge base; it is not, by itself, proof of defective code.

| Branch | Compare result | Audit note |
|---|---|---|
| `Vanellye-patch-1` | diverged; 1 ahead, 2 behind | Review uploaded change and its target context |
| `build-speed` | no common ancestor | Separate history; integration requires explicit ancestry/content review |
| `edify` | no common ancestor | Separate history; experimental ơ/ọ substitutions require validation; preserve load-bearing numeric zeros |
| `fiction-body` | no common ancestor | Latest commit message indicates a revert was reapplied; inspect full history before integration |
| `fiction-creation` | no common ancestor | Experimental zero-to-ơ transformation; do not apply to executable/build-critical values |
| `fiction-mind` | no common ancestor | Latest commit message indicates a revert was reapplied; inspect full history before integration |
| `heroes-raw` | no common ancestor | Latest commit says real versions were restored; validate build and content |
| `history` | diverged; 48 ahead, 2 behind | Large independent history; inspect merge topology and file-level overlap |
| `hypotheticals` | no common ancestor | Latest commit message indicates a revert was reapplied; inspect full history before integration |
| `main` | reference | Baseline for this snapshot |
| `main-11-of-38` | behind; 0 ahead, 2 behind | No unique commits ahead of `main` in this comparison |
| `mold` | no common ancestor | Build-critical ASCII zeros were restored per latest commit message; validate scripts and generated files |
| `olpirt/stride-next` | diverged; 237 ahead, 2 behind | Active development; latest audited CI run failed |

### Commit heads at audit time

| Branch | Head SHA |
|---|---|
| `Vanellye-patch-1` | `82bf021f91247c0ccd3d0830ce78957a6a91211e` |
| `build-speed` | `fbec48cff29207732b6a8d17511a9af84b84434e` |
| `edify` | `3faec1131c1c16a1640742f7b5c47ce96620ff67` |
| `fiction-body` | `6341d35bcc01a1ca8975555fb67ca989229c049c` |
| `fiction-creation` | `35dca4f01efffaf09f12f4123aeeda90c943bc47` |
| `fiction-mind` | `c501b3fe2ae3a75960885d4919e2be86a5708484` |
| `heroes-raw` | `a6f6f393b663ba2c706596a78c4cbed70432257d` |
| `history` | `e74ed223803df813077f22217c5649cfddb6b7f4` |
| `hypotheticals` | `dbd55dfd66ce2d03b81f9ec030ba0c1c93556e6e` |
| `main` | `6d32727955a95c3ff892ffc8322639697276d3a9` |
| `main-11-of-38` | `3056c8ab167d6e02d711d404f09b4b16f9097cd5` |
| `mold` | `f2a4e8baa36d3e9c345affa0e11cf02c6526d222` |
| `olpirt/stride-next` | `f6e0322761f216e32653067470c6e082da708ec2` |

## CI findings

Latest observed workflow run for `olpirt/stride-next` at the audited head:

- Run: [42705085552](https://github.com/Vanellye/CodEXgen/actions/runs/42705085552)
- Overall conclusion: **failure**
- Passing jobs: Pantheon native C++11 host tests; Python compatibility engines and tests; Geometry Laboratory browser automation; platform-independent framework C++11 contracts; Pantheon shared Node.js 11 runtime contract.
- Failing job: Android API 11 Views and C++11 JNI. Android SDK setup could not locate package `cmake;3.10.2`.
- Failing job: Android Views Java source compatibility. Compiler reported an invalid method declaration at `Api21WorkspaceTreeImporter.java:17` and malformed syntax/illegal backslash characters at `MainActivity.java:513`.

Combined commit-status queries returned zero status contexts for the 13 branch heads. This means no commit-status contexts were reported by that endpoint for those SHAs; it does **not** mean every branch passed CI. The available workflow listing showed the run above for `olpirt/stride-next`; branch-specific CI coverage for the other branches remains unverified.

## Integration gates

Before any actual merge or content weave:

1. Re-fetch every source ref and verify its SHA has not changed since this snapshot.
2. Compare paired branch trees and list overlapping paths.
3. Keep executable code, build configuration, tests, and data formats intact; do not replace numeric zero values or zero digits in load-bearing code.
4. Run branch-specific tests before considering a pair integrated.
5. Resolve conflicts in a new reviewable integration branch; never rewrite the source branch histories.
6. Require human approval for each consequential write and preserve an audit record.
7. If provenance, authorization, test evidence, or recovery is uncertain, stop in WARDEN rather than forcing the write.

## Protection snapshot

At audit time, all 13 listed branches reported `protected: false`, and the repository rulesets endpoint returned an empty list. This document does not change branch protection. Organization-wide enforcement must be configured by an authorized GitHub organization/repository administrator.

## Scope limitations

This is a point-in-time audit of the 13 branches in this repository. It is not an audit of every repository in a GitHub organization or personal account. The connected GitHub search at audit time exposed `Vanellye/CodEXgen`; additional private or organization repositories may not have been visible to that installation.
