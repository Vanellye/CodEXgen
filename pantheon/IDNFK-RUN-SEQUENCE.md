# IDnfk Subject Handling and Run Sequence

## Identity

`IDnfk` is the exact system identifier supplied for this component. This document does not expand or reinterpret it.

## Purpose

IDnfk builds a deterministic, side-effect-free run plan for a subject under consideration. It makes room for an explicit `OTHER` classification so unfamiliar, incomplete, or unmapped subjects are not silently discarded or forced into an inaccurate category.

## Sequence

1. **DISCOVER** — require a subject ID, source, description, and requested action.
2. **CLASSIFY** — compare the declared category against the caller's recognized-category set.
3. **OTHER** — if no recognized category matches, preserve the subject and route it to inspection.
4. **INSPECT** — require further evidence when the subject is OTHER or evidence is not VERIFIED.
5. **REVIEW** — verified, recognized subjects advance to review.
6. **AUTHORIZE** — record a traceable approval reference.
7. **READY FOR EXTERNAL AUTHORIZATION CHECK** — mark the plan ready for a separate external authorization check.

## Invariants

- `OTHER` is a valid holding classification, not a trash bin, success state, or permission grant.
- Unknown and inferred evidence never advance to execution eligibility.
- A supplied approval reference is traceability metadata, not proof of identity or authentication. It cannot independently authorize execution.
- This module plans; it does not execute requested actions, mutate files, change Git refs, or bypass Pantheon control gates.
- Every plan retains the subject's source identity and requested action.
- Invalid or incomplete subjects fail closed with an explicit finding.

## SACREL temporal integrity

Conditions and classifications may evolve when new evidence arrives. Corrections must be explicit and traceable; an earlier source record is not silently rewritten. The sequence is deterministic for the same input and recognized-category set.

## Verification

The C++11 test covers recognized subjects, missing approval references, OTHER routing, inferred evidence, and invalid source identity. A passing source-level test is not claimed until the CMake build and CTest run complete.
