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


## Refresh: repository-wide accessible scope and current CI snapshot

This refresh supersedes earlier head-SHA, ahead/behind, and CI-run details above where they differ.

### Accessible repository inventory

The connected GitHub installation search for `Vanellye` returned one accessible repository: `Vanellye/CodEXgen` (public, not archived, default branch `main`). GitHub identifies `Vanellye` as a **User** owner, not an Organization. This is the full scope visible to the current connection at this time, not proof that no other private or organization repositories exist outside its permissions.

The repository exposes 13 branches. No repository or branch was removed or modified by this audit, other than this report update on `olpirt/stride-next`.

### Current branch relationship refresh

Against `main`, `olpirt/stride-next` is now 238 commits ahead and 2 behind, with merge base `3056c8ab167d6e02d711d404f09b4b16f9097cd5`. Its current head before this report refresh was `f501acaa6834728999260bcc1abe6f68383fe30e`.

Eight branches have no common ancestor with `main`: `build-speed`, `edify`, `fiction-body`, `fiction-creation`, `fiction-mind`, `heroes-raw`, `hypotheticals`, and `mold`. Each inspected head commit has a parent, so the evidence supports **unrelated branch histories relative to main**, not a claim that the branch refs are dangling or that the commits are parentless orphan objects.

The other branch comparisons remain:
- `Vanellye-patch-1`: diverged, 1 ahead / 2 behind.
- `history`: diverged, 48 ahead / 2 behind.
- `main-11-of-38`: behind, 0 ahead / 2 behind.
- `olpirt/stride-next`: diverged, 238 ahead / 2 behind.

### Pair-level braid compatibility

The two approved pairs do have a common ancestor with each other, despite lacking a common ancestor with `main`:

| Pair traversal | Pair comparison | Merge base | Changed paths reported |
|---|---|---|---|
| `fiction-mind` → `fiction-body` | diverged, 4 ahead / 4 behind | `3b56b72f2b5e9485f9167e3e6558a1be31af1b84` | `hypotheticals/body_fiction.py`; `hypotheticals/resonance_noise_fiction.py` |
| `fiction-creation` → `hypotheticals` | diverged, 4 ahead / 5 behind | `3b56b72f2b5e9485f9167e3e6558a1be31af1b84` | `hypotheticals/BRIDGE.md`; `hypotheticals/resonance_noise_fiction.py` |

Both pairs touch `hypotheticals/resonance_noise_fiction.py`, a concrete overlap requiring manual reconciliation before any future integration. This is a review warning, not an instruction to merge. Keep the branch refs separate.

### Current CI/check coverage at audited heads

The latest workflow run on `olpirt/stride-next` is [42706993755](https://github.com/Vanellye/CodEXgen/actions/runs/42706993755), for commit `f501acaa6834728999260bcc1abe6f68383fe30e`. Seven checks were reported: five passed and two failed.

Failed:
- Android API 11 Views and C++11 JNI: SDK setup warning, `Failed to find package 'cmake;3.10.2'`.
- Android Views Java source compatibility: `Api21WorkspaceTreeImporter.java:17` invalid method declaration; `MainActivity.java:513` has a missing parenthesis, illegal backslash characters, and cascading syntax errors.

Passed:
- Pantheon shared Node.js 11 runtime contract.
- Python compatibility engines and tests.
- Platform-independent framework C++11 contracts.
- Pantheon native C++11 host tests.
- Geometry Laboratory browser automation.

Check-run inventory for the 13 branch heads:
- `olpirt/stride-next`: 7 checks (5 success, 2 failure).
- `build-speed`: 1 check (`prebuild`, success).
- The other 11 branch heads: 0 check runs returned by the GitHub check-runs endpoint.

Zero returned check runs means no check-run evidence was attached to those commit heads at the time of inspection; it does not establish that no local tests were ever run. This is a **missing CI evidence** risk for 11 branches. The `main` head also returned zero check runs and zero legacy commit-status contexts.

### Integration and policy risks surfaced

1. **Unrelated ancestry:** eight branches cannot be compared to `main` with a merge base. A content-level import/reconciliation plan is needed; do not use an automatic unrelated-histories merge as a shortcut.
2. **Pair overlap:** both approved pairs modify `hypotheticals/resonance_noise_fiction.py`; resolve semantics and tests before any future splice.
3. **CI gaps:** 11 branch heads have no check runs; only `build-speed` has one passing prebuild check outside the active branch.
4. **Android blockers:** the active branch's Android toolchain package and Java source failures prevent a verified Android build.
5. **Branch governance:** all 13 branches report `protected: false`; repository rulesets endpoint returned an empty list. This audit did not alter protection. Lack of protection raises accidental-write risk.
6. **Incomplete organization scope:** the connector exposes one public user-owned repository, not a confirmed complete organization inventory.

### Current braid remains a logical map only

The approved 11-strand order remains:
1. `fiction-mind` + `fiction-body`
2. `fiction-creation` + `hypotheticals`
3. `heroes-raw`
4. `history`
5. `main`
6. `main-11-of-38`
7. `mold`
8. `olpirt/stride-next`
9. `Vanellye-patch-1`
10. `build-speed`
11. `edify`

The two pairs are two-at-a-time logical strands; all 13 source branch refs remain independent and preserved. No branch merge, force-push, deletion, ref movement, or protection-setting change was performed.


## Branch ecology: evidence leaves, toxin warnings, and directional directives

This section translates the branch-ecology metaphor into explicit, reviewable repository signals. It is a **design directive**, not a claim that a scan has already found malware, compromised dependencies, or malicious contributors. No branch is deleted or rewritten by this model.

### 1. Leaves: evidence that can wither and fall

A branch's “leaves” are its attached evidence records: CI results, test reports, dependency inventories, security scan results, code review approvals, provenance attestations, and integration notes.

Each leaf must carry:
- source branch and exact commit SHA;
- evidence type and producing tool/workflow;
- timestamp and, where applicable, expiry/freshness window;
- result (pass, fail, warning, unavailable);
- link to the raw report or workflow run;
- scope (which files, packages, targets, and platforms were actually checked).

Lifecycle:
- **Fresh leaf:** evidence matches the current branch head and is inside its declared freshness window.
- **Withering leaf:** the branch head moved, the evidence aged beyond its freshness window, or the evidence does not cover the changed files/platform. Keep it visible but mark it stale.
- **Fallen leaf:** the evidence is superseded or expired. Move it out of the active-health summary into an immutable historical record; do not erase the audit trail.
- **Bare branch:** no applicable evidence is attached. Show “unknown / unchecked,” never green by default.

A new commit invalidates head-specific CI and review leaves unless the workflow explicitly proves the evidence still applies. Historical success must not be presented as current success.

### 2. Toxin warnings: detect, contain, and prove

A “toxin” is a verified or suspected risk signal in branch content or its supply chain. The warning must identify evidence and confidence; metaphor alone is not a finding.

Check categories:
- exposed credentials, tokens, private keys, or accidental secret material;
- known vulnerable or unpinned dependencies and unsafe dependency sources;
- suspicious build scripts, install hooks, generated binaries, or opaque downloaded artifacts;
- unsafe deserialization, command execution, path traversal, injection, or permission-boundary bypass;
- unexpected network egress, telemetry, data export, or changes to authentication/authorization;
- license/provenance gaps and unreviewed third-party code;
- tests removed, weakened, skipped, or made non-deterministic around sensitive behavior.

Warning levels:
- **Red — confirmed:** reproducible scanner/test evidence or manually verified exploitable issue. Block promotion of the affected content; preserve the branch and its evidence.
- **Amber — suspected:** credible signal needing human triage. Hold integration until resolved or explicitly risk-accepted.
- **Grey — unknown:** scanner unavailable, scope incomplete, or no result. Do not interpret as clean.
- **Green — checked:** named checks completed against the exact head with no finding in their stated scope. Green is scoped evidence, not a universal safety guarantee.

Do not call a branch “toxic” based only on its name, theme, commit message, or divergence. Record the finding, affected path/dependency, evidence, severity, confidence, owner, and remediation status. If a confirmed issue appears, quarantine the affected artifact or integration candidate in a separate review workflow; retain the source branch and history. Revoke exposed credentials through their issuing service, not by merely deleting a line from Git history.

### 3. Reaching: show where each branch can lead

For each branch, compute and display its **reach** as a graph of:
- ancestry reach: merge base, ahead/behind counts, unrelated-history state;
- content reach: files and components it changes;
- dependency reach: modules, libraries, build targets, workflows, and platforms affected;
- integration reach: branches or release targets that could receive its content;
- risk reach: downstream components exposed by a confirmed or suspected finding.

Every edge must state its evidence and direction. A branch that changes a shared file or dependency can have a wider reach than its commit count suggests. No inferred reach should be treated as an actual merge or deployment.

### 4. Branch directives: give each strand a clear direction

Each branch receives a machine-readable directive with a rationale and exit criteria:

| Directive | Meaning | Exit condition |
|---|---|---|
| **GROW** | Continue isolated development and add missing tests/evidence | New head has fresh checks and reviewed scope |
| **REACH** | Map downstream dependencies and integration consumers | Impact graph and owners reviewed |
| **HOLD** | Stop promotion while evidence, CI, ancestry, or conflict is unresolved | Required evidence and approvals exist |
| **WARDEN** | Fail closed when authorization, provenance, integrity, or safety is uncertain | Human review resolves the uncertainty |
| **REPAIR** | Address a reproducible defect or confirmed security finding in a reviewable change | Fix and regression tests pass |
| **BRAID-CANDIDATE** | Eligible for content-level reconciliation with its named pair | Pair overlap resolved; tests and approvals complete |
| **PROMOTION-CANDIDATE** | Eligible for a separately approved target-branch review | All required gates pass; target owner approves |

A directive never authorizes a merge, push, deletion, force update, or protection-setting change. It describes the next safe action only.

### 5. Initial directives from the evidence currently available

These are provisional triage directions, not security scan results:

| Branch / strand | Initial directive | Reason |
|---|---|---|
| `fiction-mind` + `fiction-body` | **BRAID-CANDIDATE + HOLD** | Pair diverged 4/4; shared file overlap needs reconciliation; no head check runs |
| `fiction-creation` + `hypotheticals` | **BRAID-CANDIDATE + HOLD** | Pair diverged 4/5; shared file overlap needs reconciliation; no head check runs |
| `build-speed` | **REACH + HOLD** | No common ancestor with main; only one passing prebuild check; inspect build configuration impact |
| `edify` | **WARDEN + HOLD** | Unrelated history and no check runs; validate all executable/data-format changes |
| `heroes-raw` | **REPAIR / VERIFY + HOLD** | Unrelated history and no check runs; validate restored content and build behavior |
| `history` | **REACH + HOLD** | 48 commits ahead and 2 behind; inspect broad ancestry and file-level impact |
| `main` | **WARDEN / BASELINE** | Baseline head has no reported check runs; do not assume verified health |
| `main-11-of-38` | **REACH + HOLD** | Two commits behind main; establish whether it has any still-needed content before promotion |
| `mold` | **WARDEN + HOLD** | Unrelated history and no check runs; verify build-critical values and scripts |
| `olpirt/stride-next` | **REPAIR + HOLD** | Two current Android CI failures; five platform-independent checks pass |
| `Vanellye-patch-1` | **REACH + HOLD** | Diverged 1/2; inspect its five changed paths and confirm intended target |

No current toxin scan result is available in this audit. Therefore toxin status for every branch is **GREY / UNKNOWN**, not clean and not confirmed compromised.

### 6. Minimum evidence leaf set before a strand can advance

- reproducible build/test results for the branch's changed targets;
- secret scanning and dependency vulnerability scanning at the exact head;
- static analysis appropriate to the languages touched;
- provenance and license review for introduced third-party artifacts;
- diff/overlap review for paired strands;
- explicit downstream reach map;
- human approval recorded against the exact commit SHA.

The evidence dashboard should show stale, fallen, missing, failed, and passed leaves distinctly. It must never hide a failure by averaging it with passing checks.

### 7. Preservation invariant

Leaves may wither, fall out of the active view, and be replaced by fresher evidence. Branch refs and commit history remain intact. “Prune” means remove unsafe content from a future integration candidate or isolate an artifact under review—not delete the original branch. All directives remain advisory until a separately authorized operation is approved.


## Engineering phase update — pair plan and independent CI

**Updated:** 2026-11-09

### File-level integration plan published

A separate, reviewable plan is available at [`docs/PAIR-INTEGRATION-PLAN.md`](PAIR-INTEGRATION-PLAN.md), committed on `olpirt/stride-next` as `afbafa57c08c03cdc447da30620efe045c8d6ffe`.

The plan records:
- Pair 1: `body_fiction.py` is additive on `fiction-body`; the shared resonance module has different deterministic seed identities on `fiction-mind` and `fiction-body`.
- Pair 2: `BRIDGE.md` is additive on `hypotheticals`; the shared resonance module has different deterministic seed identities on `fiction-creation` and `hypotheticals`.
- Cross-pair collision: all four strands converge on `hypotheticals/resonance_noise_fiction.py`. The proposed resolution is one shared module with explicit strand identities and a separate display-only formatter for `ơ`; raw binary output and numeric zeros remain intact.
- Required tests cover deterministic output, output length, strand identity, binary alphabet invariants, and marker formatting.

This is a file-level design and provenance plan only. No content from the four source branches has been merged or copied into another source branch.

### Independent CI workflows added

The new `.github/workflows/independent-branch-ci.yml` workflow was committed as an ordinary additive commit to each of the 11 branch heads that previously had no check runs:

| Branch | Workflow commit |
|---|---|
| `Vanellye-patch-1` | `cf732a008b5642243ab5e4133a5ce882f6513dca` |
| `edify` | `82e92324383bbcd02e2a3a938e8d7e4dbff4d837` |
| `fiction-body` | `71ab22da2f04c2b58171e1bafe889cc524a0ed61` |
| `fiction-creation` | `63d398d8ecad5e686b5570023c065f89e2918790` |
| `fiction-mind` | `ef62753230622ccbe755e560b0c49b268b882127` |
| `heroes-raw` | `6dbb03dc9f2b79d8d791a34b5964d7fd031dfa0c` |
| `history` | `362c7192692d5c48bec1e7374287fb32d3552c6a` |
| `hypotheticals` | `860fc3e26e147da1aa4ee38659676830ad0ec099` |
| `main` | `a02629956deda7db4416cdbb1bc9b3c5badf90a0` |
| `main-11-of-38` | `9ed3ca42e3e9b8862f019bc4069e36d6aafc1380` |
| `mold` | `11736208aa6c8288a59601da4cce2b841989ff9e` |

The workflow runs three independent jobs:
1. Git object connectivity and committed whitespace validation.
2. Python syntax compilation, plus unittest discovery if a `tests/` directory exists.
3. Android debug APK build using JDK 17, Android platform 35/build-tools 35.0.0, and the branch's Gradle wrapper.

The workflow is present at each of those branch tips and GitHub Actions created one run for each branch. At the time this update was prepared, those 11 runs were still in progress; no pass/fail conclusion is claimed here. Results must be inspected before treating any branch as verified.

The workflow does not replace the existing platform CI on `olpirt/stride-next`. `build-speed` was not modified because its head already had one successful `prebuild` check run; it still has no branch-local workflow file in the inspected tree and should receive broader coverage in a later pass if needed.

### Preservation and write ledger

- 11 existing branch refs received one new ordinary commit adding the CI workflow; no existing commit was amended, rebased, or force-updated.
- The four fiction source branches retain their prior content and histories; only the CI workflow file was added to their tips.
- The plan was added as a new document on `olpirt/stride-next`.
- No merge commits, content splices, branch deletions, force pushes, or protection-setting changes were made.
- Original branch names and prior commits remain available for inspection. The added workflow commits advance branch heads but do not rewrite their histories.


### First independent CI results — 11 branch heads

All 11 newly added workflows were triggered. At the time of this results refresh, all 11 completed.

**Results:**
- Source integrity / whitespace: **11/11 passed**.
- Android debug APK build: **11/11 passed**.
- Python syntax compilation: **5/11 passed; 6/11 failed**.
- No `tests/` directory was present on these inspected branch trees, so unittest discovery did not execute a project unit-test suite.

Overall workflow result: **5 branches passed all jobs; 6 branches failed the Python syntax job**. The Android debug build and Git integrity checks passed on every branch.

| Branch | Workflow result | Run |
|---|---|---|
| `Vanellye-patch-1` | failure — Python syntax | [42709791717](https://github.com/Vanellye/CodEXgen/actions/runs/42709791717) |
| `edify` | failure — Python syntax | [42709796729](https://github.com/Vanellye/CodEXgen/actions/runs/42709796729) |
| `fiction-body` | success | [42709801094](https://github.com/Vanellye/CodEXgen/actions/runs/42709801094) |
| `fiction-creation` | success | [42709806342](https://github.com/Vanellye/CodEXgen/actions/runs/42709806342) |
| `fiction-mind` | success | [42709811894](https://github.com/Vanellye/CodEXgen/actions/runs/42709811894) |
| `heroes-raw` | failure — Python syntax | [42709828670](https://github.com/Vanellye/CodEXgen/actions/runs/42709828670) |
| `history` | failure — Python syntax | [42709834083](https://github.com/Vanellye/CodEXgen/actions/runs/42709834083) |
| `hypotheticals` | success | [42709842087](https://github.com/Vanellye/CodEXgen/actions/runs/42709842087) |
| `main` | failure — Python syntax | [42709847269](https://github.com/Vanellye/CodEXgen/actions/runs/42709847269) |
| `main-11-of-38` | failure — Python syntax | [42709852964](https://github.com/Vanellye/CodEXgen/actions/runs/42709852964) |
| `mold` | success | [42709860085](https://github.com/Vanellye/CodEXgen/actions/runs/42709860085) |

The six Python failures point to `hypotheticals/bio_resonance_fiction.py:27`, where the expression `int(level * 2ơ)` is invalid Python syntax. The character `ơ` is being used inside a numeric expression rather than as a string/display marker. This is a reproducible syntax defect in those six branch snapshots. It has **not** been automatically rewritten: a fix should preserve numeric semantics and keep visual markers at the presentation boundary.

The five passing branches are not thereby proven secure or fully tested. Their Python syntax, Git integrity, and Android debug build passed the stated workflow scope; no dedicated Python unit tests, secret scan, dependency audit, or full release build was run by this workflow.

### Next repair gate

1. Review the six affected `bio_resonance_fiction.py` variants and identify whether the intended operation is numeric multiplication or string formatting.
2. Propose a minimal fix that keeps the numeric factor numeric and moves `ơ` into an output formatter, if that is the intended presentation.
3. Add tests before changing any of the six branch contents.
4. Apply fixes only through separate reviewable commits after approval; do not rewrite history.
5. Re-run independent CI and verify all 11 branches again.
