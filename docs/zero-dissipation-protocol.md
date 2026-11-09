# Zero-Dissipation Anchor

**Anchor identifier:** `7f7a43a973a96a06dd432bf94843213d09133323`

**Scope:** Repository-wide governance for CodEXgen, every branch, JOBs, Faculty Engine, and Geometry Laboratory.

This document establishes a review-and-verification protocol. It does not authorize autonomous destructive edits, history rewriting, branch deletion, or force pushes.

## Governing directives

1. **Detect** — Identify redundant zeros, empty placeholders, dead code, null references, and uninitialized states.
2. **Distinguish** — Preserve legitimate numerical zeros, intentional empty values, and meaningful historical data.
3. **Resolve** — Replace accidental emptiness only with validated values, explicit states, or recoverable dependencies.
4. **Reconcile** — Connect orphaned branches, disconnected modules, and missing references without erasing their histories.
5. **Verify** — Test every transformation and preserve a rollback path.
6. **Propagate** — Carry approved improvements through authorized branches without silently overriding ownership.

## Required safeguards

- Treat `0`, `0.0`, `false`, empty strings, empty collections, and `null` as distinct values. Never classify them as defects by appearance alone.
- Preserve source history and branch ancestry. Prefer additive commits and pull requests over rewriting shared history.
- Require evidence, a focused diff, and relevant tests before accepting a repair.
- Record each proposed repair with its file/path, finding, rationale, validation, and rollback reference.
- Do not propagate changes to a branch without authorization from its owner or maintainer.
- Never force-push as part of automated repair. If a force-with-lease operation is separately authorized, verify the expected remote head immediately beforehand.
- Keep uncertain findings as review items; do not guess replacement values.

## Lifecycle

### Detect
Run static analysis, compiler checks, tests, dependency/reference scans, and branch/CI inventory. Findings are candidates, not automatic edits.

### Distinguish
Classify each finding as intentional, defective, uncertain, or historical. Include context and tests that demonstrate why a value is or is not meaningful.

### Resolve
Make the smallest reversible change. Prefer explicit types/states and validated dependency wiring. Preserve compatibility unless a migration is approved.

### Reconcile
Map branch ancestry and module interfaces before integration. Use merge commits or pull requests that retain provenance. Do not flatten or discard divergent histories.

### Verify
Run targeted tests, full available CI, build checks, and persistence/recovery tests where relevant. Capture the commit and test results.

### Propagate
Promote only reviewed commits. Use branch protection and normal pull-request review. Keep a rollback commit or documented revert procedure.

## Initial integration order

1. Land and review this protocol on an isolated feature branch.
2. Inventory repository branches and current CI coverage.
3. Map JOBs, Faculty Engine, and Geometry Laboratory to their actual source paths and interfaces.
4. Add independent checks for uncovered modules.
5. Implement read-only detection/reporting before proposing automated repairs.
6. Pilot a single low-risk, test-covered repair.
7. Propagate by authorized pull request, one branch at a time.

## Acceptance criteria

- No legitimate zero, false value, empty collection, or historical record is changed merely because it looks empty.
- Every proposed repair has a rationale, test evidence, and rollback path.
- Existing branch history remains intact.
- No unauthorized branch receives changes.
- CI and recovery checks pass before promotion.
