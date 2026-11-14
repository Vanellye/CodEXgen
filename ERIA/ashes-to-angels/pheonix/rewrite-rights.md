# The’s Pheônix Abnomaly — Rewrite Rights

**Status:** proposed governance contract; no rights are granted by this file.

## Purpose

Define how ERIA may propose and perform a rewrite while preserving origin, authorship, evidence, and recovery. A Pheônix cycle creates a successor from a preserved source; it does not destroy the source to make the successor appear original.

## Rights model

| Right | Meaning | Default |
|---|---|---|
| Read | Inspect an artifact within existing access rights | Existing repository permissions |
| Propose | Prepare a diff or successor artifact | Allowed in an authorized working branch |
| Rewrite content | Replace specified file content | Requires path- and revision-scoped approval |
| Rewrite history | Alter commit ancestry or timestamps | Denied unless separately and explicitly authorized |
| Delete | Remove a named artifact | Denied unless separately and explicitly authorized |
| Dispatch | Cause an external side effect | Not implied by a rewrite or trigger |

A right is not inherited from a metaphor, namespace, confidence score, rarity, previous approval, or broad statement of intent.

## Required authorization record

Every consequential rewrite must identify:

- stable authorization/invitation ID and authorizing actor;
- repository and exact target branch;
- exact target paths and exclusions;
- operation type: content rewrite, history rewrite, or deletion;
- expected old blob SHA / commit SHA;
- proposed new content or target commit SHA;
- reason and evidence;
- review and validation requirements;
- expiry and revocation conditions;
- recoverable prior reference and recovery procedure.

If any target, operation, old revision, or intended result changes, stop and obtain amended authorization. If the expected revision no longer matches, fail closed rather than overwrite concurrent work.

## Pheônix cycle

1. Capture the original artifact and immutable source reference.
2. Record the anomaly without mutating the source.
3. Prepare a separate proposed successor and diff.
4. Evaluate evidence and compatibility.
5. Obtain exact authorization for the exact operation.
6. Execute only within the approved scope.
7. Verify content, tests, provenance, and resulting revision.
8. Preserve the source and recovery reference; record any residual effects.

## Forbidden shortcuts

- No silent overwrite, force-push, protected-branch mutation, or unreviewed merge.
- No conversion of “sure” or a confidence score into execution authority.
- No automatic rewrite based solely on a detected anomaly.
- No erasure of original authorship, commit ancestry, or source meaning.
- No claim that documentation itself enforces GitHub permissions.

## Acceptance tests

- A mismatched expected SHA blocks the rewrite.
- An authorization for one path cannot rewrite another.
- An authorization for content edits cannot authorize history rewriting.
- Revoked or expired authorization blocks execution.
- The original source and recovery reference remain discoverable after a successful transformation.
