# Planting Seeds Ethics — Pantheon injection policy

## Meaning

A "seed" is any proposed code, generated module, configuration, dependency, prompt, data transformation, or runtime instruction introduced into an ERIA target. "Planting" means staging that proposal for evaluation; it does not mean silently executing or deploying it.

## Required sequence

1. **Identify** — assign a stable seed ID and state its intent.
2. **Trace** — record source repository, branch, commit, author/actor, source hash, and any transformations.
3. **Declare** — name the target, exact requested scope, expected effects, dependencies, and compatibility evidence.
4. **Protect** — verify consent, security, safety, ownership, privacy, and least-privilege constraints.
5. **Review** — obtain an independently verifiable human approval for the exact target and scope.
6. **Stage** — prepare an isolated, reversible patch; preserve the original.
7. **Validate** — run relevant tests and integrity checks; record failures and uncertainty.
8. **Decide** — keep on HOLD, reject, or mark PROPOSAL_ONLY for human review. Integration requires a separate explicit authorization.
9. **Recover** — document rollback and verify restoration if an approved integration is later reversed.
10. **Audit** — append the decision, evidence, reviewer reference, commit, and result to the audit record.

## Non-negotiable gates

- Missing or mismatched scope, consent, provenance, ownership, security, safety, compatibility, or approval means HOLD.
- A successful parser, test, scanner, model, or workflow is not authorization.
- No injected seed may self-approve, expand its permissions, change its own gate, or authorize a subsequent seed.
- No automatic write to protected branches, release, deployment, external transmission, file-system-wide mutation, or physical actuation.
- Verification flags supplied by a caller are claims to be authenticated upstream; they are not cryptographic proof.
- Preserve source and history. Prefer a separate branch and a minimal patch.

## Pantheon implementation boundary

The current Pantheon I-INJECT C99 contract checks required references, exact scope equality, and consent/security/safety/ownership/approval/compatibility assertions. It returns `PROPOSAL_ONLY` and performs no mutation or execution. This policy documents the ethical lifecycle; it does not pretend that the existing contract is a complete language runtime or cryptographic identity system.

## Audit record fields

`seed_id`, `intent`, `source_reference`, `source_sha256`, `provenance_reference`, `target`, `target_revision`, `requested_scope`, `authorized_scope`, `compatibility_reference`, `consent_evidence`, `security_evidence`, `safety_evidence`, `ownership_evidence`, `approval_reference`, `validation_results`, `rollback_reference`, `decision`, `reviewer`, and timestamps.

This is a policy and review contract, not permission to execute an injection.
