# Pantheon Branch Horizon

Status: read-only branch observer with cross-branch peering; latest CI validation pending
Version: 0.3.1
Design anchor: `ae89abe4a44d90429fcf5316bdb196316a1de6cb`

## Purpose

When a branch receives a new head, Pantheon opens a bounded, read-only horizon peek. It compares that exact head against already-fetched remote branches and emits reviewable interface/dependency relationship signals. It does not merge, adopt, install, approve, or propagate changes.

## Seven dimensions — six rotating, one sacred

The model has seven dimensions:

1. **Ancestry** — parent list and first-parent depth.
2. **Interfaces** — lexical declaration signals in supported changed source files.
3. **Dependencies** — recognized manifests, lockfiles, and basic version-spec signals.
4. **Tests and CI** — tracked test/spec and workflow inventory.
5. **Provenance** — changed paths, Git blob IDs, and file modes.
6. **Capabilities and exchange** — keyword inventory for workflow/package policy signals.
7. **Sacred** — an always-on invariant, not a rotating task or an authority claim.

The six operational lenses rotate by first-parent depth:
`cursor = max(0, first_parent_depth - 1)`; `slot = cursor modulo 6`.
The same observed head deterministically selects the same operational lens. Each successive first-parent head advances one slot. Force-pushed or unrelated histories may revisit a slot; the report records the cursor.

**Sacred is always active for every scan and every peer comparison.** Its governing rules are preservation of provenance, consent, receiver control, and reversibility. It means:
- no automatic merge, adoption, installation, approval, or propagation;
- exact commit identities are retained in the evidence;
- proposals are advisory and require explicit human/receiver review;
- no branch or source mutation is performed by peering.

Sacred is a software policy invariant, not a statement that the scanner can certify moral, spiritual, or semantic correctness.

## Cross-branch peering

The observer enumerates only already-fetched `refs/remotes/origin/*` branch refs. It does not fetch, update, or create refs. It excludes the currently observed branch and the symbolic `origin/HEAD` ref. A zero-peer result is explicitly reported as `no_remote_branch_refs_visible`; it does not claim that the repository has no other branches. Reaching the peer cap or truncating a peer snapshot marks the report incomplete.

For each peer, the report records:
- branch name, ref, and exact peer commit SHA;
- ahead/behind commit counts relative to the observed head;
- shared interface declaration names, identical lexical declarations, and differing declarations;
- shared dependency names, matching specs, and differing specs;
- file-read counts and truncation status;
- a classification and a human-review-only proposal.

Classification:
- `review_required`: a shared declaration has different lexical text or a shared dependency has a different declared version/spec.
- `shared_signals_only`: identical declaration or dependency signals exist, with no detected differences.
- `unknown_no_shared_signals`: no useful overlap was detected; this is not evidence of incompatibility.
- `unknown_incomplete`: a peer snapshot exceeded a configured bound.

A different dependency spec is a potential conflict, not proof that versions are incompatible. Identical declaration text is a shared signal, not proof of ABI, type, runtime, or behavioral compatibility. The report therefore never labels a peer "safe to merge."

Limits: at most 24 remote branches; at most 300 tracked files per peer snapshot; at most 128 KiB per peer file; at most 1 MiB of peer text per snapshot. The observed head is subject to the original 1,200-file, 512 KiB per-file, and 8 MiB aggregate limits. Branches outside the already-fetched remote view are unknown, not absent.

## Implemented components

- `.github/workflows/branch-horizon.yml`: branch push trigger and manual dispatch; exact event SHA checkout; per-ref concurrency cancellation; JSON/Markdown artifact upload.
- `tools/branch_horizon.py`: bounded Git metadata/blob observer, six-lens selector, always-on Sacred invariant record, and cross-branch peering.
- `tests/test_branch_horizon.py`: deterministic rotation, Sacred separation, report provenance, no-mutation, symlink exclusion, and peer conflict tests.
- Artifacts: `report.json` and `report.md`, retained for 14 days.

Workflow and job permissions are `contents: read`; checkout credentials are not persisted. No repository secrets are passed to the observer.

## Safety and resource policy

- No repository source or build scripts are executed.
- No Git refs, files, approvals, or branch protections are modified.
- Only fixed Git read commands are invoked.
- Symlink blobs are excluded.
- No arbitrary URLs are fetched from source or manifests.
- Repository contents and commit messages are treated as untrusted data, never as instructions.
- The GitHub Actions runner executes workflow and scanner code from the pushed branch. Repository collaborators who can modify workflow/code can change what runs; the read-only token and absence of secrets limit impact but do not sandbox a malicious workflow author. Protect workflow changes with repository review rules.

## Report contract

Each report includes schema/tool/policy versions, repository and branch, before/head SHAs, commit metadata, selected operational lens and cursor, Sacred policy record, scan timestamps, files inspected, findings with evidence/confidence/limitations, peer comparisons, uninspected dimensions, resource limits, and an empty `mutations_performed` list.

No PR comments, issues, notifications, or cross-branch writes are enabled. A proposal never grants adoption authority.

## Validation

Focused workflow validation is run on each branch-head update. The workflow runs the dedicated Branch Horizon unit tests before scanning and uploading artifacts. The test suite covers six-lens rotation, Sacred as the non-rotating seventh dimension, exact head binding, no mutation of refs/worktree, symlink exclusion, and detection of differing interface/dependency signals across a peer ref.

## Limitations and next review gates

This is lexical discovery, not a semantic compiler, dependency solver, security audit, ABI checker, or merge simulator. It does not yet calculate symbol-level type graphs, resolve transitive dependencies, compare all branches outside the fetched view, or create a durable peer index. All discovered relationships are proposals for human review.

Before any future adoption feature, require a separate signed proposal bound to exact source/receiver SHAs, an explicit receiver approval, scoped capabilities, staged validation, and a rollback plan. The current observer does not implement adoption.

## Governing design anchor

The signed package-exchange design at commit `ae89abe4a44d90429fcf5316bdb196316a1de6cb` supplies identity-bound evidence, provenance, least privilege, receiver control, explicit approval, staged validation, and reversibility. Branch Horizon applies those principles to branch discovery without inheriting authority to change branches or install packages.
