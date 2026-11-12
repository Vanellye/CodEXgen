# ERIA ĎÏÎ§Ŝ Authorization and Patch Gate

**Status:** Proposed operating contract, committed on the isolated `transmission` branch.  
**Scope:** Local source intake, local persistence, patch preparation, and any separately requested consequential operation.

## Name and purpose

`ĎÏÎ§Ŝ` is the ERIA authorization-and-patch gate. It separates a proposed change from permission to perform that change. The gate makes authority, scope, provenance, verification, and outcome explicit before an operation can proceed.

The gate is a control boundary, not an authorization source. It cannot grant itself permission, infer consent from a trigger, or convert one approval into another.

## Non-inheritance of permissions

The following capabilities are independent. Approval for one does not imply approval for any other:

| Scope | Permitted operation |
|---|---|
| `source.collect` | Accept caller-supplied source bytes into a provenance envelope |
| `source.store` | Persist a verified source record in the approved local app-private store |
| `source.read` | Retrieve a stored record |
| `patch.prepare` | Prepare a reviewable patch without applying it |
| `repository.modify` | Apply an approved change to a specified repository and branch |
| `execute` | Run a specified program or test command in a specified environment |
| `publish` | Publish an identified artifact to an identified destination |
| `transmit` | Send identified data to an identified external destination |

No scope is inherited, implied, bundled, or expanded by another scope. In particular, local collection or storage does not authorize repository modification, execution, publication, or transmission.

## Default-deny decision rule

A consequential operation is denied unless its authorization is explicit, current, attributable to the responsible human approval process, and bound to the exact operation.

The authorization record must identify, as applicable:

- operation and narrowly defined scope;
- source and destination;
- repository and branch, or execution environment;
- exact content digest or patch identity;
- purpose and data being handled;
- approval reference and approving authority;
- validity period and any applicable limits.

Missing, ambiguous, mismatched, expired, or unverifiable authorization means **deny**. A trigger, webhook, event, detected condition, background process, or successful integrity check is never permission to act.

External transmission, publication, and dispatch remain disabled unless separately and explicitly authorized for the particular payload, destination, and purpose. This document does not grant any such authorization.

## ĎÏÎ§Ŝ patch flow

1. **Detect:** Record the proposed operation as a proposal only. Detection has no side effect.
2. **Separate:** Identify the exact capability required. Do not conflate collection, storage, reading, preparation, modification, execution, publication, or transmission.
3. **Preserve:** Retain the original source and its provenance. Create a digest for the exact bytes under review.
4. **Verify:** Check the source envelope, digest, patch scope, target branch, and applicable tests. Record what was and was not verified.
5. **Authorize:** Obtain a distinct human approval bound to the exact operation and target. No self-approval or inferred approval.
6. **Act:** Perform only the approved operation, within its stated limits. If approval is absent or the target changes, stop.
7. **Witness:** Record the result, resulting commit or artifact identity, verification evidence, and any failure.
8. **Recover:** Preserve the prior state and provide a tested, reviewable recovery path where mutation occurred.

## Patch workaround flow

A blocked or failed operation must not be bypassed. ERIA may instead:

- preserve the rejected proposal and its reason;
- produce a non-applied patch for human review;
- identify missing authorization or failed checks;
- offer a safe local test or simulation that does not contact external systems;
- retry only after the relevant condition is corrected and the required approval is obtained.

A workaround must not conceal execution, alter the authorization decision, broaden scope, or dispatch data externally.

## Repository safeguards

- Work on a named, isolated branch until a separate promotion decision is approved.
- Do not modify `main`, merge, force-push, publish, or release merely because a patch is prepared or tests pass.
- Bind approval to the reviewed diff and expected branch head. If either changes, require re-review.
- Preserve commit history and source lineage; corrections are traceable successors, not silent replacements.
- Keep automated checks advisory unless a human-approved policy explicitly defines their enforcement role.

## Audit record

For each gated operation, record the proposal, requested scope, approval reference, source and target identities, verification results, action outcome, and recovery information. Do not record secrets or unnecessary personal data.

## Current implementation boundary

The existing local source collector and store implement only the local collection, persistence, and retrieval portions of this contract. They do not implement a cryptographic identity or approval service, patch application, repository mutation, execution, publication, or external transmission. The current local record format is not encrypted at rest; see [LOCAL-SOURCE-STORAGE.md](LOCAL-SOURCE-STORAGE.md).

This document defines the intended authorization contract. It does not claim that every control is already enforced by runtime code.
