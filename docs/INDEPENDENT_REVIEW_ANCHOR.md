# PR #56 — Independent Review Anchor

This review is intentionally not a rubber-stamp approval. A reviewer must independently inspect the diff and record a reasoned assessment.

## Required review body

A qualifying GitHub approval must include all four headings below, with substantive content under each:

- SCOPE: Identify what was inspected and what was not inspected.
- EVIDENCE: Cite concrete files, tests, CI results, contracts, or line-level observations.
- RISKS: State remaining risks, missing dependencies, and limitations; write none found only with a reason.
- TESTS: State which checks were run and their result, or identify what remains untested.

The automated gate rejects approval by the pull-request author, approvals superseded by a later review from the same reviewer, approvals without the four evidence sections, and review states other than the latest APPROVED.

## Reviewer independence

The reviewer must make their own assessment, not copy the author's conclusion. The reviewer should challenge at least one assumption, inspect the changed files, and distinguish passing CI from safety, deployment, or hardware authorization.

## Scope anchor

PR #56 targets main from fix/main-water-ic-verification. The review must confirm that the base branch remains unchanged, that WATER equipment records remain metadata-only, and that no external I/O, deployment, or physical actuation is introduced.

## Non-authorizing outcome

A qualifying review is evidence for merge consideration only. It does not merge the PR, authorize deployment, or enable hardware.
