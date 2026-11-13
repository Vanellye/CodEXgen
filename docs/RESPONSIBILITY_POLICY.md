# ERIA Repository Responsibility Policy

## Non-negotiable boundaries

- No workflow may merge a pull request automatically.
- No workflow may deploy, publish, release, or dispatch external actions without a separately reviewed and explicitly authorized change.
- No hardware, actuator, pump, valve, or treatment-system control may be added to CI.
- CI credentials remain least-privilege and read-only unless a separately reviewed task requires otherwise.
- Every consequential change retains source provenance and a reviewable commit history.
- A passing test is evidence for the tested scope only; it is not deployment, hardware, safety, or product-release authorization.

## Review gate

The `ERIA Responsibility Gate` requires an approval from a reviewer other than the pull-request author. The latest review from each reviewer is considered; a later change-request or dismissal supersedes an earlier approval.

The `CODEOWNERS` file identifies sensitive paths. This only becomes a merge control when repository rules require Code Owner review.

## Required repository settings

A repository administrator must configure a ruleset for `main` that:

1. Requires pull requests before merging.
2. Requires at least one approval from someone other than the author.
3. Requires Code Owner review.
4. Requires the `Independent human approval` status check and the existing CI checks.
5. Dismisses stale approvals when new commits are pushed.
6. Requires conversation resolution.
7. Blocks force pushes and branch deletion.

The repository currently has no rulesets configured. This commit does not claim that these server-side controls are active. If rulesets cannot be configured, the policy remains a documented and CI-tested gate, not a guaranteed block against direct writes or administrator overrides.

## Deployment policy

There is no deployment authorization in this policy. A future deployment workflow must be a separate proposal, use a protected environment with required reviewers, use narrowly scoped credentials, and have a human-approved deployment record. No such workflow is created here.

## Current scope

This policy adds review enforcement only. It does not merge PRs, deploy software, perform external dispatch, or activate physical equipment.
