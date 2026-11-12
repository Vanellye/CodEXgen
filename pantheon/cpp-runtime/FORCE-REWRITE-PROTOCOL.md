# Force Rewrite Protocol

**Status:** Governance specification for ERIA/Pantheon  
**Default:** Reversible successor rewrite; Git history rewrite is disabled unless separately authorized.

## Purpose

Force rewriting may be used to correct, reorganize, or replace material when ordinary additive correction is insufficient. It must not silently erase origin, bypass review, or convert a proposal into authority.

## Two distinct operations

### 1. Reversible successor rewrite — default

- Preserve the original object or record unchanged.
- Create a successor with a new identity and an explicit `supersedes` reference.
- Record the reason, author/actor, timestamp, source identity, evidence, and validation result.
- Retain a tested rollback or restoration path.
- Keep unresolved differences visible; do not label a rewrite as verified merely because it was applied.

### 2. Git history rewrite — exceptional

History rewriting changes commit identities and can disrupt collaborators. It is not the same as correcting a file in a new commit.

Before a history rewrite:

1. Name the exact repository, branch, and commit range.
2. Confirm the branch is not protected, shared, or the base of active work without collaborator coordination.
3. Fetch the remote and verify the expected remote head.
4. Create and verify a durable backup reference and, where appropriate, an external bundle.
5. Record the old and proposed new commit IDs, the reason, scope, and recovery instructions.
6. Obtain explicit human approval for this exact rewrite plan.
7. Review the rewritten commit graph and run relevant tests.
8. Push only with `--force-with-lease`, never blind `--force`.
9. Verify the remote head after the push and publish the recovery reference.

If the remote head differs from the expected value, stop. Do not overwrite another contributor's work.

## Authorization contract

A generic approval to add this protocol, update a document, or create a branch does **not** authorize rewriting Git history. Approval must identify the exact repository, branch, range, and intended replacement. Approval expires if the remote head changes.

The following are never implicit:
- permission to rewrite `main` or a protected branch;
- permission to delete tags, branches, or source records;
- permission to rewrite another contributor's commits;
- permission to force-push merely because a local branch is ahead or diverged.

## ECTICT and provenance rules

- Preserve source identity and distinguish verified facts, inferences, and unknowns.
- Record the original and successor separately.
- Explain what changed and why.
- Allow dissent and unresolved review findings to remain visible.
- Require a human reviewer to approve adoption after validation.
- A successful push is not proof that the rewritten code is correct.

## Stop conditions

Stop without mutation if the target branch or expected head is ambiguous, backup verification fails, approval is missing, collaborators may be affected without coordination, tests fail, or remote state changes during preparation.

## Current implementation boundary

This document establishes the policy. It does not execute Git commands, grant credentials, alter branch protection, or enable an autonomous history-rewrite service. Actual history rewriting remains a separately approved, operator-executed action.
