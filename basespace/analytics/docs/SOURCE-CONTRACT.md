# BS-ANALYTICS Source and Provenance Contract

## Dataset admission
Each dataset retains a stable `dataset_id`, source URI or connector-native identifier, source type and publisher when known, retrieval timestamp separate from publication time, exact SHA-256 of acquired bytes (no normalization), byte length, row count, declared grain, and known coverage limitations.

A URL alone is not successful retrieval. If source bytes cannot be acquired, record `PENDING` and do not claim a fingerprint.

## Analysis admission
Every measure declares formula, unit, numerator/denominator where applicable, grain, population, time period, filters, and lineage to source records. Preserve nulls and missing coverage. Distinguish observed facts from estimates, user claims, scenarios, and illustrative fixtures.

## Integrity and revisions
Source records, evidence, revision events, and approval events are append-only in the SQLite reference schema. Corrections create successor revisions. SHA-256 verifies byte identity only; it does not establish authorship, truth, consent, or authority.

## Promotion and external writes
External mutation or promotion requires independent reviewer identity, verified signature, exact repository/branch/commit/content digest and scope, freshness and revocation checks, and explicit human confirmation. Missing or invalid evidence means DENY.

## Privacy
The browser dashboard processes a selected CSV locally and does not upload its contents. The SQL schema is a local reference schema, not a hosted database. Do not store secrets or personal data without a separate data-minimization and access-control review.
