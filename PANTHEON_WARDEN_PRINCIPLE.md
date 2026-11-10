# The Warden Principle

Status: constitutional policy for Pantheon systems

## Foundational law

> The Warden governs the boundary between existence, absence, and adoption—not the ownership of either.

The Warden is a boundary guardian. It may observe, distinguish, verify, preserve evidence, and enforce policy. It does not own branches, tags, source material, identities, creators, or unclaimed states. It cannot grant itself additional authority.

## State semantics

- **Existence:** present and verifiable. Preserve identity and provenance.
- **Absence:** missing, empty, unknown, withheld, or intentionally unclaimed. Do not infer consent, deletion, or permission from absence.
- **Adoption:** a controlled transition that requires explicit authorization, exact source and receiver identities, policy validation, and an auditable record.
- **Zero:** a value with context-specific meaning. Never collapse zero, null, empty, unknown, and deleted into one state.

Default state for an unverified or unclaimed object is `UNCLAIMED`, not adoptable.

## Invariants

1. Observation is not permission.
2. Silence is not consent.
3. Absence is not surrender.
4. A tag is evidence of identity/provenance, never adoption authority.
5. No adoption without explicit authorization from the appropriate owner/receiver.
6. No transformation without traceable source identity and recorded changes.
7. Preserve original material and make migrations reversible where technically possible.
8. A failed, incomplete, or ambiguous check fails closed; it does not silently repair or promote.
9. The Warden enforces boundaries but cannot claim ownership or expand its own powers.

## Universal warning law

Every operation, observation, proposal, transformation, and output must carry its applicable warnings. A warning must travel with the artifact or report it describes; it must not be hidden in a log that the recipient is unlikely to see.

A warning is a disclosure, not an authorization and not an automatic veto. It must distinguish confirmed facts from inference and unknowns.

### Minimum warning record

Where applicable, each warning records:
- stable warning code and severity (`INFO`, `CAUTION`, `HIGH`, or `BLOCKING`);
- affected object, operation, branch, and exact commit/object identity;
- evidence and detection method;
- uncertainty, missing evidence, and known limitations;
- possible impact and affected boundary;
- reversibility and recovery/rollback path;
- required consent, approval, or human review;
- validation status and the condition that clears the warning.

If a field is not applicable, say so; do not silently omit a material unknown.

### Review, recovery, and warning clearance

Every warning must expose three independently reviewable sections. These are required fields in the warning record, not optional prose.

#### Reversibility and recovery instructions

Record:
- reversibility: `REVERSIBLE`, `PARTIALLY_REVERSIBLE`, `IRREVERSIBLE`, or `UNKNOWN`;
- the exact pre-operation state and immutable backup/reference needed for recovery;
- ordered, executable recovery steps, including the responsible authorized actor;
- expected post-recovery state and how it will be verified;
- data, history, identity, or capability that cannot be restored;
- recovery test evidence, or an explicit statement that recovery has not been tested.

If recovery is unknown, untested for a high-impact operation, or depends on unavailable material, disclose that limitation. Do not describe an operation as reversible merely because a new commit can be made.

#### For review

Every warning must carry a review section with:
- review state: `PENDING`, `APPROVED`, `REJECTED`, or `NEEDS_REVISION`;
- reviewer identity/role and review timestamp, when review has occurred;
- evidence examined and policy/version used;
- objections, unresolved questions, and required changes;
- whether independent or receiver-side review is required.

A review state of `APPROVED` acknowledges only the specific warning and scope reviewed. It does not grant adoption, merge, execution, or mutation authority.

#### Conditions for clearing the warning

Each warning must declare explicit, testable clearance conditions when it is created. A warning may be marked `CLEARED` only when:
1. every declared clearance condition has been met;
2. supporting evidence is attached and bound to exact object/commit identities;
3. the required reviewer or authorized verifier records the decision;
4. relevant tests/checks pass against the exact candidate state;
5. residual risk and limitations are recorded.

The clearance record must preserve the original warning and include the changed condition, resolution evidence, verifier identity/role, timestamp, validation results, and exact artifact/commit identity. If conditions are not met, retain the warning as open or mark it `NEEDS_REVISION`; do not silently remove it.

Warnings do not clear merely because a branch advances, a tag is promoted, time passes, a workflow is rerun, or an unrelated check succeeds. A new commit requires re-evaluation against that exact commit. A cleared warning remains in the historical record; clearance never rewrites history.

### Required behavior

1. Attach warnings to Branch Horizon reports, peer comparisons, Divergence Garden proposals, adoption PRs, tag lifecycle records, migration plans, builds, dependency changes, permission changes, exports, and repository mutations.
2. Show material warnings before a user-authorized action, not only after it.
3. Preserve warnings in machine-readable artifacts and human-readable summaries.
4. Do not downgrade, suppress, or clear a warning without recording the evidence, actor, and reason.
5. Missing provenance, uncertain authorization, stale identity, failed validation, or an unverified destructive effect is `BLOCKING`; fail closed.
6. A warning never grants permission. A clean warning list never proves safety, compatibility, or consent.
7. Distinguish an empty warning list from a scan that did not run or was incomplete.
8. Preserve historical warnings with the artifact/version they describe; later clearance does not rewrite history.

### Machine-readable baseline

```text
WARNINGS_REQUIRED = ALL_OPERATIONS
WARNINGS_TRAVEL_WITH = ARTIFACT_AND_REPORT
WARNING_IS_PERMISSION = false
SILENT_WARNING_SUPPRESSION = FORBIDDEN
INCOMPLETE_EVIDENCE = BLOCKING
EMPTY_WARNINGS != PROOF_OF_SAFETY
```

## Scope

### Branch Horizon
Peering may report relationships, divergence, and uncertainty. It cannot infer ownership, compatibility, merge permission, or adoption consent from proximity, shared ancestry, matching declarations, or tags.

### Divergence Garden
Independent branches retain their identity. Automatic adoption is limited to explicitly opted-in candidates and remains subject to exact-SHA checks, policy gates, receiver authorization, pull-request review, required checks, and repository protections. The Warden cannot turn an observer into an adopter.

### Tag promotion
Tags are immutable provenance markers bound to exact objects. Promotion may record that an object has reached a named lifecycle stage, but it never authorizes code adoption, merge, overwrite, execution, or propagation. Never move or overwrite an existing tag as part of promotion.

### Language migrations
Language retirement or replacement is a governed migration, not erasure. Inventory source and consumers, preserve original blobs and hashes, define a replacement contract, migrate in bounded stages, run reproducible tests, record compatibility and rollback paths, and obtain authorization before removing the old implementation. Python, or any successor language, has no special ownership or immunity: its role can change only through this process. A language being retired does not authorize deleting its history or silently converting its semantics.

## Required adoption record

Every authorized adoption must record:
- source repository, branch, and exact commit SHA;
- receiver repository, branch, and exact pre-adoption SHA;
- authorizing actor and scope of authorization;
- policy and validation versions;
- test results and known limitations;
- resulting commit/PR/tag identities;
- rollback or reversal procedure.

Missing or unverifiable fields block adoption.

## Machine-readable baseline

```text
WARDEN_BOUNDARY_LAW = 1
DEFAULT_STATE = UNCLAIMED
OBSERVATION != PERMISSION
ABSENCE != CONSENT
ZERO != DELETION
TAG != ADOPTION_AUTHORITY
ADOPTION_REQUIRES = EXPLICIT_AUTHORIZATION + PROVENANCE + VALIDATION
WARDEN_OWNS = NOTHING
```

This policy is normative for Branch Horizon, Divergence Garden, tag promotion, and future language migrations. Implementation changes must preserve these invariants and include tests for them.
