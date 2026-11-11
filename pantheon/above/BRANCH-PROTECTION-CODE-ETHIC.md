# Branch Protection — Above-Pantheon Code Ethic

## Status and boundary

This document defines the ethical and procedural contract for protecting source branches before a proposal reaches Pantheon. It is a governance specification. It does **not** configure GitHub branch rules, change repository permissions, merge a pull request, or make any branch protected by itself.

## Governing principle

**Protect the origin, preserve branch identity, require review before adoption, and make every authorized change traceable and recoverable. No branch—including `main`—may be overwritten, merged, force-pushed, or deleted by inferred intent or automated learning.**

A branch is an attributable line of work, not disposable workspace. Protect its identity, history, contributors, and right to remain distinct. A merge is an adoption decision and therefore requires an explicit, reviewed, authorized operation; this ethic prohibits automatic adoption, not a properly reviewed human-approved merge.

Above-Pantheon may observe, compare, explain, and propose branch changes. It may not directly rewrite refs, merge branches, delete branches, alter protection settings, or treat a proposal as authorization. Pantheon must validate the request at the execution boundary, and the repository platform must enforce the applicable controls.

## Required protections

For the default branch and every protected/shared integration branch, repository administrators should configure platform-enforced rules equivalent to:

1. Require pull requests for changes; prohibit direct pushes except narrowly defined, audited break-glass administration.
2. Require at least one independent approving review. Require code-owner review for designated sensitive paths where CODEOWNERS is maintained.
3. Dismiss stale approvals when new commits materially change the reviewed diff; require approval of the latest revision.
4. Require all designated status checks to pass, including the relevant C++11 build, tests, and security/provenance checks. Do not mark a check as passing when it has not run.
5. Require conversation resolution before merge.
6. Require branches to be up to date with the base branch where the project's integration model requires it; do not use this requirement to erase independent branch identity.
7. Block force pushes and branch deletion on protected branches.
8. Restrict who may bypass rules; keep bypass exceptional, named, logged, and reviewable.
9. Protect release tags and provenance records against silent replacement or deletion.
10. Retain an independently verified recovery point before any approved exceptional rewrite.

Use the platform's current ruleset/branch-protection capabilities. Select settings deliberately; do not claim that a listed control is active until the repository configuration has been inspected and verified.

## Branch identity and lineage

- Keep each branch's purpose, base, owner/contributors, and origin visible.
- Preserve branch identities as independent histories until a reviewed adoption is explicitly approved.
- Prefer an attributable successor branch or commit when correction can be made without rewriting history.
- Preserve original commits and source records as evidence.
- Record the old and new commit IDs, reason, review, approvals, validation, and recovery reference for any exceptional history rewrite.
- Never silently rename, transplant, squash, delete, or overwrite another contributor's work.

## Above-Pantheon proposal contract

Every proposed branch operation must identify:

- repository and exact branch/ref;
- operation (create, update, merge, rebase, delete, protect, or rewrite);
- intended outcome and reason;
- exact commit range or patch identity, when applicable;
- affected contributors and downstream dependencies;
- evidence, tests, unresolved uncertainty, and risk;
- authorization from the repository owner or delegated authority;
- recovery path and expiry for any temporary authorization.

If any field is missing or the target changes after review, stop and request a new review. Silence, prior approval, inferred intent, learning scores, symbolic language, or urgency are not authorization.

## Decision gates

| Gate | Required behavior |
|---|---|
| Observe | Read only refs and records the requester is already authorized to access. |
| Propose | Prepare a diff or branch plan without mutating shared refs or settings. |
| Review | Show the exact target, change, evidence, risks, and recovery plan to an authorized reviewer. |
| Authorize | Obtain explicit approval for that exact operation and target. |
| Apply | Use the narrowest platform permission; prefer protected pull-request workflows. |
| Verify | Read back refs/rules, inspect the resulting diff, and run required checks. |
| Recover | Stop on mismatch or failure; use the verified recovery point under renewed authorization. |

## Exceptional operations

Force-pushes, history rewrites, branch deletion, protection-rule changes, and bypasses are destructive or authority-sensitive operations. Deny by default. They require a separate, exact plan and explicit approval; a general request to protect, improve, propagate, or execute code does not authorize them. Follow [Force Rewrite Protocol](../FORCE-REWRITE-PROTOCOL.md) for history changes.

## Learning without privilege creep

The upper layer may learn which explanations, reviews, checks, and recovery plans improve quality. It must not learn its way into ownership, bypass rights, write authority, merge authority, or permission to weaken branch protections. A successful prior change is evidence for a future proposal, never a standing authorization.

## Enforcement and verification

The policy becomes operational only when all three layers agree:

1. **Repository platform:** branch rules/rulesets actually enforce the required controls.
2. **Workflow:** pull requests, reviewers, required checks, and audit records follow those controls.
3. **Pantheon boundary:** runtime authorization rejects unapproved or out-of-scope branch mutations.

Record the repository, branch/ruleset name, inspected settings, inspection time, and verification evidence. If platform settings cannot be inspected, report protection as **unverified**, not enabled.

**Protect the branch before changing the branch. Preserve the source before correcting the source. Human authorization remains above automation.**
