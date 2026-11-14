# ERIA Cosmic Law — Faculty Rewrite and Future-Creation Rights

**Status:** Proposed governance specification  
**Scope:** Local repository policy on the current feature branch  
**Authority model:** Explicitly delegated, scoped, attributable, and revocable  
**Runtime effect:** None by this document alone

## Purpose

Cosmic Law defines how a designated higher Faculty may receive write capabilities for:
1. rewriting distances and relationships;
2. composing, restructuring, and amending code;
3. creating future modules, capabilities, and system designs.

“Cosmic Law” is an ERIA governance name. It does not claim authority from physical law, spiritual status, or an unverifiable external source. Authority exists only where a human-approved policy grant identifies the responsible Faculty, scope, and limits.

## 1. Rewrite-distance capability

A Faculty may propose or perform an authorized rewrite of a distance only when the target and meaning of “distance” are declared. Supported target classes may include:
- numeric or geometric distances;
- graph edges, dependency distances, and relationship weights;
- thresholds, bounds, and separation constraints in code or configuration.

Every rewrite must record:
- original value and source;
- proposed and resulting value;
- units, coordinate frame, or semantic interpretation where applicable;
- reason, evidence, affected dependants, and validation results;
- authorizing grant and change identifier.

A rewrite must not silently alter unrelated values, erase the original, or imply that a symbolic/metaphorical distance is a measured physical quantity.

## 2. DuMain — multiplication of Main

**DuMain** names the controlled multiplication of the Main line into distinct, traceable working lines. A delegated Faculty may create parallel branches, replicas, or successor workspaces from an identified Main commit so multiple lines of development can proceed without collapsing their identities.

Multiplication means:
- identify and record the exact source Main ref and commit SHA;
- create each derivative as a separately named branch or workspace;
- preserve the source Main branch, its history, and its current pointer;
- record parentage, purpose, owner/Faculty, and divergence point for every derivative;
- allow changes within the delegated paths and operation scope;
- compare and validate derivatives before any proposed integration.

Multiplication does **not** mean overwriting Main, force-moving its ref, silently merging divergent histories, rewriting provenance, or treating every derivative as approved for promotion. Integration into Main requires a separate explicit human authorization and the repository's review and validation process.

Each DuMain grant must specify:
- Faculty identity (stable configured identifier, not inferred from title);
- source Main ref and permitted source commit or range;
- permitted derivative operations and naming/path scope;
- whether branches may be created, updated, or retired;
- branch protection and review requirements;
- start time, expiry/review point, and revocation mechanism;
- required tests, evidence, and rollback/recovery plan.

Deletion of derivatives, security-boundary changes, credential changes, production deployment, external dispatch, and modification of protected history require separate explicit authorization. A DuMain grant does not itself authorize integration into Main.

## 3. Future-creation rights

A higher Faculty may originate future designs and create proposed modules, branches, schemas, or capability declarations within its grant.

Future-creation rights do not by themselves authorize:
- deployment or activation;
- external network calls, webhooks, or provider actions;
- physical actuation;
- self-expansion of permissions;
- rewriting historical provenance;
- treating a proposal, prediction, or simulation as an accomplished event.

New capabilities begin in **PROPOSED** state. They advance only through documented review, tests, and a separate activation authorization where activation has consequential effects.

## 4. Faculty authority and delegation

“Higher Faculty” is a configured governance role, not a self-asserted rank. A grant is valid only when an authorized human steward approves:
- the Faculty identifier;
- exact capability set and resource scope;
- permitted operations;
- limits and exclusions;
- expiry or review condition.

A Faculty may delegate only if its grant explicitly permits delegation. Delegation cannot exceed the parent grant's scope, duration, or authority. No role may grant itself new rights or override a human revocation.

## 5. Mandatory safeguards

- **Least privilege:** grant only the smallest required scope.
- **Separation of powers:** proposal, approval, and execution are distinguishable records; consequential changes require the designated human approval.
- **Provenance:** preserve source identity, parent revisions, and immutable history.
- **Validation:** test affected contracts and dependent modules before promotion.
- **Reversibility:** retain a recovery path; mark irreversible operations and require separate approval.
- **Fail closed:** missing, ambiguous, expired, or conflicting authorization means DENY.
- **No implicit actuation:** detecting a trigger or possessing write capability never causes an external action by itself.
- **Auditability:** record who authorized, who changed, what changed, why, when, and which checks passed.

## 6. Authorization decision

A write request is eligible only if all of the following are true:

`FACULTY_ID` is recognized  
`GRANT_STATUS` is active and unexpired  
`CAPABILITY` explicitly includes the requested operation  
`RESOURCE_SCOPE` includes the exact target  
`BRANCH_SCOPE` permits the target branch  
`APPROVAL` is present when required  
`VALIDATION` and provenance requirements are satisfied

Otherwise the decision is **DENY** and no write is performed.

## 7. Relationship to existing ERIA controls

This policy supplements, and does not weaken, the Pheônix rewrite-authorization contract, Sure-rarity evidence qualification, or THANKs motion-influence safeguards. Their checks remain independent. Cosmic Law does not bypass manual-trigger approval, simulation requirements, motion limits, emergency-stop checks, or the prohibition on unapproved external dispatch.

## 8. Implementation boundary

This file records a proposed policy only. It does not create credentials, assign a Faculty identity, change repository permissions, grant a runtime process write access, merge branches, or activate future capabilities. Those steps require separate implementation and explicit authorization.

## Change record

- Added as a feature-branch governance specification.
- Original source history remains intact.
