# ERIA Faculty Capability Governance

## Status and intent

This document defines Faculty Engine as the accountable human-governance layer for ERIA capability requests. Faculty is present throughout the capability lifecycle ("Faculty always"): proposal, permission review, execution readiness, evidence review, and closure.

Faculty is a software representation of recognized roles and delegated authority. It does not imply machine consciousness, independent legal authority, or permission to act without an accountable human principal.

## Shared contract

Every capability request MUST carry:

- a stable request identifier and originating module;
- the human principal and the recognized Faculty role responsible for review;
- the requested capability and narrowly scoped resource/destination;
- purpose, consent basis, expiry, and revocation path;
- evidence and policy version used for the decision;
- a decision state: `proposed`, `approved`, `denied`, `executed`, `failed`, or `revoked`;
- an append-only audit reference with secrets and sensitive payloads redacted.

Approval is specific to the request, scope, resource, and time window. It cannot be inherited by another request, broadened by a downstream module, or treated as approval for a different capability.

## Faculty checkpoints

1. **Intent:** record the human request and its stated purpose.
2. **Authority:** verify that the reviewer role has delegated authority for this capability and scope.
3. **Permission:** evaluate least privilege, consent, policy, and expiry.
4. **Readiness:** verify safety controls and preconditions before an adapter is invoked.
5. **Evidence:** record the outcome without storing credentials or unnecessary sensitive data.
6. **Closure:** revoke temporary grants and preserve a reviewable decision record.

No module may self-assign Faculty authority, approve its own request, or silently escalate its permissions. Where independent review is required, the proposer and approver must be distinct authorized principals.

## Capability-specific controls

### Credentials

Use approved secret-management APIs only. Faculty approves a narrowly scoped secret reference and operation; callers receive only the minimum required material, preferably short-lived handles or tokens. Secret values MUST NOT enter logs, evidence records, prompts, or generated artifacts. Credential extraction, harvesting, and disclosure remain denied.

### Execution

Processes must be visible and user-authorized. A request includes the executable identity, arguments or operation manifest, working boundary, resource limits, and expected effects. Faculty approval is bound to that manifest. Hidden execution, unreviewed persistence, and privilege escalation remain denied.

### External dispatch

Use authenticated, provider-supported integrations. Faculty checks destination allowlists, payload class, purpose, consent, and replay protection before dispatch. A detected trigger is not authorization to send. Unapproved or covert dispatch remains denied.

### Hardware

Use documented device APIs with operator confirmation, device identity checks, bounded commands, safety interlocks, and an accessible emergency stop. Faculty approval does not override device-level safety systems. Physical actuation remains disabled until the responsible operator confirms the specific action.

### Biological research

Support literature review, data analysis, and non-interventional computational simulations. Faculty records provenance, model assumptions, uncertainty, and review status. No biological intervention, wet-lab actuation, or automated control of biological systems is authorized by this contract.

## Fail-closed behavior

Unknown roles, missing consent, expired grants, ambiguous scope, unavailable audit recording, failed interlocks, or policy disagreement MUST deny the operation. A denial must be visible and reviewable. No retry may broaden scope or bypass the denied checkpoint.

## Relationship to existing governance

This contract supplements the shared ExecutionBoundaryGuard and create-only artifact storage policy. It does not weaken deny-by-default behavior, authorize any currently prohibited capability, change branch protection, or authorize merge, release, deployment, or external action.

## Integration sequence

- Map existing Faculty Engine roles and interfaces before replacing or duplicating them.
- Connect Root, Main, HOME, and StridePath through versioned shared contracts.
- Add adapters one at a time, each with explicit permission checks and isolated denial tests.
- Preserve provenance and reversible changes.
- Require independent human review of the exact proposed change before merge.

## Governing principle

Intelligence may propose; Faculty may verify delegated authority; evidence may qualify; accountable humans retain control over consequential action.
