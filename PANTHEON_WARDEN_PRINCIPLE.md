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
