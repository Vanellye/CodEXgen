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
