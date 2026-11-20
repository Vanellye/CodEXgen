# Pantheon NEW Module

**Role:** Consent-based, evidence-auditable introspection and narrative proposal layer.  
**State:** Staged; not wired into Pantheon runtime.

## Contract

NEW accepts only already-minimized public information or consented privacy-preserving aggregates. The caller must provide a permission basis, purpose, source identity, record identity, capture time, and provenance digest. The authorization flag is an upstream assertion; it is not cryptographic proof of consent or legal authority.

## Provenance is not proof

These concepts are deliberately separate:

- **Provenance:** where a record came from, when it was captured, its identity, and its transformation/history references.
- **Proof / supporting evidence:** the material and method used to support or corroborate a particular claim.
- **Integrity digest:** a mechanism for detecting whether referenced bytes changed; it does not establish truth, permission, completeness, or representativeness.
- **Evidence classification:** source-reported, independently corroborated, or hypothesis. A corroborated claim still remains open to challenge and correction.

NEW requires a proof reference, method, and check time before labeling a claim independently corroborated. It does not pronounce claims universally proven.

## Narrative and privacy boundaries

NEW emits a classified evidence summary, not an autonomous verdict or a finished account of people. It does not connect to sources, monitor private streams, identify or rank individuals, infer sensitive traits, publish, contact people, or initiate actions. Narrative interpretation remains a human responsibility and must be labeled as interpretation.

Do not place private communications, credentials, intimate data, or identifiable personal records into this module. Aggregate data must be privacy-preserving and appropriately consented or lawfully public. Do not use outputs to stigmatize, retaliate against, manipulate, or target people.

## Review standard

Before any downstream use, a human reviewer should verify:
1. Source authority, permission basis, scope, and intended purpose.
2. Provenance continuity and integrity of the referenced source material.
3. Whether the proof reference actually supports the exact claim being made.
4. Independence, method, date, limitations, conflicting evidence, and possible selection bias.
5. Data minimization, re-identification risk, representativeness, and privacy impact.
6. Clear separation of observation, source-reported statement, corroborated claim, hypothesis, and interpretation.
7. Corrections are additive, linked to the affected claim, and preserve the prior version.

If authorization, provenance, proof metadata for a corroborated claim, or data classification is missing or conflicting, hold the record. No inference is upgraded to fact by repetition, confidence, a hash, or narrative fluency.

## Build and test

```sh
cc -std=c99 -Wall -Wextra -Werror -Ipantheon/NEW pantheon/NEW/NEW.c pantheon/NEW/tests/test_NEW.c -o /tmp/new-test
/tmp/new-test
```

No source connector, crawler, account access, covert monitoring, or autonomous publication is included. Runtime integration requires a separately reviewed adapter, privacy and permission controls, correction-chain verification, and explicit human approval.
