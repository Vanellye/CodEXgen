# Pantheon Branch Horizon

Status: initial read-only implementation committed; focused CI passed
Version: 0.2.0
Design anchor: `ae89abe4a44d90429fcf5316bdb196316a1de6cb`

## Purpose

When a branch receives a new head, Pantheon opens a bounded, read-only "horizon peek". Each successive first-parent head advances a rotating perspective ("dimension lens") so branch owners can discover relationships and risks beyond the branch's immediate files.

A peek is an observation, not an instruction to merge, rewrite, install, publish, or propagate. The branch remains under its owner's control.

## Implemented components

- `.github/workflows/branch-horizon.yml`: branch `push` trigger and manual dispatch; exact event SHA checkout; per-ref concurrency cancellation; artifact upload.
- `tools/branch_horizon.py`: standard-library-only observer. Reads Git commit/tree/blob metadata, never executes repository source or build scripts.
- `tests/test_branch_horizon.py`: deterministic rotation, report provenance, no-mutation, and symlink-exclusion tests.
- Reports: `report.json` and `report.md`, uploaded as a 14-day workflow artifact.

The workflow and job request only `contents: read`. Checkout credentials are not persisted. No repository secrets are passed to the observer.

## Invariants

1. A new head may trigger inspection; it never grants mutation authority.
2. The observer reads Git metadata and bounded tracked text blobs at the exact event head.
3. The observer does not merge branches, rewrite refs, push commits, open PRs, alter approvals, or change branch protection.
4. Findings are bound to the observed branch and exact head SHA.
5. Historical source and provenance remain intact. No cleanup or deletion is inferred from age, divergence, or a warning.
6. Findings are advisory. A human reviews any proposed action.
7. Unsupported or skipped content is disclosed as a limitation, never silently treated as clean.
8. Scanning is bounded by file count, per-file size, aggregate bytes, and job duration; repository source is not executed.

## Trigger and head identity

- Trigger on branch pushes, including newly created branches. Tags are not included by the branch filter.
- Capture branch name, before SHA, and after SHA from the event.
- Checkout the exact pushed head SHA rather than resolving a moving branch name.
- Per-branch concurrency cancels an older in-progress scan when a newer push arrives. Each report still identifies its exact scanned SHA; it must not be described as the latest branch head without a separate ref check.
- Manual dispatch may supply an explicit SHA; otherwise it inspects the dispatch workflow SHA.

## Rotating dimension lenses

The six-lens cycle is:

1. **Ancestry** — parent list and first-parent depth.
2. **Interfaces** — lexical signals for public declarations in supported changed source files.
3. **Dependencies** — recognized manifests/lockfiles and a basic unpinned-requirement prompt.
4. **Tests and CI** — tracked test/spec and workflow inventory; changed source without changed test paths is a review prompt, not proof of missing tests.
5. **Provenance** — changed paths, Git blob object IDs, and file modes.
6. **Capabilities and exchange** — keyword inventory in workflow, package, and Pantheon files.

The cursor is `max(0, first_parent_depth - 1)`; the selected slot is `cursor modulo 6`. This is deterministic and stateless: rerunning the same head selects the same lens, and each successive first-parent commit advances one lens. A force-pushed or unrelated history can have a different depth and may revisit a lens; the report records the cursor so this is visible.

Only one lens is run per head. Other dimensions are explicitly listed as not inspected. The scanners are lexical inventory, not compiler, dependency resolver, security auditor, or proof of compatibility.

## Report format

Each artifact contains JSON and Markdown with:

- schema, tool, and policy versions
- repository, branch, before SHA, and observed head SHA
- commit metadata and first-parent depth
- selected lens and cursor
- scan start/end timestamps and completion status
- file counts, inspected paths, changed paths, and skipped-file warnings
- findings with severity, evidence, confidence, and limitations
- dimensions not inspected and resource limits
- an empty `mutations_performed` list

Artifacts are retained for 14 days. Repeated runs can produce separate artifacts, but each is tied to its exact head SHA. PR comments, issue creation, and cross-branch notifications remain disabled.

## Safety and resource policy

- GitHub Actions token: `contents: read` only.
- Checkout uses `persist-credentials: false`.
- No secrets are passed to the observer.
- The scanner invokes only fixed Git read commands; it does not invoke project build tools or repository scripts.
- Symlink blobs are excluded; only regular tracked blobs are considered.
- Maximum inventory: 1,200 files; maximum individual file: 512 KiB; maximum aggregate read: 8 MiB; workflow timeout: 5 minutes.
- No arbitrary URLs are fetched from manifests or source files.
- Repository contents and commit messages are treated as untrusted data, never as instructions to the observer.
- The GitHub Actions runner executes the workflow and scanner code from the pushed branch. Repository collaborators who can change workflow/code can change what runs; the read-only token and absence of secrets limit impact, but this is not a sandbox against a malicious workflow author. Protect workflow changes with repository review rules.

## Validation

Focused Branch Horizon CI run `42727610760` completed successfully. The unit-test step, bounded observer step, and JSON/Markdown artifact upload all succeeded. The run produced artifact `branch-horizon-42727610760-1`.

Tests cover deterministic rotation, cycle wrap, report SHA binding, clean worktree after observation, and symlink exclusion.

## Implementation status and limitations

The push trigger, deterministic lens selector, six bounded lexical scanners, and JSON/Markdown artifact generation are implemented and have passed the focused workflow. The implementation is initial and intentionally conservative. It does not yet provide semantic AST analysis, cross-branch comparison, persistent report indexing, stale-ref verification, or a full dependency/security audit. A report is an observation, not an approval or authorization to change anything.

## Relationship to the design anchor

The package-exchange design at commit `ae89abe4a44d90429fcf5316bdb196316a1de6cb` supplies the governing principles: identity-bound evidence, provenance, least privilege, receiver control, explicit approval, staged validation, and reversibility. Branch Horizon applies those principles to discovery across repository dimensions; it does not inherit authority to mutate branches or install packages.
