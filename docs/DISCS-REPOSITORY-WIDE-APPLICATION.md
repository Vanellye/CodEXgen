# ERIA ĎÏÎ§Ŝ Repository-Wide Application Matrix

**Status:** Repository-wide policy and implementation inventory  
**Policy owner:** Human maintainer  
**Applies to:** Every module, tool, workflow, generated artifact, and future integration in this repository

The ĎÏÎ§Ŝ authorization-and-patch gate in [DISCS-AUTHORIZATION-AND-PATCH-GATE.md](DISCS-AUTHORIZATION-AND-PATCH-GATE.md) is the governing contract for the entire repository. A directory or language boundary does not exempt a component.

## Universal rules

1. Treat every event, trigger, webhook, schedule, scan result, quality score, and successful test as information—not authorization.
2. Require a distinct, explicit, scope-matched approval for each consequential capability.
3. Do not infer transmission, publication, execution, repository mutation, credential access, or hardware actuation from local collection or storage permission.
4. Preserve source, provenance, exact patch identity, and prior state before a change.
5. Fail closed on missing, ambiguous, stale, mismatched, or unverifiable approval.
6. Keep proposals and simulations non-mutating. Record whether an action actually occurred.
7. Bind approvals to the target, content digest, branch, destination, purpose, and limits relevant to the operation.
8. Re-review when the approved diff, branch head, destination, or requested operation changes.

## Repository-wide coverage

| Area | Examples in this repository | Required gate behavior |
|---|---|---|
| Android application and UI | `app/src/main`, `compose/` | UI actions must distinguish review from commit, local write, execution, and external calls. A button or saved token is not an approval. |
| Contracts and envelopes | `app/src/main/.../contracts/` | Validate structure and provenance separately from authorization. Valid data never grants action permission. |
| Pantheon runtime and native contracts | `app/src/main/.../pantheon/`, `pantheon/` | Hold by default; exact scope matching; review-ready is not execution approval. C modules remain contracts, not privileged adapters. |
| Git bridge and credentials | `GitFreedomBridge.kt`, `GitBridgeScreen.kt`, `GitBridgeModels.kt`, `TokenVault.kt` | Local import/commit, remote fetch, push, force-with-lease, pull-request creation, and credential save/clear are distinct operations requiring distinct authorization. Never treat a configured token as user approval. |
| Source intake and local persistence | `app/src/main/.../source/` | Keep collection, storage, and retrieval scopes separate; verify content digest and read-back. Local storage does not authorize export. |
| Python utilities and generators | `python/`, `generated_modules/` | Analysis and generation are proposals until separately approved for file writes, execution, or replacement of generated output. |
| Shell tools and hooks | `tools/`, `.githooks/` | Default to read-only checks. Any repair, deletion, execution beyond the declared check, or network call needs its own scope and review. |
| CI and dependency automation | `.github/workflows/`, `.github/dependabot.yml` | CI may validate; it must not silently publish, deploy, merge, rewrite source, change permissions, or dispatch externally. Dependency updates remain reviewable proposals. |
| Hypothetical and quarantined material | `hypotheticals/` | Preserve classification and provenance. Do not promote hypothetical material into factual/runtime code without evidence and review. |
| Documentation and generated reports | `docs/`, reports | Documentation may define policy but cannot grant credentials, permissions, or runtime capabilities. Generated reports are not approvals. |

## Capability separation

Use narrow scopes, with names adapted to the exact operation:

- `source.collect`
- `source.store`
- `source.read`
- `patch.prepare`
- `workspace.import`
- `repository.read`
- `repository.modify`
- `execute`
- `credential.store`
- `credential.delete`
- `publish`
- `transmit`
- `hardware.actuate`

A single approval must not silently cover multiple capabilities. If an operation contains multiple stages—for example, local commit followed by remote push—gate each stage separately.

## Current implementation status and known gaps

This matrix is a governance map, not proof that every existing adapter already enforces every rule.

- **Implemented boundaries:** The Android `PantheonRuntimeGate` validates envelopes and produces review-only results; the source collector and local store implement separate local collection, persistence, and retrieval scopes; Pantheon C contracts reject missing or mismatched approval and do not execute actions.
- **Existing Git bridge requires further enforcement:** `GitFreedomBridge` contains remote fetch/clone, push, force-with-lease, and pull-request operations, as well as local import and commit. Its current API uses configured credentials and branch checks, but does not yet require a ĎÏÎ§Ŝ operation-specific approval object for each of those actions. Treat those paths as **not yet gate-enforced**. Do not interpret this policy commit as enabling or authorizing them.
- **Credential controls:** `TokenVault` encrypts a user-supplied token with Android Keystore, but save and clear actions need their own explicit UI authorization treatment.
- **Local source record encryption:** The current source-store record is not encrypted at rest. See [LOCAL-SOURCE-STORAGE.md](LOCAL-SOURCE-STORAGE.md).
- **Approval authenticity:** Current authorization values are caller-supplied assertions, not cryptographic proof of approver identity or legal consent.
- **Automation:** CI checks are validation only. They do not constitute human approval to merge, publish, deploy, or transmit.

## Rollout order

1. Keep this contract and matrix as the common acceptance standard for every module.
2. Inventory each side-effecting entry point and its call sites.
3. Add explicit operation-specific approval inputs at those boundaries.
4. Separate compound actions (especially local commit from remote push).
5. Add negative tests proving missing, mismatched, expired, and wrong-target approvals are denied.
6. Verify that denied operations leave local and remote state unchanged.
7. Promote only through a separately reviewed pull request and explicit human decision.

Until a boundary passes those tests, mark it **not yet gate-enforced**. Do not describe policy documentation alone as runtime enforcement.
