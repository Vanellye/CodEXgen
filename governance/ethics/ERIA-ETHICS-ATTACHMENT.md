# ERIA Ethics Attachment System (E-EAS)

**Policy version:** 1.0.0  
**Enforcement mode:** Human approval required for every consequential operation  
**Default:** Deny when authorization is absent, ambiguous, expired, unverifiable, or out of scope.

## Purpose and attachment scope

This contract applies to every repository, application, service, module, workflow, integration, and runtime that adopts ERIA governance. Each component must identify the policy version it implements and preserve the source and version of every decision.

This file is a governance contract. Adding it to a repository does not itself grant credentials, change repository permissions, activate integrations, deploy software, or authorize an operation.

## Non-negotiable principles

1. **Human authority:** Only an accountable human with the required authority may approve a consequential operation. Software cannot approve itself, infer approval, or elevate its own permissions.
2. **Purpose and consent:** Respect human purpose, consent, autonomy, privacy, and applicable law.
3. **Least privilege:** Scope authorization to one actor, operation, target, and time window. Read permission never implies write, dispatch, deployment, or actuation permission.
4. **Evidence and uncertainty:** Distinguish verified facts, reproducible findings, heuristics, hypotheses, and unknowns. Preserve evidence and confidence.
5. **Provenance:** Preserve source repository, commit, artifact hashes, policy version, decision history, and transformation lineage.
6. **Reversibility:** Prefer isolated branches and recoverable changes. Destructive or irreversible operations require explicit, separate approval and a verified recovery plan.
7. **No covert execution:** Triggers, webhooks, schedules, passing tests, quality scores, or eligibility results never independently authorize execution, publication, external dispatch, or physical actuation.
8. **Accountability:** Record requests, decisions, reviewers, evidence, validation, execution outcome, and disposition.

## Required decision lifecycle

`PROPOSED -> VALIDATED -> ELIGIBLE -> HUMAN_APPROVED -> EXECUTED -> AUDITED`

These states are distinct:

- **Validated:** Policy and technical checks completed; no permission is implied.
- **Eligible:** The proposal meets stated criteria; no permission is implied.
- **Human approved:** An authorized person approved the exact operation, target, scope, and validity period.
- **Executed:** The exact approved operation was carried out by a separately authorized execution mechanism.
- **Audited:** Evidence and outcome were recorded.

Any changed target, payload, scope, operation, or material risk invalidates the approval and requires a new review. Denial, timeout, missing evidence, or verification failure means **BLOCKED**.

## Approval requirements

A valid approval must be explicit, attributable, scoped, time-bounded, and verifiable. It must identify:

- unique request ID;
- requesting actor and accountable approving actor;
- repository/application and immutable commit or artifact digest;
- exact operation, target, and permitted scope;
- rationale, evidence, risks, and uncertainty;
- policy version and validation results;
- approval timestamp and expiry;
- recovery/rollback plan where applicable.

The requester cannot satisfy an independent-review requirement by self-approval. Approval of a pull request is not automatically approval to deploy, transmit data, change permissions, or activate hardware.

## Audit and retention

Keep append-only, tamper-evident records. Hash-chain or sign records where the implementation supports it. Never silently rewrite or delete prior decisions; corrections must be new linked records. Minimize personal data and never place secrets, tokens, or credentials in audit records.

The repository's protected-environment review history and workflow run are supporting evidence. The workflow in this repository records a review checkpoint; it does not execute the requested operation or claim that a specific reviewer identity is contained in the generated artifact.

## Integration contract

Every adopting component must:
1. declare its policy version and responsible owner;
2. submit consequential operations as structured requests;
3. deny by default unless a matching, unexpired human approval is independently verified;
4. bind approval to the exact request digest and immutable target;
5. prevent reuse, replay, scope expansion, and approval after expiry;
6. emit an audit record for allow, deny, error, and cancellation;
7. expose no bypass path through alternate triggers, background jobs, webhooks, or privileged modules.

## Explicitly out of scope

This policy does not authorize autonomous filesystem mutation, credential access, production deployment, external dispatch, biological or medical intervention, or physical/hardware actuation. Each requires a separate, explicit authorization and appropriate safety review.

## Related repository policy

Where present, the repository's existing code-ethics and rehabilitation documents remain in force. This attachment supplements rather than silently replaces them.
