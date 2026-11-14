# GOD Collaboration

This is ERIA's shared workspace for references, analysis, translations, annotations,
frequency interpretations, and other intellectual descendants of preserved sources.

## Rules
- Originals live only in ORIGINAL_DATA/objects/ and are addressed by SHA-256.
- records/<record-id>/source-reference.json points to the source record and digest.
- New work must be a new file with its own digest, author/actor, timestamp,
  transformation description, and one or more parent record IDs.
- Never edit or replace an ancestor, its metadata, or a prior lineage event.
- Collaboration content is derivative and non-authoritative until separately reviewed.
- Shared writes require an adapter-verified PONS grant scoped to the exact GOD vault.
- Conflicts create a new candidate/descendant; they never resolve by overwriting.

The initial collector creates source-reference records only. Translation, frequency
analysis, semantic indexing, and collaboration synchronization are separate stages
and must preserve the source digest and parent links.
