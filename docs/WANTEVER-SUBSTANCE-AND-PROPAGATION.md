# Wantever — Substance and Propagation Contract

**Status:** proposed shared design contract; branch adoption and runtime enforcement must be verified independently.
**Canonical name:** Wantever.
**Scope:** meaning-preserving transformation, composition, and propagation of compatible contributions across ERIA.

> Transform the substance. Preserve the truth of its origins. Never confuse propagation with permission to overwrite.

## 1. Meaning

Wantever is the ERIA principle for turning existing contributions into new, traceable outcomes. It is not a blanket instruction to copy every file, merge every branch, or treat every contribution as compatible.

Wantever changes the substance of a result through explicit composition and transformation. It preserves the source history, records what changed, and makes the resulting meaning reviewable.

## 2. Governing principles

1. **Composition over erasure.** Combine compatible contributions without deleting or falsifying their origins.
2. **Transformation over renaming.** A change in name alone is not a change in behavior or substance; describe the actual transformation.
3. **Provenance at every boundary.** Bind each derived artifact to its source repository, branch, commit or content digest, transformation, and validation evidence.
4. **Meaning before propagation.** Check schema, units, interfaces, dependencies, permissions, and domain constraints before carrying a contribution forward.
5. **Unknown remains unknown.** Missing, conflicting, stale, or incomplete evidence must remain explicitly unknown or require review.
6. **Consent before consequential action.** Discovery and compatibility analysis may be read-only; writes, adoption, deployment, export, and actuation require their own scoped human authorization.
7. **Reversibility by design.** Preserve source records, record transformations, provide recovery steps, and identify irreversible side effects.
8. **No automatic convergence.** Branch identity, ancestry, and purpose remain distinct unless a reviewed integration explicitly changes them.

## 3. Propagation lifecycle

For every candidate contribution:

1. **Discover** the source without executing imported content.
2. **Pin** the exact repository, branch, commit SHA, and relevant artifact digests.
3. **Inspect** the branch purpose, tree, interfaces, dependencies, tests, licenses, and security boundaries.
4. **Classify** the contribution as compatible, incompatible, review-required, or unknown for each target domain.
5. **Map** source concepts to target contracts without collapsing absent, null, zero, false, empty, and unknown.
6. **Transform** through a named, versioned adapter or documented operation; retain the original and record parameters.
7. **Verify** digests, provenance, policy, and independent test evidence.
8. **Propose** adoption through a reviewable pull request or equivalent approval record.
9. **Authorize** each consequential operation explicitly and only for its reviewed scope.
10. **Recover** through an auditable revert or compensating action, documenting what cannot be reversed.

A changed source SHA invalidates evidence tied to the previous SHA and requires re-evaluation.

## 4. Domain propagation rules

| Domain | Wantever application | Boundary |
|---|---|---|
| Android / CodeGen Studio | Carry reviewed contracts into UI and local workflows | UI intent is not execution authority |
| Python services | Transform and validate explicit data contracts | Inputs and outputs remain testable and provenance-bound |
| Stride | Orchestrate reviewed adapters and work units | Orchestration does not silently command workers |
| Pantheon | Apply capability and policy contracts | Capability checks are not an OS sandbox |
| Git Freedom Bridge | Exchange and propose branch contributions | No silent push, merge, force update, or history rewrite |
| TACS | Bind artifacts to digests, signatures, and correction chains | A valid signature is not adoption permission |
| Branch Horizon / Divergence Garden | Compare, classify, and report divergence | Similarity or promotion does not authorize adoption |
| Fiction / hypothesis / experimental domains | Preserve labels, assumptions, and evidence quality | Fiction and hypotheses are not empirical validation |
| Data and records | Preserve raw values and append derived transformations | Do not rewrite historical records in place |
| External systems or hardware | Require explicit capability, target, and recovery review | No implied deployment, export, or physical actuation |

This table is a mapping contract, not proof that every listed domain has implemented Wantever.

## 5. Substance record

Each propagated result should record, where applicable:

- stable result identifier and schema version;
- source repository, branch, commit SHA, and content digest;
- source purpose and declared contribution;
- target domain and compatibility decision;
- transformation name, version, parameters or parameter digest;
- original and derived artifact digests;
- units, quality, and uncertainty where relevant;
- tests, toolchain, environment, and exact tested SHA;
- reviewer, authorization scope, and decision timestamp;
- known limitations, recovery procedure, and irreversible effects.

Do not place credentials, private keys, or unnecessary personal data in the record.

## 6. Adoption gates

A contribution may be proposed for adoption only after:

- source and target SHAs are pinned;
- compatibility and provenance are documented;
- independent verification examines the exact candidate;
- required reproducible tests pass on that candidate;
- security, privacy, licensing, and permission boundaries are reviewed;
- a human reviewer approves the exact diff;
- a recovery path and its limitations are recorded.

No tag, signature, score, agent, CI job, or propagation process may independently approve or merge its own contribution.

## 7. Acceptance criteria

- [ ] Wantever is described as a transformation and composition contract, not a rename-only operation.
- [ ] Source branch identities and commit ancestry remain preserved.
- [ ] Derived artifacts carry traceable provenance.
- [ ] Unknown and conflicting evidence is never silently promoted to a pass.
- [ ] Domain adapters preserve units, types, and meaningful distinctions.
- [ ] Consequential actions require scoped human authorization.
- [ ] Validation is tied to exact immutable inputs.
- [ ] Recovery and irreversible effects are documented.
- [ ] Branch-specific implementation status is reported honestly.

## 8. Implementation boundary

This document establishes a shared design contract. It does not claim that Wantever is implemented, tested, or deployed in every branch or runtime. Each branch must be inspected and updated through a separate reviewable change with focused tests. Until those changes are merged and verified, propagation means a shared reference and an adoption plan—not automatic code convergence.

Wantever is a software and governance concept. It does not establish biological, electromagnetic, spiritual, or other physical effects.


## 9. Inventory of invited invention

Wantever can compose the ERIA inventory concepts defined in [ERIA — Inventory of Invited Invention](ERIA-INVENTORY-OF-INVITED-INVENTION.md):

- **WITHOUT** records a known absence, deliberate omission, or unresolved gap.
- **WONT** records a stated willingness, disposition, or intended direction.
- Their composition may invite improvisation and generate proposals; it does not create consent or execution authority.
- **CAP** records a scoped, evidenced, revisable boundary. It does not imply that a mandatory safety, legal, or policy limit may be bypassed.

Preserve each source entry and its provenance. Keep proposals distinct from confirmed facts and adopted changes. Destructive force pushes remain prohibited by default; any exceptional non-fast-forward update requires exact scoped authorization, a recoverable prior reference, and an expected-old-SHA lease check. If those conditions are not met, retain the existing history.

This vocabulary is an ERIA design contract. It does not claim that every runtime or branch already enforces these controls.
