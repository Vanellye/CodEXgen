# ERIA–NaDa Governance Contract

Status: proposed architecture contract; implementation and CI enforcement must be verified separately.
Scope: branch communication, contribution evaluation, and protected integration into `main`.

## Governing invariants

1. A branch retains its identity, ancestry, and provenance. Similarity or resonance never implies ownership or permission.
2. No branch, tag, signature, automated agent, CI workflow, or promotion process may independently authorize adoption into `main`.
3. Unknown or incomplete evidence is reported as unknown. It is never silently converted into compatibility, trust, or approval.
4. Validation is read-only until a human-authorized, reviewable integration action is taken.
5. Integration must be recoverable without rewriting or erasing the source branch's history.

## Gate 1 — Resonance-based compatibility checks

Compare candidate and target at pinned commit SHAs. Evaluate, at minimum:

- ancestry and divergence;
- public interfaces, schemas, and protocol versions;
- dependency declarations, lockfiles, toolchains, and runtime requirements;
- tests, build workflows, and generated-artifact contracts;
- permissions, capabilities, data handling, and security boundaries;
- provenance, licenses, and declared contribution origin.

Produce a structured compatibility report with evidence references and per-dimension states: `compatible`, `incompatible`, `review_required`, or `unknown`.

Lexical similarity, matching declarations, or a numeric resonance score are advisory signals only. They do not prove semantic compatibility. Any missing, truncated, stale, or unpinned evidence must produce `unknown` or `review_required`, never a pass.

## Gate 2 — Secure, authenticated branch communication

- Use authenticated transport with certificate validation; never disable TLS verification.
- Use short-lived, least-privilege credentials where supported. Keep secrets out of source, logs, reports, and artifacts.
- Bind every request and response to repository identity, branch name, exact commit SHA, protocol version, timestamp, and a unique request identifier.
- Verify signed manifests and content digests before accepting exchanged artifacts. Reject replayed, expired, malformed, or mismatched messages.
- Treat remote branch content and metadata as untrusted input. Do not execute received code during discovery or verification.
- Record authorization decisions and revocations. Recheck authorization at the moment of any privileged action.

A valid signature proves control of a signing key and integrity of signed content; it does not prove that content is safe, correct, or authorized for adoption.

## Gate 3 — Independent contribution verification

The verifier must be logically separate from the contribution producer and must inspect the exact candidate SHA.

Verify:

- source repository, branch, commit ancestry, and immutable content digests;
- signature validity, signer identity, key status, and trust policy;
- complete change inventory, including generated files, workflows, dependencies, and permissions;
- policy compliance, license/provenance evidence, and declared scope;
- test and build evidence produced by trusted workflows.

A contributor's own attestation is evidence to check, not independent verification. Missing evidence blocks approval; it is not guessed or silently repaired.

## Gate 4 — Reproducible testing

- Pin source commits, dependencies, toolchain versions, and build inputs.
- Use lockfiles and deterministic generation where available.
- Run focused tests and the required repository CI suite in a clean environment.
- Record commands, environment/toolchain versions, input SHAs, test outcomes, and artifact hashes.
- Compare generated artifacts and build outputs where reproducibility is supported.
- Distinguish a successful test run from tests not run, skipped, flaky, or unavailable.

A passing result applies only to the exact tested commit SHA. If the branch moves, the evidence is stale and verification must run again.

## Gate 5 — Human-authorized adoption

Adoption requires all of the following:

1. A complete compatibility and provenance report.
2. Successful independent verification.
3. Required reproducible tests passing on the exact candidate SHA.
4. A human reviewer with repository permission explicitly approving the proposed change.
5. A reviewable pull request and protected-branch checks.

No automatic tag promotion, resonance score, signature, agent, or CI job may merge, approve, or write directly to protected `main`. Use the repository's normal review and branch-protection controls. Approval applies only to the reviewed diff and SHA; material changes invalidate it.

## Gate 6 — Reversible integration and recovery

Before adoption, record the target SHA, candidate SHA, review reference, verification report, and resulting artifact hashes.

- Prefer normal merge commits or reviewed squash/rebase operations according to repository policy; do not rewrite protected branch history.
- Preserve source branches and their commit ancestry.
- For recovery, prefer a reviewed revert commit that restores the prior behavior while preserving the audit trail.
- Document data/schema migration rollback separately; a code revert alone may not reverse external state.
- Keep recovery instructions, required permissions, expected effects, and verification steps with the change record.
- Never use force-push to recover or repair protected `main`.

A recovery point is not a guarantee that every external side effect is reversible. State explicitly what can and cannot be restored.

## Adoption state machine

```text
DISCOVERED
  -> PINNED
  -> COMPATIBILITY_REPORTED
  -> AUTHENTICATED
  -> INDEPENDENTLY_VERIFIED
  -> REPRODUCIBLY_TESTED
  -> HUMAN_APPROVED
  -> MERGED_THROUGH_PROTECTED_REVIEW
  -> POST_MERGE_VERIFIED

Any failed or missing gate -> BLOCKED / REVIEW_REQUIRED
Any post-merge regression -> RECOVERY_REVIEW -> REVERT (human-authorized)
```

No transition may skip a gate. A state transition records the actor, timestamp, exact SHAs, evidence, and decision.

## Acceptance criteria

- [ ] Reports are bound to immutable source and target SHAs.
- [ ] Incomplete evidence produces an explicit unknown/review-required result.
- [ ] Authentication, signature, replay, and authorization failures fail closed.
- [ ] Verification runs independently of the contribution producer.
- [ ] Reproducible test evidence identifies exact inputs and toolchain.
- [ ] No automation can approve or merge its own contribution or bypass branch protection.
- [ ] Human approval is recorded against the exact reviewed diff.
- [ ] Recovery uses auditable revert procedures and includes data-state limitations.
- [ ] Tests demonstrate that each gate blocks adoption when its requirement is absent.

## Implementation boundary

This document specifies required behavior; it does not claim that all six gates are implemented or enforced by the current application or CI. Each implementation must be added in a separately reviewable change with focused tests. Until enforcement is demonstrated, treat the contract as a design requirement, not a security guarantee.

The contract is conceptual and software-governance focused. The term resonance describes measured architectural compatibility; it does not assert physical, biological, or electromagnetic effects.
