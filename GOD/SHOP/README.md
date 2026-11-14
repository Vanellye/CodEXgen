# SHOP — typed non-original content store

SHOP stores the immutable, content-addressed bytes for **every non-original GOD record**, regardless of its record type.

## Object layout

`SHOP/objects/<first-two-hex>/<sha256>`

The object path is derived from the exact output bytes. Existing objects are verified and reused; they are never overwritten.

## Record and lineage contract

- Original records retain their existing schema, authority marker, and `ORIGINAL_DATA/objects/` path.
- Every non-original record uses a lowercase typed identifier (1–64 characters; `a-z`, `0-9`, underscore, hyphen; `original` is reserved).
- Every SHOP record has at least one direct parent, a `derivation` manifest, and a non-empty `validated_parents` proof manifest.
- The derivation manifest records operation, method, source context (relative path, filename, source SHA-256), and creator.
- Parent ancestry, content digest, byte length, source context, and store/type pairing are revalidated before provenance is accepted.
- A new descendant never edits an original or another ancestor. Corrections are descendants, not replacements.
- `SOURCE_PROVENANCE/records/` stores metadata for both original and SHOP records; `LINEAGE/events.jsonl` is append-only.

## Authorization

Creation uses the trusted PONS `god.derive` capability with exact resolved-vault scope. Missing, mismatched, or unverified grants are held. PONS's current `PROPOSAL_ONLY` decision is the application-level grant gate; it is not an OS sandbox or cryptographic identity proof.

See [the collector and derivative API contract](../COLLECTOR.md).
