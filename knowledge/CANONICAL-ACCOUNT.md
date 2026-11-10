# CodEXgen — Canonical Account

**Record version:** 1.0  
**Repository:** \`Vanellye/CodEXgen\`  
**Record status:** canonical working account; additive and reviewable  
**Snapshot reference:** \`knowledge/branch-head-snapshot-2026-11-10T011800Z.json\`  
**Snapshot time:** 2026-11-10 01:18 UTC  
**Default branch observed:** \`main\`  
**Main head observed:** \`67ecdb5c5bd148b6fd7c9945fa648f3c89a93a95\`

## 1. What this account is

This document is the repository-level account of CodEXgen: its governing principles, major workstreams, branch identities, verified integration points, historical decisions, known risks, and unfinished questions.

It is an index and synthesis, not a replacement for branch histories, original files, commit objects, author intent, or contributor decisions. The source branch remains the authority for its own contents. This account records what was observed and where the evidence lives.

**Main is a meeting point and shared index. Main does not own the branches, their identities, their histories, or their unadopted work.** A branch can be related to another without being absorbed by it.

## 2. Canonical preservation covenant

> Preserve the origin. Map the connections. Test the peering. Let every branch retain its identity.

CodEXgen's operating principles, as expressed across the repository work and project decisions:

- Adapt without abandoning integrity.
- Innovate without overriding consent.
- Learn without rewriting history.
- Evolve without erasing what came before.
- Do not confuse progress with permission, innovation with authority, or change with erasure.
- Preserve original source and provenance; store corrections, interpretations, and generated summaries separately.
- Treat unknown as unknown. Do not silently repair, infer missing values, or guess authorial intent.
- A passing build proves only the checks actually run against that exact commit and environment.
- A signature establishes integrity/authenticity within its trust model; it does not establish safety, correctness, or permission to install/adopt.
- Observation is not permission. Absence is not consent. A tag identifies; it does not authorize adoption.
- Consequential writes, exports, promotions, merges, and propagation require explicit authorization and a reviewable path.
- Reversibility, recovery instructions, and clear conditions for clearing warnings belong in the record.
- A workflow should carry the work, not command the worker.

The Warden governs the boundary between existence, absence, and adoption; it does not own either side of that boundary.

## 3. Repository identity and current observed state

At the recorded snapshot, GitHub returned 27 branch refs. Their exact names and head SHAs are preserved in the accompanying JSON snapshot. That file is the point-in-time ref record; it does not imply a complete semantic review of all 27 branches.

The current snapshot differs from the first-pass register in at least these observed heads:

| Branch | Earlier register snapshot | Current observed head |
|---|---|---|
| \`knowledge-recycle-foundation\` | \`4227381c9ebfab486d7773f8fdc7a82b0a0993fa\` | \`ab1cd44ac9260c69742fd88ea4e27f6bf9eb1c59\` |
| \`pantheon/branch-horizon\` | \`7b3de5ecf47a64bd3039b97c6a920f5d6b6f41c7\` | \`93545f384490bf77821722b49f5de361a7597a5d\` |
| \`pantheon/divergence-adoption\` | \`bdb4c8dae89140743ec06e6f4ce48774b2617d2c\` | \`057b100077129dd54fa29a4a31f71b8f9ad6474f\` |

These are new observations, not silent edits to the earlier snapshot. The first-pass \`knowledge/BRANCH-BY-BRANCH-REGISTER.md\` remains a historical inventory with its original captured SHAs. The new snapshot is the newer ref observation.

### Branch families (organizational labels, not ownership or merge instructions)

- **Core / history / preservation:** \`main\`, \`main-11-of-38\`, \`history\`, \`heroes-raw\`, \`Vanellye-patch-1\`.
- **Creation and hypothetical work:** \`fiction-body\`, \`fiction-creation\`, \`fiction-mind\`, \`hypotheticals\`, \`mold\`.
- **Learning and cognition:** \`edify\`, \`cognitive-layer-2\`, \`leveled-consciousness\`, \`knowledge-recycle-foundation\`.
- **Stride:** \`olpirt/stride-next\`.
- **Git and channel integration:** \`integration/git-freedom-router\`, \`integration/channel-router-main\`.
- **Pantheon / governance / peering:** \`pantheon/branch-horizon\`, \`pantheon/cpp-html-consent-engine\`, \`pantheon/divergence-adoption\`, \`pantheon/signed-package-exchange\`, \`pantheon/source-digest-engine\`, \`zero-dissipation-anchor\`.
- **Repair and review candidates:** \`repair/quarantine-legacy-python-syntax\`, \`review/legacy-syntax-quarantine\`, \`review/two-snapshot-synthesis\`.
- **Build performance:** \`build-speed\`.

A family label is only a navigation aid. It does not claim shared ancestry, compatibility, readiness, or authority.

## 4. Major workstreams and what they establish

### 4.1 Android / CodeGen application foundation

PR #1 introduced an Android Gradle/Compose project structure and UI/view-model foundations, plus Python-side cleanup and tooling. Its PR description reports a debug build using AGP 8.7.3, Kotlin 2.0.21, Gradle 8.9, Compose BOM 2024.10.01, compile SDK 35, and min SDK 24.

**Evidence boundary:** PR #1 is merged. The PR's build statement is a historical PR claim; it is not a fresh device test. A generated Compose mirror and unresolved model references were recorded as debt. Do not equate a successful build with production readiness or device compatibility.

### 4.2 Stride — temporal records, context, and reconciliation

The \`olpirt/stride-next\` line contains distinct work on:

- Append-only JOB correction proposals and review decisions.
- Read-only reconciliation that derives a corrected view without altering original events.
- Explicit authorization before proposing corrections.
- Temporal conflict visibility and retained review history.
- Holified Inception as a read-only contextual reader that links observations and concepts while leaving unresolved links unresolved and labeling creative combinations as hypotheses.
- Consent-aware context mapping and independent subsystem boundaries.

Important implementation references recorded in prior branch work include:

- \`python/stride_core/job_reconciliation.py\` — commit \`7169c2666ab1b88fbc81479b1c57c9dbcd68e03b\`.
- \`tests/test_job_reconciliation.py\` — commit \`c97d3d4e5ab0bd9e75fa2e88bac0efd2b790e40c\`.
- \`docs/TEMPORAL-RECONCILIATION.md\` — commit \`6b3d694bd9dedc31170a01060f07642120640019\`.
- \`python/stride_core/holified_inception.py\` — commit \`602bd51f456463e28855c952a21916a78d69c097\`.
- \`tests/test_holified_inception.py\` — commit \`6df063b7d41721d94738804aac1521e4474b0dba\`.

**Evidence boundary:** These references identify branch-local implementation and test artifacts. They do not establish current cross-branch integration, external discovery, sentience, or the factual correctness of generated associations.

### 4.3 Git Freedom Bridge

PR #9 is an isolated review candidate on \`integration/git-freedom-router\`. It adds Java Git bridge components, a token vault, a Storage Access Framework workspace importer, and a pinned JGit dependency.

Recorded safety design includes fast-forward-only pull, configured feature-branch push targeting, dirty-worktree rejection, no force-push path, and current-branch checks around Git mutations.

Open review concerns include:
- Vault cryptographic construction and provider compatibility.
- Inconsistent passphrase length rules.
- Whether all local file writes are protected by branch authorization.
- Workspace import overwrite/conflict preview.
- Token lifecycle and in-memory unlocked-token handling.
- TLS and transport behavior on real Android devices.

**Current state:** PR #9 is open and draft. The current commit status endpoint returned no statuses (pending, zero contexts) when checked. Do not claim Android compilation or device validation for this PR. No Kotlin UI wiring or automatic merge into \`main\` is claimed.

### 4.4 Pantheon — boundaries, branch observation, and package peering

The Pantheon workstream includes separable ideas and artifacts:

- **Branch Horizon:** bounded, read-only observation of exact branch heads and review signals. Lexical similarity is not compatibility proof.
- **Warden Principle:** observation, absence, tags, and branch identity do not confer adoption authority.
- **Divergence adoption:** a proposal for narrow, opt-in, exact-SHA-bound, staged, PR-based adoption. The documented proposal says it is not active until the workflow is merged into the default branch.
- **Signed package exchange:** a design specification separating signature verification, policy checks, receiver review, explicit approval, staging, validation, and installation. It is not an implementation claim.
- **Source Digest:** a specification for local-first, non-executing source inspection, metadata catalogs, and content hashes, with refusal of silent output replacement.
- **C++/HTML consent engine:** an independently identified branch; its current implementation and compatibility require a dedicated audit before any adoption claim.

These components may peer through explicit, tested interfaces. They are not a single proven integrated system merely because their designs are related.

### 4.5 Knowledge, Edify, and learning records

The knowledge foundation turns selected repository artifacts into source-linked lessons while preserving the distinction between originals and derived learning.

Current additive artifacts on this work branch:
- \`knowledge/EDIFYING-KNOWLEDGE-FOUNDATION.md\` — purpose, evidence labels, record model, review lifecycle, and boundaries.
- \`knowledge/seed-catalog.json\` — seven initial records.
- \`knowledge/branch-lessons.json\` — twelve branch-linked lesson records.
- \`knowledge/BRANCH-BY-BRANCH-REGISTER.md\` — first-pass 27-branch inventory.
- \`knowledge/branch-head-snapshot-2026-11-10T011800Z.json\` — refreshed 27-ref point-in-time snapshot.
- This document — repository-level canonical account.

The \`edify\` branch's transformation policy remains branch-local. Its scope and relationship to altered numeric glyphs elsewhere are unresolved. No global text or numeric transformation is authorized by this account.

### 4.6 Fiction, hypotheticals, and scientific boundaries

The fiction branches and \`hypotheticals\` preserve creative exploration. Fictional biological mechanisms, simulated signals, or metaphorical language are not empirical evidence, validated medical mechanisms, or executable biological instructions.

The malformed source \`hypotheticals/bio_resonance_fiction.py\` remains byte-for-byte preserved and quarantined from syntax compilation by an exact blob-hash check. The malformed expressions are recorded verbatim; no numeric replacement or intended semantics are guessed. A build passing around that one quarantined file does not mean the file compiles.

### 4.7 Build and CI

Historical independent-branch CI and branch audit records show that validation has differed by branch and by commit. A result belongs only to the exact SHA, workflow, environment, and checks actually run.

PR #17's current head \`ab1cd44ac9260c69742fd88ea4e27f6bf9eb1c59\` has three completed successful jobs:
- Source integrity and whitespace.
- Android debug APK build.
- Python syntax and available unit tests, including the exact legacy-source hash check and compilation of non-quarantined Python files.

This does not certify all 27 branches, all application behavior, all device environments, or every feature.

## 5. Verified integration and decision history

| Change | Observed disposition | What it means |
|---|---|---|
| PR #1 — Android project restructure/build | Merged | Android project structure and related changes entered the recorded PR #1 merge line. |
| PR #10 — two-snapshot synthesis | Merged | Snapshot comparison and provenance principles were documented. |
| PR #16 — legacy syntax quarantine | Merged | CI pins the original malformed fictional source and excludes only that exact file from syntax compilation; the source itself is not repaired. |
| PR #17 — knowledge foundation | Open, draft; CI successful at current head | Additive knowledge records and branch inventory are under review; not merged. |
| PR #9 — Git Freedom router | Open, draft; current status endpoint has no contexts | Isolated integration candidate; security and runtime review remain. |
| PR #8 — legacy syntax review note | Open, draft; stale review candidate | Distinct historical review artifact; PR #16 later added the quarantine to main. Inspect before closing or changing; do not assume it is redundant without reviewing its exact diff and history. |

### Snapshot ancestry warning

The two-snapshot synthesis documented that the Stride and Main snapshots were divergent at the compared points. Earlier GitHub compare requests also reported no common ancestor for the specific PR #1/current-main comparisons. Identical file blobs were used to preserve matching Android implementation, not to invent shared ancestry. The cause of disconnected history was not established. Preserve the commit graph and report ancestry only when Git evidence supports it.

## 6. Seven seeds — conceptual framework

The seven seeds are a conceptual framework, not required software execution order or a claim that all seven layers are implemented:

1. **Foundation — Being**
2. **Awareness — Perception**
3. **Knowledge — Learning**
4. **Creation — Imagination**
5. **Harmony — Connection**
6. **Stewardship — Responsibility**
7. **Infinite Main — Becoming**

Treat these as independent perspectives or portals unless a future, explicit design decision defines dependencies. No seed should silently become a mandatory gateway or authority over another.

## 7. Data, memory, correction, and adoption rules

### Records
- Keep source records immutable in the historical sense: never rewrite them to match a later interpretation.
- Store corrections as linked records with author, time, exact source reference, proposed value, evidence, rationale, and review state.
- Accepted corrections may affect a derived view; they do not erase the original.
- Preserve declined, superseded, and unresolved proposals as part of the decision history.

### Knowledge
- Every extracted lesson should identify repository, branch/snapshot, commit, path, blob hash where available, transformation, evidence status, limits, relationships, and review state.
- Distinguish observed source content from verified behavior, proposed designs, fiction, and hypotheses.
- Similarity is retrieval metadata, never truth, consent, or adoption authority.

### Adoption and writes
- A catalog entry, tag, signature, score, recommendation, or CI pass cannot independently authorize code adoption.
- Require explicit user/contributor authorization for consequential operations.
- Prefer additive commits, fast-forward updates, reviewable PRs, and rollback instructions.
- No force-push or history rewrite is part of this canonical account.
- Do not alter \`main\` or merge an open PR without explicit authorization.

### Privacy and stewardship
- Do not ingest credentials, secrets, or private interaction data into repository knowledge records.
- Any future personal-data memory system needs explicit consent, minimization, retention, deletion, provenance, access controls, and review.
- Prayer, faith, praise, and spiritual meaning remain voluntary human practices. Software must not infer belief or spiritual status from biometrics or claim divine authority.
- Biological or electromagnetic hypotheses remain hypotheses until supported by suitable empirical evidence; a software model or fictional source is not biological proof.

## 8. Relationship map (conceptual, not a dependency graph)

- **Main ↔ branches:** index and reference; no ownership or automatic adoption.
- **Branch Horizon ↔ Warden:** observation is bounded by non-ownership and non-adoption.
- **Divergence adoption ↔ signed package exchange:** both describe staged, explicit receiver-side review; integration and implementation are not established.
- **Source Digest ↔ branch catalog:** fingerprints and metadata can support provenance, but a digest alone does not establish meaning.
- **Stride JOB reconciliation ↔ knowledge review:** both preserve originals and record decisions separately; their schemas and runtimes are not declared interchangeable.
- **Holified Inception ↔ knowledge extraction:** contextual links can suggest relationships, but unresolved links and hypotheses stay labeled.
- **Git Freedom ↔ adoption governance:** Git operations are consequential; bridge safeguards and explicit authorization must be tested before wider use.
- **Fiction branches ↔ scientific work:** creative exploration may inspire questions but cannot substitute for experimental evidence.
- **Seed framework ↔ all workstreams:** conceptual orientation, not a control hierarchy.

No arrow in this section asserts a runtime dependency, common ancestry, or tested compatibility.

## 9. Outstanding work and evidence gaps

1. Complete branch-by-branch semantic review of all 27 current heads, including files, commit history, tests, licenses, build configurations, and provenance.
2. Reconcile current head changes in \`pantheon/branch-horizon\` and \`pantheon/divergence-adoption\` against the previously inspected SHAs.
3. Inspect \`build-speed\`, \`main-11-of-38\`, \`mold\`, \`Vanellye-patch-1\`, and the three fiction branches individually rather than inferring from names or shared files.
4. Review PR #9's cryptography, branch guard coverage, workspace conflict handling, token lifecycle, and Android device behavior; obtain exact-SHA CI evidence.
5. Review PR #8's exact diff and determine whether it should remain as a separate historical review record after PR #16.
6. Reconcile PR #1, PR #10, and current Main ancestry without rewriting history or assuming disconnected-graph causes.
7. Verify the seven-seed catalog schema and expand branch lessons only when exact source artifacts are inspected.
8. Define a typed relationship vocabulary and a review ledger for knowledge entries without making either a central authority.
9. Establish reproducible per-branch validation matrices and record skipped, unavailable, flaky, and platform-specific tests.
10. Review license and attribution obligations before any cross-branch or external code reuse.

## 10. Canonical status vocabulary

Use these labels consistently:

- **Verified:** a specific claim was checked against exact source, hash, commit, or reproducible run. State the scope.
- **Observed:** present in an inspected artifact; behavior has not necessarily been tested.
- **Proposed:** a design or possible future action, not active behavior.
- **Hypothesis / fiction:** exploratory content, not factual or scientific proof.
- **Unknown:** evidence is missing or ambiguous; leave it unresolved.
- **Needs review:** an identified risk or decision remains open.
- **Accepted for reuse:** a human review decision for a lesson, not permission to adopt code.
- **Merged:** GitHub confirms the PR was merged; do not infer runtime readiness.
- **Validated at SHA:** only the listed checks passed for that exact commit and environment.

## 11. Change protocol for this account

1. Never overwrite a historical snapshot to make it appear current.
2. Add a new timestamped branch-head snapshot for every later ref inventory.
3. Append new source-linked lessons; do not mutate the original source record.
4. If a source moves, preserve the old SHA and create a new observation.
5. If a correction is proposed, record the original, proposal, evidence, author, and review separately.
6. If a relationship is uncertain, label it as a hypothesis or open question.
7. Before any integration, run provenance checks, interface review, and reproducible tests against exact SHAs.
8. A passing gate permits further review, not automatic adoption.
9. Keep PR review, user authorization, and merge as separate decisions.
10. Provide recovery instructions and conditions for clearing warnings.

## 12. Current canonical conclusion

CodEXgen is a multi-branch creative and technical repository with distinct workstreams in Android application development, Stride temporal/context systems, Git operations, Pantheon governance and peering, knowledge cataloging, and fictional/hypothetical exploration.

Its strongest shared design direction is not forced unification. It is **traceable connection without erasure**: preserve origins, make relationships explicit, test interfaces, keep uncertainty visible, and require consent before consequential adoption.

This account is a consolidated working index, not a completed semantic audit or certification of the whole repository. The next work is to deepen evidence branch by branch while retaining each branch's identity.

---

*Prepared as an additive knowledge artifact on \`knowledge-recycle-foundation\`. It does not modify \`main\`, merge a PR, alter original branch sources, or authorize branch adoption.*
