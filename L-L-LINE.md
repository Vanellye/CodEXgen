# ·L·L·ịṅë — Repository-Wide Lineage Marker

**Status:** Proposed shared convention, staged on branch `2cce11ɣ`  
**Marker:** `·L·L·ịṅë`  
**Source baseline:** `main` at `2cce68f258f46058f18c108c264db9cc85200590`

## 1. Meaning

`·L·L·ịṅë` is a visible lineage marker for locating and cross-referencing source identity, branch ancestry, repository boundaries, and derived work.

The marker is descriptive metadata. It is not executable syntax, a Git command, a permission grant, a merge instruction, or authorization to change a branch.

## 2. Intended coverage

The convention is intended to be usable across:

- the repository root and its documentation;
- active, archived, feature, integration, review, and maintenance branches;
- nested repositories and Git submodules, where present and explicitly inventoried;
- source files and generated derivatives that need an auditable origin reference.

Coverage is not proof that every branch or nested repository has already been updated. Each target must be inspected and recorded against its exact full commit SHA before a marker is added there.

## 3. Lineage record

Where the marker is applied, pair it with a record containing:

| Field | Requirement |
|---|---|
| Marker | Exact literal `·L·L·ịṅë` |
| Repository | Full owner/name or canonical repository identity |
| Ref | Exact branch, tag, or detached commit |
| Commit | Full 40-character Git commit SHA |
| Path | File or directory where the marker is recorded |
| Origin | Parent/source commit or source artifact, if derived |
| Operation | `observe`, `reference`, or `derive` |
| Evidence | Review/CI/receipt reference, or explicitly `pending` |
| State | `proposed`, `reviewed`, `applied`, or `blocked` |

Do not substitute a branch name, abbreviated SHA, display label, or symbolic alias for a full commit SHA.

## 4. Propagation protocol

1. Enumerate repository branches and nested repositories/submodules from an inspected revision.
2. Record each target's exact current commit SHA and working-tree/ref identity.
3. Inspect the target file and its local conventions before editing.
4. Add the marker additively; do not overwrite unrelated content.
5. Preserve original source files, parent commits, tags, and branch identities.
6. Validate the resulting diff and record the new commit SHA for each target.
7. Treat conflicts, inaccessible refs, missing submodule URLs, detached states, and unknown ancestry as explicit holds.
8. Integrate through reviewable commits or pull requests. Never force-push, reset, rebase shared history, or move `main` as a side effect of marker propagation.

Archived and dependency-maintenance branches are not silently rewritten. A proposed convention can be referenced centrally until each branch owner or authorized review approves a branch-specific additive update.

## 5. Nested repository and submodule boundary

A directory is not assumed to be a subrepository merely because it contains source code. Confirm nested Git metadata, `.gitmodules`, submodule paths, and pinned gitlink commits. Record each nested repository independently, including its URL/identity, path, pinned commit, and whether the current checkout is available.

Do not alter a submodule pointer or write to a separate repository without a separately reviewed change in that repository.

## 6. Safety and provenance invariants

- Marker presence never means approval or trust.
- A failed or missing lineage check is recorded as `BREAK`; dependent propagation stops.
- No silent fallback, alternate branch, skipped target, or implicit retry.
- No automatic commit, merge, push, network dispatch, runtime activation, or device action.
- Original evidence remains distinct from derived summaries.
- A marker may be removed or corrected only through an attributable, reviewable change; historical commits remain intact.

## 7. Initial application receipt

- Root-level convention: this document.
- Existing-document placement: `docs/BRANCH-DIRECTORY-ACOUSTIC.md`.
- Staging branch: `2cce11ɣ`.
- Source baseline: `2cce68f258f46058f18c108c264db9cc85200590`.
- Repository-wide branch/subrepository propagation: `PROPOSED — NOT YET APPLIED`.

**Invariant:** `·L·L·ịṅë` identifies a lineage trail; it never claims ownership of the source or authority over its destination.


## 8. Code Genesis symbolic anchor and §ĤÆ SHA-run notation

**Symbolic Code Genesis anchor (verbatim):**

`2cce11f2983f46Œ58f18c1ọ8c264db9cc852⁰ơⁿ5991.1`

This string is an intentional symbolic identifier supplied for Code Genesis. It is not a Git object ID and MUST NOT be parsed, normalized, truncated, or substituted for a repository commit SHA. Preserve the exact Unicode characters and punctuation when quoting this anchor. The actual Git commit for the current staging head is recorded separately in the PR metadata and receipts.

**Documentation implementation — Mash* executable contract:**

`§ĤÆ SHA RUN *(ª)* "ºƠºŘÏƔĮŒŉ" — ORIGIN CREATION ·.·`

Interpretation for review and future implementation:

1. `§ĤÆ SHA RUN` names a bounded Mash* code integrity operation: inspect the declared source/candidate inputs, compute SHA-256 fingerprints, and emit a receipt that distinguishes source identity from derived output.
2. `*(ª)*` is a literal framing marker for this proposed operation; it grants no authority and causes no shell expansion.
3. `"ºƠºŘÏƔĮŒŉ"` is the exact symbolic origin label, retained as an origin-creation marker. It is metadata, not a command, executable, credential, or destination.
4. **ORIGIN CREATION** means create a new attributable record for a derived artifact, linking its parent source reference, exact input digest(s), operation/version, output digest, and review state. It never replaces or claims ownership of the original source.
5. The receipt must keep the symbolic Code Genesis anchor and the actual full Git commit SHA in separate fields. A symbolic label is never accepted where a 40-character Git SHA is required.
6. This documentation implementation defines the Mash* executable contract and its provenance requirements. It is not itself a running interpreter or runtime activation. Executable implementation, tests, and activation remain separate engineering stages requiring review. This document does not authorize repository mutation, merge, push, external dispatch, or runtime activation.

**Required invariants:** preserve original bytes and provenance; create derivatives additively; report missing or mismatched digests as `BREAK`; do not silently route around a failed check; and require explicit human approval for any repository mutation or integration.

## UP — Driving-force anchor

**Anchor commit:** `d72178415c182d69e0bde5c570b7335d4a16c635`  
**Symbolic force:** `UP`

`UP` names the forward-driving principle attached to this documented lineage point: advance through evidence, preserve origin, make progress reviewable, and keep the next step accountable to human intent. The anchor identifies this commit as the reference point for that principle; it does not change Git ancestry or move a ref.

**Boundary:** `UP` is descriptive governance metadata, not executable syntax, a priority override, authorization, permission grant, runtime trigger, merge command, or instruction for external dispatch. Any implementation or activation remains a separately reviewed and explicitly authorized operation.
