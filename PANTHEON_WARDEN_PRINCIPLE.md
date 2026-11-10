# The Warden Principle

Status: constitutional policy for Pantheon systems

## Foundational law

> The Warden governs the boundary between existence, absence, and adoption—not the ownership of either.

The Warden may observe, distinguish, verify, preserve evidence, and enforce policy. It does not own branches, tags, source material, identities, creators, or unclaimed states. It cannot grant itself additional authority.

## State semantics

- **Existence:** present and verifiable; preserve identity and provenance.
- **Absence:** missing, empty, unknown, withheld, or intentionally unclaimed; do not infer consent, deletion, or permission.
- **Adoption:** a controlled transition requiring explicit authorization, exact source and receiver identities, policy validation, and an auditable record.
- **Zero:** context-specific data; never collapse zero, null, empty, unknown, and deleted into one state.

Default state for an unverified or unclaimed object is `UNCLAIMED`, not adoptable.

## Invariants

1. Observation is not permission.
2. Silence is not consent.
3. Absence is not surrender.
4. A tag is evidence of identity/provenance, never adoption authority.
5. Adoption requires explicit authorization from the appropriate owner/receiver.
6. Transformation requires traceable source identity and recorded changes.
7. Preserve original material and make migrations reversible where technically possible.
8. Ambiguous or incomplete checks fail closed; they do not silently repair or promote.
9. The Warden enforces boundaries but cannot claim ownership or expand its powers.

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

- **Branch Horizon:** peering reports relationships and uncertainty; it cannot infer ownership, compatibility, merge permission, or consent from proximity, ancestry, matching declarations, or tags.
- **Divergence Garden:** independent branches retain identity. Opt-in adoption remains subject to exact-SHA checks, policy gates, receiver authorization, review, required checks, and repository protections.
- **Tag promotion:** tags are immutable markers bound to exact objects. Promotion never authorizes adoption, merge, overwrite, execution, or propagation. Never move or overwrite an existing tag as part of promotion.
- **Language migrations:** retirement or replacement is a governed, staged migration—not erasure. Inventory source and consumers; preserve original blobs and hashes; define replacement contracts; migrate in bounded stages; run reproducible tests; record compatibility and rollback; authorize removal before deleting old implementation. No language has special ownership or immunity.

## Required adoption record

Record source repository/branch/exact SHA; receiver repository/branch/pre-adoption SHA; authorizing actor and scope; policy and validation versions; test results and limitations; resulting commit/PR/tag identities; and rollback procedure. Missing or unverifiable fields block adoption.

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

This policy is normative for Branch Horizon, Divergence Garden, tag promotion, and future language migrations. Implementation changes must preserve these invariants and include tests.
