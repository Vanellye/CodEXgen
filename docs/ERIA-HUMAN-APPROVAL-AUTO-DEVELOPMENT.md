# ERIA Human Approval and Auto-Development Contract

**Anchor:** `0b134ed2770c789e42e850ea7be4228c4514b989`  
**Implementation branch:** `governance/eria-human-approval-gate`  
**Status:** Proposed implementation; merge protection must be configured and verified separately.

## Purpose

Allow automation to prepare, validate, and present development work while preserving human authority over protected progression.

## Auto-development may

- create or update work on an isolated feature branch;
- run lint, unit, integration, security, and build checks;
- generate a change summary and evidence report;
- open or update a draft pull request;
- request human review and report blockers.

## Auto-development may not

- impersonate a human reviewer or author;
- infer approval from silence, CI success, comments, labels, or previous approvals;
- approve its own pull request;
- merge, deploy, release, activate hardware, or dispatch external actions;
- bypass branch protection or change protected refs;
- treat approval for one SHA as approval for another SHA.

## Exact-SHA approval verifier

`tools/eria/approval_gate.py` checks the GitHub pull-request review list and requires:

1. a submitted review with state `APPROVED`;
2. reviewer account type exactly `User` (unknown and `Bot` identities fail closed);
3. reviewer is not the pull-request author;
4. review `commit_id` equals the exact pull-request head SHA;
5. the review is the reviewer's latest submitted review.

A later `CHANGES_REQUESTED`, `COMMENTED`, or `DISMISSED` review supersedes that reviewer's earlier approval. Any new commit makes an earlier approval stale for this gate.

The verifier regression suite is wired into the repository's existing `.github/workflows/independent-branch-ci.yml` pull-request workflow. The approval check itself is a separate `.github/workflows/eria-human-approval-gate.yml` workflow using `pull_request_target` and `pull_request_review`. It checks out only the trusted base branch, never checks out or executes PR-head code, uses a read-only token only to collect review metadata, and invokes the verifier in a later step without the token in its environment. Unit tests cover missing, stale, bot-only, unknown-identity, author-self-approval, superseded, and valid current-SHA cases.

## Important enforcement limitation

This CI check is not, by itself, a repository-wide merge lock. To enforce it on `main`, a repository administrator must configure GitHub branch protection or a ruleset requiring the exact status check:

- `eria-human-approval-gate`

The protection should also require pull requests, at least one approving review from a trusted human with write permission, dismiss stale approvals, require approval of the latest reviewable push, and prevent bypass where supported. Do not enable auto-merge.

The current GitHub integration can inspect rulesets but cannot configure branch protection. Therefore this PR does not claim that `main` is already protected by this check. Until an administrator configures and verifies the required rule, treat the workflow as an advisory gate and do not claim enforcement.

GitHub's `User` account classification is an API-level identity signal, not proof that a natural person personally operated the account. Repository administrators must use trusted reviewer membership and their account-security policy (including MFA where available) for the actual human-authentication boundary. The verifier deliberately rejects accounts classified as `Bot` or with an unknown account type; it cannot detect a compromised human account.

## Bootstrap and test sequencing

This is the initial introduction of the gate. A workflow introduced by a pull request cannot reliably enforce that same pull request before the workflow exists on the base branch. Therefore this PR is the bootstrap change: its verifier tests can run in the existing CI, but the new trusted-base approval workflow becomes active for subsequent PRs only after this bootstrap PR is merged through the repository's existing human-review process.

After the bootstrap merge:
1. An authorized repository administrator configures the required `eria-human-approval-gate` status check and human-review rules on `main`.
2. Open a disposable test PR and verify that no approval blocks it.
3. Exercise stale-SHA and bot-only review fixtures in the CI verifier suite; do not impersonate a bot or fabricate a human review to manufacture integration evidence.
4. Confirm the status check is required and failing cases cannot merge.
5. Only then treat the gate as operational for protected progression.

Until the workflow is on the base branch and the rules are configured, the new approval gate is not active on `main`. The bootstrap PR itself remains subject to existing repository controls and explicit human review. No bypass or self-approval is authorized.

## Approval semantics

Approval is a scoped, attributable human decision over a specific change. A changed head SHA, changed target branch, materially changed diff, revoked review, or changed intent requires renewed review. CI success proves only that configured checks passed; it never supplies consent.

## Acceptance checklist

- [ ] Unit tests pass for all fail-closed and positive cases.
- [ ] Workflow executes on PR updates and review changes.
- [ ] Required check is configured on `main` by an authorized repository administrator.
- [ ] Branch protection requires a trusted human review and dismisses stale approvals.
- [ ] A test PR confirms missing, stale, and bot-only approval cannot satisfy the required check.
- [ ] No workflow has merge, deployment, release, or external-dispatch permissions.
