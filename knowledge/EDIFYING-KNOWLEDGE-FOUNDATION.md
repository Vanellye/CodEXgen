# Edifying Knowledge Foundation

## Purpose

This layer turns repository history into reusable learning without turning history into editable raw material. It is an additive index of lessons, evidence, relationships, and unresolved questions. It does not absorb branches, rewrite source, or decide what a contributor meant.

**Recycle the knowledge; preserve the origin.**

## Starting boundary

This is a deliberately small, evidence-backed seed catalog, not a claim that every repository branch or file has been ingested. Its initial sources are:

- the current `main` snapshot at `67ecdb5c5bd148b6fd7c9945fa648f3c89a93a95`;
- the documented Stride snapshot at `a8c6a90efc09e27afbead0f07191e17bf4faa431`;
- the existing `edify` branch policy document, read as a branch-local proposal rather than a rule imposed on other branches.

Every catalog entry points back to a source. Where a source hash or exact author is unavailable, that absence remains explicit. No inferred authorship, missing values, or intended semantics are filled in.

## Knowledge record model

Each reusable lesson should carry:

1. **Identity** — stable record ID and concise title.
2. **Origin** — repository, branch or snapshot, commit, path, and blob hash when available.
3. **Record type** — observation, decision, correction, lesson, proposal, hypothesis, or open question.
4. **Evidence status** — verified, observed, proposed, hypothetical, fictional, or unknown.
5. **Transformation** — what was extracted or summarized; the source itself remains unchanged.
6. **Learning** — a concise reusable lesson, explicitly separated from source text.
7. **Limits** — uncertainty, untested behavior, scope, and known gaps.
8. **Relationships** — links to related records without merging their identities.
9. **Review state** — unreviewed, reviewed, accepted for reuse, declined, or superseded. A review changes the derived catalog, never the historical source.

## Evidence labels

- **Verified** — directly checked against a named artifact, hash, commit, or reproducible test result. State exactly what was verified.
- **Observed** — present in a source, but not independently tested for behavior.
- **Proposed** — a suggested design or interpretation, not adopted fact.
- **Hypothetical / fictional** — explicitly speculative or fictional; never promote to empirical evidence.
- **Unknown** — source, meaning, compatibility, authorship, or behavior is not established.

A passing build is evidence only for the exact build and commit tested. It does not prove correctness, safety, semantics, or runtime behavior beyond that test.

## Non-negotiable preservation rules

- Original source files, commit history, authorship, timestamps, and blob identities are not rewritten by cataloging.
- A correction is a separate record linked to the original; it never silently replaces it.
- A proposal is not an accepted correction. A generated summary is not source truth.
- A syntactically valid replacement is not proof of intended meaning.
- Missing or ambiguous values remain unresolved until supported by evidence or author confirmation.
- Branch names are navigational labels, not ownership claims. Branches may contribute, decline, fork, or evolve independently.
- Cross-branch links are suggestions for review, not automatic adoption or merge permission.
- No automated learning process may use a catalog entry to authorize a consequential repository write.

## Seed lessons

### 1. Preserve legacy syntax as evidence

The quarantined fictional Python source is pinned by Git blob SHA `2d689a275e0a2bf39a1c1fa14afe3d84fb5589c2`. CI verifies that exact blob and excludes only that file from syntax compilation. The malformed expressions are recorded verbatim; replacement values are not guessed.

**Reusable lesson:** isolate a known defect narrowly, preserve its bytes, and make the validation boundary visible. Do not call quarantine a repair.

### 2. Separate correction from original event

Stride's JOB reconciliation work uses append-only correction proposals and review decisions. The original event remains intact; an accepted correction affects a derived view, while declined and accepted review history remains available.

**Reusable lesson:** store what happened separately from what a reviewer later believes should be shown. Derived state must be traceable to the source event and the review decision.

### 3. Keep contextual synthesis read-only

The Stride Holified Inception reader is documented as a contextual reader that can relate observations and creative concepts while labeling unresolved links and hypotheses. It does not claim factual discovery or silently adjudicate ambiguity.

**Reusable lesson:** context can expand interpretation without acquiring authority over the underlying record.

### 4. Treat semantic memory as retrieval, not truth

The current `python/semantic_vector_memory.py` stores prompts and reasoning text in a persistent vector collection and retrieves nearby traces using a distance threshold. This is an observed implementation, not proof that a retrieved trace is correct, consented for indefinite retention, or suitable for reuse.

**Reusable lesson:** similarity is a retrieval signal, not evidence of truth or permission. Future ingestion should define consent, minimization, retention, deletion, provenance, and human review before using personal interaction data.

### 5. Keep adaptive changes reviewable

The current `python/adaptive_governance.py` contains an illustrative pipeline that can construct a rewritten trace after a simulated judgment. Its implementation is not an append-only correction ledger and should not be confused with the Stride JOB reconciliation model.

**Reusable lesson:** preserve the input trace and store any generated alternative as a linked proposal. Never overwrite the original or describe a simulated judge as a validated authority.

### 6. Branch-local policies do not silently become global law

The `edify` branch's `EDIFY.md` describes a branch-root model and a text transformation that replaces ASCII zeroes in non-load-bearing text with alternate glyphs. The current `main` README contains altered numeric glyphs in build/version examples, while load-bearing source and configuration require ordinary digits. The intended scope and history of those changes are not established by this catalog.

**Reusable lesson:** preserve the policy document as an artifact, record compatibility concerns, and require explicit scope review before applying any transformation outside its originating branch. Never normalize or reverse such changes by guessing.

## Review and reuse lifecycle

1. **Discover** — identify candidate records without changing them.
2. **Fingerprint** — capture exact source path, commit, and blob hash when available.
3. **Classify** — label type and evidence status; keep unknowns visible.
4. **Extract** — write a concise lesson in a separate catalog entry.
5. **Cross-reference** — link related entries without collapsing their origins.
6. **Review** — allow a human to accept, decline, or qualify reuse.
7. **Apply** — if a lesson motivates code or policy changes, create a separate reviewed change with tests and rollback.
8. **Recheck** — verify the catalog still points to the intended source; never silently update a source identity.

## Suggested future interfaces

These are separable capabilities, not mandatory directories or a central authority:

- **Archive reader:** read-only access to source artifacts and Git metadata.
- **Fingerprint:** deterministic path/commit/blob identity capture.
- **Knowledge extractor:** creates proposed summaries with source citations.
- **Relationship mapper:** records typed links such as `derived_from`, `contradicts`, `implements`, `tests`, or `supersedes`.
- **Review ledger:** append-only human decisions about proposed knowledge.
- **Export:** portable JSON/JSONL or Markdown snapshots with provenance attached.

No interface should require a branch to surrender its internal model. Peering is optional and must be reviewed at the boundary.

## Explicit non-goals

This foundation does not:

- ingest private user conversations, secrets, credentials, or personal telemetry;
- infer biological, psychological, spiritual, or scientific facts from fictional source code;
- automatically adopt tags, branches, corrections, or generated recommendations;
- merge branches, modify `main`, or repair legacy syntax;
- treat semantic similarity, recency, popularity, or branch size as authority;
- claim repository-wide completeness.

## First acceptance criteria

- Every seed entry has a stable ID and traceable origin.
- Source records remain unchanged.
- Uncertain semantics and missing provenance are marked, not guessed.
- Fiction and hypotheses remain labeled.
- A lesson can be exported and reviewed without requiring its source branch to merge.
- No catalog action can trigger a consequential write without separate authorization.
