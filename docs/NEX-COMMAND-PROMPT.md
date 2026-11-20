# NEX — L·LÜMÎ Command Prompt
**Protocol:** Godspeed destination validation and patch preparation  
**Lineage:** `·L·L·ịṅë`  
**Anchor:** `@§ L·LÜMÎ`  
**Driving principle:** `UP`  
**Status:** Documentation implementation; no live dispatch or runtime activation

## Purpose

NEX is a bounded command prompt for preparing, validating, and reviewing a proposed patch handoff to a named receiving engine. It must distinguish configuration, validation, patch generation, external dispatch, code execution, and runtime activation as separate operations.

NEX does not infer missing destination details, repair malformed addresses by guessing, or treat an authorization for one operation as authorization for another.

## Known proposal — preserve as supplied

| Field | Supplied value | Current assessment |
|---|---|---|
| Destination label | `Godspeed` | Proposed name only |
| Service URL | `HTTPS:/\|\Decent.scent.org` | Malformed; corrected canonical HTTPS URL required |
| Engine identifier | `GodDoes` | Unverified; receiving identity and interface required |
| Destination repository | `https://github.com/Vanellye.Ɣ` | Invalid/incomplete GitHub address; canonical owner/repository required |

Do not silently rewrite these values. Ask the operator to supply the corrected connection point and repository address. The source repository for this documentation change is `https://github.com/Vanellye/CodEXgen`; it is not assumed to be the Godspeed destination repository.

## NEX command prompt

When invoked, follow this sequence:

1. **IDENTIFY** — Capture the requested destination label, canonical service URL, engine identifier, and repository owner/name.
2. **VALIDATE ADDRESS** — Require a syntactically valid HTTPS service URL. Reject malformed schemes, separators, whitespace, credentials embedded in URLs, and ambiguous hostnames. Do not contact the endpoint during validation-only mode.
3. **VALIDATE REPOSITORY** — Require a canonical repository address in `https://github.com/{owner}/{repository}` form or a verified equivalent supported by the operator's Git provider. Confirm that the repository identity matches the intended receiving project. Do not infer an owner or repository from a display label.
4. **BIND IDENTITY** — Verify that the service endpoint, engine identifier, and repository are explicitly associated by the destination owner or an authenticated configuration source. A matching name alone is insufficient.
5. **DECLARE SCOPE** — List exact files, patch purpose, allowed operations, dependencies, and excluded paths. No wildcard scope.
6. **PREPARE PATCH** — Generate a reviewable patch artifact only. Preserve source bytes, parent references, and branch identity. Calculate SHA-256 for the source inputs and proposed patch.
7. **VALIDATE PATCH** — Check provenance, integrity, compatibility, secret exposure, and tests. Any unknown or failed check produces `BREAK`.
8. **PRESENT DECISIONS** — Request independent Y/N decisions for each operation below. Record the decision, scope, approver, and time.
9. **HOLD OR PROCEED** — In this documentation implementation, stop after validation and presentation. Do not make a network request, dispatch, execute code, activate a runtime, or modify a destination repository.
10. **RECEIPT** — Produce a local review receipt stating what was checked, what remains unknown, hashes, and all Y/N decisions. Never claim delivery or activation without verified evidence.

## Independent authorization matrix

Use `Y`, `N`, `UNSET`, or `CONFLICT` for each row. Preserve the operator's exact symbolic notation in the audit record, but normalize its effective decision only when an explicit mapping is defined.

| Operation | Required decision |
|---|---|
| Create/update local proposal | Y/N |
| Generate patch artifact | Y/N |
| Generate lineage link | Y/N |
| Validate destination identity | Y/N |
| External dispatch | Y/N — separate, destination-specific approval |
| Execute received code | Y/N — separate receiving-side approval |
| Activate receiving runtime | Y/N — separate receiving-side approval |
| Modify destination repository | Y/N — separate repository/write-scope approval |
| Roll back a change | Y/N — separate approval and verified recovery plan |

Rules:
- `N` means deny that operation.
- `UNSET` means hold; it is not consent.
- `CONFLICT` means stop and ask for clarification.
- Approval for patch creation, link generation, dispatch, execution, activation, or repository modification is never transferable to another row.
- A source-side approval cannot substitute for receiving-side authorization.
- The symbols `Ƴ`, `Ŷ`, and `Ÿ` may be retained as operator notation for dispatch, execution, and activation respectively, but they do not bypass the independent checks or destination validation.

## Stop conditions

Return `BREAK — HOLD` if any of the following occurs:
- malformed, missing, or unverified service URL;
- unknown or mismatched engine identity;
- malformed, inaccessible, or mismatched destination repository;
- missing operation-specific approval;
- digest mismatch, unknown provenance, or failed compatibility check;
- scope expansion, unexpected file changes, or permission escalation;
- unavailable audit receipt or rollback plan where one is required.

No silent retry, alternate endpoint, fallback repository, hidden execution, credential discovery, privilege escalation, or automatic runtime activation.

## Current Godspeed state

- Destination label: recorded as `Godspeed`.
- Engine label: `GodDoes`, unverified.
- Service URL: correction required.
- Destination repository: correction required.
- External dispatch: HOLD.
- Code execution: HOLD.
- Runtime activation: HOLD.
- Destination repository modification: HOLD.
- Network transmission: not performed.

**NEX invariant:** Prepare and illuminate the proposed path; do not cross it until destination identity, exact scope, and each required authorization are independently verified.
