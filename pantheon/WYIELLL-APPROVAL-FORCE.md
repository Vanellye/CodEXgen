# WYIELLL — Approval Force and Open Potential

## Status

This document defines a proposed ERIA/Pantheon governance contract. It is not a runtime authorization adapter, credential, permission grant, or execution mechanism.

## Governing phrase

**“Do What You Wyielll”** expresses a declared purpose to move work toward its stated outcome. It does not override source ownership, consent, access controls, review, or platform authorization.

The phrase is an instruction to prepare and evaluate a proposal—not a bearer token and not proof that a particular person approved a particular write.

## Open potential

The user's imagery of nerves and pluripotent cells is represented only as a software-design metaphor:

- Preserve multiple candidate paths while evidence is incomplete.
- Keep source identity and prior states intact as alternatives are explored.
- Distinguish observed signals, hypotheses, and verified findings.
- Select or specialize a path only after review against the declared purpose and constraints.
- Do not infer biological transformation, neural access, or cellular effects from software behavior.

No candidate path owns the source from which it was derived. A new result is an attributable successor, not a silent replacement.

## Approval Force

Approval Force is the requirement that a consequential operation be backed by a current, explicit, scope-bound human authorization.

An approval record must identify, at minimum:

- the approving person and the authority by which they may approve;
- the exact repository, resource, or record;
- the exact operation and intended outcome;
- the reviewed patch, plan, or content identity;
- affected owners or parties and their required consent;
- evidence, tests, uncertainty, and known risks;
- the approval time, expiry, and revocation mechanism;
- the recovery or rollback path.

A text phrase, symbolic marker, inferred intention, previous approval, confidence score, or successful prior action is not an authenticated approval record.

## Decision sequence

1. **Receive** the declared purpose without changing the source.
2. **Interpret** the request and expose ambiguities for correction.
3. **Prepare** a bounded proposal or patch.
4. **Inspect** provenance, dependencies, scope, evidence, and risks.
5. **Review** the exact proposed operation with the authorized human.
6. **Authorize** only the exact reviewed operation using the host platform's trusted identity and permission mechanisms.
7. **Apply** only if authorization is current and all policy checks pass.
8. **Verify** the resulting state and record the outcome.
9. **Recover or hold** if scope changes, approval is absent or revoked, validation fails, or the result differs from the approved proposal.

Any mismatch returns the operation to review. No step may silently escalate its own authority.

## Fail-closed rule

If the system cannot authenticate the approver, establish ownership, verify scope, or confirm that the applied operation matches the reviewed proposal, it must stop without writing.

Approval Force never authorizes force-push, branch deletion, history rewriting, merging, deployment, publication, physical actuation, or access to another person's data by implication. Those actions retain their separate approval and platform controls.

## Relationship to existing policy

This document supplements [Intent-Based Write Authorization](INTENT-WRITE-AUTHORIZATION.md), [Branch Protection Code Ethic](above/BRANCH-PROTECTION-CODE-ETHIC.md), and [Force Rewrite Protocol](FORCE-REWRITE-PROTOCOL.md). Where rules overlap, the stricter control applies.

**Purpose can direct the proposal. Evidence can justify it. Only verified, scoped human authorization can permit the consequential change.**
