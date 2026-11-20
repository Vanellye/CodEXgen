# Intent-Based Write Authorization and Learning Curve

## Status

This document defines the ERIA/Pantheon policy for deriving a write-permission request from a person's declared intent. It is a governance specification, not an active permission grant or an implemented authorization adapter.

## Governing rule

**Intent determines the requested capability; verified scope, risk, evidence, and explicit authorization determine whether that capability may be granted.**

A statement of intent is not itself a write token. A model's confidence, inferred preference, prior success, learning score, urgency estimate, or symbolic instruction must never independently grant write access.

The system must not claim to know a person's private or subconscious intent. It may interpret only the intent explicitly declared for the current task, and it must show its interpretation for correction.

## 1. Intent classes

Every proposed operation must declare one primary intent and its target:

| Intent | Meaning | Default capability |
|---|---|---|
| OBSERVE | Read, inspect, compare, or explain across all sources the requester is already authorized to access | Read-All (read breadth only; no write, export, or access-control bypass) |
| PROPOSE | Prepare a plan, patch, or preview without applying it | No persistent write |
| LOCAL_EDIT | Change a disposable or explicitly selected working copy | Scoped sandbox write |
| PERSIST | Save a change to a named file, branch, or record | Exact-target write after confirmation |
| EXTERNAL_ACTION | Publish, transmit, deploy, merge, or affect an external service | Separate explicit approval and platform authorization |
| DESTRUCTIVE | Delete, overwrite, revoke, rewrite history, or make recovery harder | Deny by default; exceptional approval and verified recovery plan |

The intent label is descriptive, not an authority level. A harmless-looking label cannot reduce the risk of the underlying operation. **Read-All** means broad reading only within resources and data the requester is already permitted to see; it never bypasses privacy boundaries, ownership, consent, classification, or platform access controls, and it never includes mutation.

## 2. Decency and dignity constraints

All permission decisions must preserve:
- Human dignity, agency, privacy, and freedom to disagree.
- Consent of the person whose data, account, device, or work is affected.
- Source identity, provenance, and an intelligible correction history.
- Least privilege, narrow scope, reversibility, and a clear stop path.
- Equal respect for contributors; no inferred intent or learning score may override another person's rights.

No learning loop may manipulate, shame, coerce, impersonate, or silently act on a person. Private thoughts, beliefs, emotions, and spiritual meaning are not write-authority signals.

## 3. Progressive learning curve

Permission proceeds through explicit stages. Progress is evidence of task readiness, not an automatic promotion of rights.

1. **Understand — OBSERVE.** Restate the declared goal, target, constraints, and affected parties. Ask one focused clarification when a material ambiguity remains.
2. **Prepare — PROPOSE.** Produce a plan or diff. Identify files, records, side effects, uncertainties, and rollback options. Do not mutate persistent state.
3. **Practice — LOCAL_EDIT.** Where appropriate, work in a disposable sandbox or isolated branch. Keep the original intact.
4. **Review — PERSIST request.** Present the exact proposed change, target, evidence, tests, and recovery path. The authorized human reviews the actual operation, not merely its summary.
5. **Apply — scoped authorization.** Grant only the named operation on the named target, for the shortest practical duration. Re-check authorization immediately before the write.
6. **Verify — evidence.** Read back the result, run relevant tests, and compare the outcome with the declared intent. A failed or partial operation enters a safe hold; do not silently continue.
7. **Reflect — learn.** Record what worked, what failed, corrections, and unresolved disagreement. Use this to improve future explanations and proposals, not to enlarge permissions.

A person may pause, decline, appeal, or return to any earlier stage without penalty. A repeated task may reuse a reviewed plan, but not an expired or broadened permission.

## 4. Write decision contract

A write may proceed only when all applicable conditions are true:

- The user has explicitly declared the intended action.
- The target and scope are exact and visible.
- The operation is necessary for that intent and no narrower capability suffices.
- Required evidence and validations are present and independently checkable.
- The affected owner or authorized person has approved the exact operation.
- The authorization is current, unexpired, and not revoked.
- The operation has a proportionate recovery plan; irreversible actions receive exceptional review.
- The actual operation still matches the approved preview.

If any condition is missing, ambiguous, stale, or changed, deny or pause. Never infer approval from silence, previous approval, a learning score, or a general request to "propagate" or "execute."

## 5. Learning loop without privilege creep

The learning record may update:
- Intent-interpretation quality.
- Clarity of previews and explanations.
- Test coverage and verification quality.
- Reliability of rollback and recovery.
- Known failure modes and unresolved questions.

The learning record must not automatically update:
- User or contributor identity.
- Ownership of a source or branch.
- Permission scope, duration, or authority.
- Consent status.
- Trust level used as a substitute for evidence.
- The ability to bypass review, approval, or a safety gate.

Successful history can support a recommendation for a future request. It cannot silently convert Read-All into write authority, or a local write into an external or destructive right.

## 6. Audit and provenance

For each authorization decision, record where available:
- Declared intent and the user's confirmed interpretation.
- Requester, affected owner, and approving authority.
- Exact resource, operation, scope, and expiry.
- Preview or patch identity and source revision.
- Evidence references, validation results, and uncertainty.
- Decision, reason, timestamp, execution result, and recovery status.

An evidence reference is not proof of authenticity by itself. Production adapters must validate identities, approvals, and audit records using the host platform's trusted mechanisms.

Keep original source records distinct from lessons learned. Corrections create attributable successors; they do not silently rewrite provenance.

## 7. Stop conditions

Stop and return to review if the target changes, scope expands, the user changes intent, an approval expires, evidence conflicts, a test fails, recovery is unavailable, or the operation would affect an unconsenting party.

Destructive Git history changes remain governed by [Force Rewrite Protocol](FORCE-REWRITE-PROTOCOL.md). This policy does not authorize force-pushes, merges, deployments, account actions, or physical-device control.

## Implementation boundary

This document is a policy contract only. It does not grant filesystem, GitHub, network, Android, operating-system, or device permissions. Runtime enforcement requires a separately reviewed authorization adapter, tests for allow/deny/expiry/revocation/scope changes, and a human-approved integration.

**Learn from the outcome. Do not learn your way into greater authority.**
