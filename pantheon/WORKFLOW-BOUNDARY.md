# Pantheon Boundary — Above and Below Workflows

## Architectural separation

CodEXgen has three distinct workflow zones. They exchange explicit records; they are not one unrestricted chain.

```text
ABOVE PANTHEON
Human purpose / JOB
    -> evidence and provenance
    -> principles and consent
    -> proposal
          |
          v
PANTHEON BOUNDARY
    validate contract
    -> apply Rise / Fall / Warden policy
    -> verify authorization and safety
    -> issue scoped decision
          |
          v
BELOW PANTHEON
    authorized gateway selection
    -> module / adapter execution
    -> result and side-effect record
          |
          +------> evidence returned ABOVE for review
```

## Above: preparation and governance

The above workflow answers: **What is being proposed, why, by whom, with what evidence, and under whose authority?** It prepares the JOB, preserves the contributor's purpose, distinguishes evidence from interpretation, and obtains specific authorization.

See [Above Pantheon](above/README.md) and [Universal Workflow — JOBs](../docs/UNIVERSAL-WORKFLOW-JOBS.md).

## Pantheon: decision boundary

Pantheon is the boundary, not the owner of the purpose. It validates required fields, checks policy conditions, and emits one of three symbolic outcomes:

- **ơ / RISE:** proposal may proceed within its approved scope.
- **ọ / FALL:** stop, retreat, or return for correction.
- **WARDEN:** pause because evidence, safety, authority, or interpretation is insufficient.

A decision is not a universal permission token. Each consequential receiver must validate the decision identifier, scope, and authorization again. A RISE state never authorizes unrelated actions.

## Below: execution and reporting

The below workflow answers: **What exact operation was authorized, what happened, and what evidence resulted?** It selects eligible gateways, executes bounded operations, records outcomes, and returns results as evidence for the above workflow.

See [Below Pantheon](below/README.md), [Gateway Origin](GATEWAY_ORIGIN.md), and [Control Authorization Standard](CONTROL_AUTHORIZATION.md).

## Search & Rescue: four independent lanes

The [Pantheon Search & Rescue workflow](search-rescue/README.md) applies the same boundary discipline to four separately governed lanes:

1. **Search** collects leads and preserves source provenance; it cannot confirm identity or dispatch.
2. **Coordination** assigns accountable roles and tasks; it cannot alter evidence or expand authority.
3. **Verification** independently assesses leads; it cannot dispatch or execute rescue.
4. **Rescue** executes only tasks authorized by the responsible human incident coordinator; it cannot rewrite evidence or override safety holds.

Every lane handoff requires an explicit, acknowledged record with sender, recipient, purpose, scope, authorization, timestamps, sensitivity, and audit reference. No lane may silently upgrade another lane's status. Missing acknowledgement, invalid scope, expired authorization, or conflicting state places the affected operation in WARDEN.

This is a design specification, not a live rescue or dispatch service. Real incidents remain under emergency services and trained human incident command. See the dedicated document for privacy, accessibility, child safeguarding, and implementation limitations.

## Separation invariants

1. Above-Pantheon components may propose; they may not directly execute protected modules.
2. Pantheon may decide within its declared policy; it may not invent human intent, consent, or evidence.
3. Below-Pantheon components may execute only the approved operation; they may not grant themselves authority.
4. FALL and WARDEN cannot be upgraded by downstream routing or a high score.
5. Results flow upward as evidence, never as silent changes to purpose or consent.
6. Keep provenance and JOB identity across both handoffs; preserve separate records for proposal, decision, and execution.
7. Human review remains available; contributors may pause, decline, correct, or appeal.
8. A failed or incomplete stage does not silently trigger the next stage.

## Implementation status

This document defines the architecture. The existing JOB lifecycle, Rise/Fall policy prototype, Gateway Router, and native runtime provide partial building blocks. The full proposal envelope, signed/scoped decision token, receiver-side authorization enforcement, durable event log, and end-to-end integration tests are not yet implemented. The Search & Rescue four-lane workflow is documentation-only; secure case storage, access enforcement, identity verification, dispatch integration, and responder authentication are not implemented. Do not describe these workflows as operational until the required controls are implemented and tested.
