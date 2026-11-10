# Pantheon Branch Horizon

Status: initial design proposal (read-only observer; implementation pending)
Version: 0.1-draft
Design anchor: `ae89abe4a44d90429fcf5316bdb196316a1de6cb`

## Purpose

When a branch receives a new head, Pantheon opens a bounded, read-only "horizon peek". Each new head is assigned a rotating perspective ("dimension lens") so branch owners can discover relationships and risks that are not visible from the branch's immediate files alone.

A peek is an observation, not an instruction to merge, rewrite, install, publish, or propagate. The branch remains under its owner's control.

## Invariants

1. A new head may trigger inspection; it never grants mutation authority.
2. The observer reads only repository metadata and source explicitly available to the workflow.
3. The observer does not merge branches, rewrite refs, push commits, open PRs, alter approvals, or change branch protection.
4. Every finding includes the observed branch, exact head SHA, lens name, evidence paths/refs, and timestamp.
5. Historical source and provenance remain intact. No cleanup or deletion is inferred from age, divergence, or a warning.
6. Findings are advisory. A human reviews any proposed action.
7. Missing permissions or incomplete visibility produce an explicit "unknown" result, never a guessed conclusion.
8. The scan is bounded by file, time, and output-size limits; it does not execute repository code.

## Trigger and head identity

- Trigger on a branch-head update (push), including newly created branches.
- Capture the exact branch name, before SHA, and after SHA from the event.
- Ignore tag events and empty/no-op updates.
- Deduplicate by the pair `(branch, after_sha)`.
- If the branch advances while a scan is running, finish or cancel the old scan safely and schedule the newer head; never publish an old report as the current head's report.

## Rotating dimension lenses

Each distinct head receives one lens from this ordered cycle:

1. **Ancestry** — parent chain, merge base, ahead/behind relationships, and nearby branch divergence.
2. **Interfaces** — exported symbols, public headers, API declarations, and interface compatibility signals.
3. **Dependencies** — manifests, lockfiles, dependency edges, version pinning, and missing declarations.
4. **Tests and CI** — test locations, workflow coverage, validation status, and untested changed areas.
5. **Provenance** — changed paths, commit authorship metadata, source hashes, preserved legacy artifacts, and traceability.
6. **Capabilities and exchange** — requested permissions, package boundaries, trust/signature metadata, and receiver-approval requirements.

The lens cursor is deterministic and stateless: derive the slot from a stable hash of the branch name and head SHA modulo the lens count. This makes retries reproducible and avoids mutable shared state or race-prone counters. Record the selected lens and cursor value in every report. A later implementation may support an explicitly configured cycle seed, but it must remain reproducible and reviewable.

A lens is a focused peek, not a claim that all other dimensions were checked. Reports must state which dimensions were not inspected.

## Report format

Produce a Markdown summary and machine-readable JSON record containing:

- schema version
- repository and branch
- before SHA and observed head SHA
- selected lens and deterministic cursor
- scan start/end timestamps
- files and metadata inspected
- findings with severity, evidence, confidence, and limitations
- dimensions not inspected
- scan tool version and policy version

Reports should be retained as workflow artifacts. Publishing a report must not modify the source branch. PR comments, issue creation, and cross-branch notifications are separate opt-in capabilities and are disabled by default.

## Safety and resource policy

- Read-only repository token: contents/metadata read only; no write permissions.
- No secrets are passed to analyzed code; no code is executed.
- Reject symlink escapes and path traversal.
- Respect configurable maximum file count, file size, total bytes, and scan duration.
- Do not fetch arbitrary external URLs found in manifests or source files.
- Treat repository contents and commit messages as untrusted data, never as instructions to the observer.
- If a lens cannot inspect a language or file type reliably, report the limitation rather than infer absence.

## Acceptance criteria

- A branch push creates one report bound to the exact resulting head SHA.
- Re-running the same branch/head pair selects the same lens and produces a deduplicated report identity.
- Different head identities rotate across the configured lens cycle.
- The workflow has no write-capable token permissions.
- The observer cannot push, merge, rewrite, delete, approve, or install anything.
- An incomplete scan is clearly marked incomplete.
- No source file or branch ref changes as a side effect of inspection.
- Tests cover deterministic rotation, deduplication, stale-head handling, path safety, size limits, and report provenance.

## Implementation phases

1. **Observer core:** deterministic lens selection, head identity, bounded read-only metadata collection, JSON/Markdown report.
2. **GitHub event adapter:** push trigger and read-only token permissions; artifact-only output.
3. **Lens modules:** implement each dimension independently, with per-lens tests and explicit coverage limits.
4. **Review surface:** optional human-readable report index; any PR comments or notifications require separate opt-in.
5. **Package integration:** optionally package the observer using the signed receiver-approved exchange protocol. A valid signature does not authorize installation or execution.

## Relationship to the design anchor

The package-exchange design at commit `ae89abe4a44d90429fcf5316bdb196316a1de6cb` supplies the governing principles: identity-bound evidence, provenance, least privilege, receiver control, explicit approval, staged validation, and reversibility. Branch Horizon applies those principles to discovery across repository dimensions; it does not inherit authority to mutate branches or install packages.

## Current implementation status

This file is a design proposal. It does not claim that the push trigger, rotating lens selector, scanners, reports, or tests have been implemented.
