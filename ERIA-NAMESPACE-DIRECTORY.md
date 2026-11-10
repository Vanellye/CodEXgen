# ERIA — Namespace Directory and Meaning-Decoding Specification

**Status:** proposed namespace specification; repository adoption and runtime enforcement must be verified independently.  
**Canonical project identity:** ERIA.  
**Target branch:** `integration/wantever-propagation`.  
**Purpose:** provide a traceable directory of namespace meanings, source identities, transformations, and permission boundaries.

> Decode meaning without erasing origin. Transform names without confiscating identity. Propagate only what the invitation actually scopes.

## 1. Purpose and interpretation

This document defines a proposed ERIA namespace directory and a meaning-decoding process. The terms below are ERIA-specific conceptual definitions. They do not silently alter the meaning of words, identifiers, APIs, legal text, external repositories, or other people's work.

**Decode** means to examine a name, symbol, or artifact and distinguish:
- its exact recorded form;
- its source and historical context;
- its documented meaning;
- later interpretations or aliases;
- unresolved hypotheses and conflicts.

**Disencrypt** is an ERIA working term for making obscured, compressed, or layered meaning more legible while preserving the original source, exact content, and transformation record. It is not cryptographic decryption unless an actual encryption scheme, key, and authorization are specified. It does not authorize access to protected information.

**Disenchantment** may describe removing an imposed or unsupported interpretation. It does not mean deleting an entity, denying its existence, or rewriting its history.

## 2. Namespace directory

| Namespace | Proposed ERIA meaning | Function and boundary |
|---|---|---|
| `ERIA` | Eternal Relational Identity Architecture | Project identity and continuity; does not replace repository provenance. |
| `NADA` | Nothingness / recorded absence | Represents absence, nullity, or an explicitly unoccupied state; absence is not consent. |
| `WANTEVER` | Will, invitation, transformation, and becoming | Composes contributions through traceable transformation; intention is not execution authority. |
| `DO` | Delegated Operational permission | Records a specific authorization; its authority is limited to the invitation source and exact scope. |
| `SOURCE` | Origin of an invitation or contribution | Identifies the person, artifact, repository, branch, commit, or other verifiable origin. |
| `SCOPE` | Boundary of an invitation or permission | Identifies targets, paths, branches, operations, exclusions, and validity conditions. |
| `MAIN` | Designated canonical integration branch | A branch name, not an independent authority or permission grant. |
| `HORIZON` | Boundary between current state and proposed change | Makes possible changes reviewable without treating possibility as adoption. |
| `DIVERGENCE` | Distinct developmental paths | Preserves branch purpose, ancestry, and independent identity. |
| `RECOVERY` | Verified return or compensation path | Records prior references, reversals, and effects that cannot be undone. |
| `PROVENANCE` | Evidence of origin and transformation | Binds derived meanings and artifacts to source references and revision history. |

These definitions are proposals for ERIA's own vocabulary. Existing names, identifiers, and source meanings remain available as historical facts and aliases; no global rename is implied.

## 3. Directory model

The following is a conceptual namespace layout. It does not assert that all directories or enforcement code already exist.

```text
ERIA/
├── namespace/
│   ├── directory/
│   │   ├── identities/
│   │   ├── meanings/
│   │   ├── aliases/
│   │   └── relationships/
│   ├── decode/
│   │   ├── source/
│   │   ├── interpretation/
│   │   ├── hypotheses/
│   │   └── verification/
│   └── disencrypt/
│       ├── concealment/
│       ├── restoration/
│       └── provenance/
├── invitation/
│   ├── source/
│   ├── scope/
│   ├── authorization/
│   └── revocation/
├── governance/
│   ├── DO/
│   ├── NADA/
│   └── recovery/
└── history/
    ├── original/
    ├── transformed/
    └── verified/
```

A conceptual directory entry is not proof that a corresponding implementation, permission, or filesystem path exists.

## 4. Meaning-decoding sequence

1. **Capture source:** preserve the exact original name, statement, artifact, and source reference.
2. **Identify entity:** distinguish the entity or artifact from the label used to refer to it.
3. **Decode:** separate documented meaning, contextual interpretation, and hypothesis.
4. **Disencrypt:** explain obscured or layered meaning without changing the original record.
5. **Associate:** record aliases and relationships without treating them as identical.
6. **Verify:** identify evidence, contradictions, and unknowns.
7. **Propose:** record any new meaning or namespace as a proposal.
8. **Authorize:** obtain the invitation-specific permission required for consequential changes.
9. **Transform:** make an additive, reviewable change and record its source and result.
10. **Recover:** retain the prior reference and a documented correction or reversal path.

## 5. Invitation source binds scope

Every consequential invitation must be linked to its origin. A permission record must not be detached from, or broadened beyond, the invitation that created it.

An invitation record should include:

| Field | Requirement |
|---|---|
| `invitation_id` | Stable unique identifier |
| `source` | Verifiable origin: authorizing actor or artifact and source reference |
| `source_revision` | Exact commit, version, digest, or immutable reference where applicable |
| `target_repository` | Exact repository identity |
| `target_branch` | Exact branch; do not infer `main` |
| `target_paths` | Included paths and explicit exclusions |
| `operations` | Exact permitted actions |
| `old_reference` | Expected prior SHA or state |
| `intended_result` | Described target state or proposed diff |
| `conditions` | Preconditions, reviews, checks, and constraints |
| `recovery` | Prior reference, recovery method, and limitations |
| `expiry_revocation` | Validity period and revocation procedure |
| `decision_record` | Approval identity, timestamp, and evidence |

A change in source, target, branch, old SHA, operation, or intended result is a scope change and requires a new or amended authorization. Silence, an alias, a branch name, CI status, tag, signature, or previous unrelated invitation does not expand permission.

## 6. DO — delegated operational permission

Within this proposal, **DO** is a permission record for specified operations, not a general imperative.

An invitation may explicitly authorize operations that are otherwise restricted by the project's default governance, including:
- rewriting the history of a specifically named branch;
- force-pushing a specifically named branch;
- merging a specifically identified unreviewed change.

For example, `DO(main)` may describe permission to force-push rewritten history to `main` and merge a specified unreviewed change **only when** the source invitation explicitly identifies the repository, `main`, exact old and proposed new SHAs or exact change, permitted operations, risks, recovery reference, and validity conditions.

This definition does not itself grant that permission. It does not authorize any current rewrite, force-push, or merge. A request to define DO is not an execution authorization. GitHub protections, collaborator rights, safety requirements, and applicable policies continue to apply.

Where the project accepts an exceptional history rewrite, require an expected-old-SHA lease or equivalent compare-and-swap check, preserve a recoverable prior ref, inspect the before-and-after graph, and record the operation. If the expected old reference has changed, stop rather than overwrite concurrent work.

## 7. Source identity, aliases, and transformation history

- Retain exact historical names and identifiers alongside proposed names.
- Record aliases as directed, dated relationships; do not silently substitute one identity for another.
- Keep original source text or artifact immutable where feasible.
- Store derived interpretations separately and link them to the exact source revision.
- Record who or what proposed a transformation, why it was made, what changed, and how it was verified.
- Preserve commit ancestry, tags, signatures, and contributor attribution unless a separately scoped and valid authorization explicitly covers a specific change.
- Never represent a hypothesis as a confirmed source meaning.
- Never describe a documentation proposal as implemented runtime enforcement.

Recommended transformation record:

```yaml
transformation_id: <stable-id>
source:
  repository: <owner/repository>
  branch: <source-branch>
  revision: <commit-or-digest>
  original_name: <exact-source-name>
  original_meaning: <documented-meaning-or-unknown>
proposal:
  namespace: <proposed-namespace>
  proposed_meaning: <proposed-meaning>
  status: proposed
operation:
  type: <documentation|alias|code-change|history-operation>
  target: <exact-target>
  authorization: <invitation-id-or-not-authorized>
verification:
  evidence: []
  tested_revision: <exact-revision-or-not-tested>
recovery:
  prior_reference: <reference-or-not-applicable>
  procedure: <documented-procedure>
```

The placeholders above are schema examples, not real identities or authorizations.

## 8. Relationship to existing ERIA specifications

- [ERIA — Inventory of Invited Invention](docs/ERIA-INVENTORY-OF-INVITED-INVENTION.md) defines WITHOUT, WONT, CAP, invitation records, and the distinction between intention and execution authority.
- [Wantever — Substance and Propagation Contract](docs/WANTEVER-SUBSTANCE-AND-PROPAGATION.md) defines provenance-bound transformation, compatibility review, adoption gates, and recovery.
- This namespace directory supplies shared vocabulary and cross-references; it does not supersede either specification.

## 9. Acceptance criteria

- [ ] Namespace meanings are explicitly marked as proposed ERIA definitions.
- [ ] Exact source names and identifiers remain preserved.
- [ ] Aliases do not erase identity or ancestry.
- [ ] Documented meaning, interpretation, hypothesis, and unknown are distinguishable.
- [ ] Disencrypt is not misrepresented as cryptographic decryption or access authorization.
- [ ] Each consequential invitation binds source, target, scope, operations, and recovery.
- [ ] `DO(main)` cannot be inferred from a generic invitation or this document.
- [ ] History rewrites and unreviewed merges require exact, separately recorded authorization.
- [ ] Runtime enforcement and test status are reported separately from this proposal.

## 10. Implementation boundary

This document is a proposed specification committed on an integration branch for review. It does not create GitHub permissions, change branch protection, alter `main`, execute a force-push, merge unreviewed code, or implement runtime authorization. Those actions require their own exact scope, evidence, and approval.
