# GOD — Grand Original Data

GOD is ERIA's preservation root. It stores source originals and provenance; ERIA creates searchable, translatable, interconnected interpretations without altering originals.

## Preservation contract
- Original bytes are immutable after ingestion. Corrections and new versions are new records, never replacements.
- Each record carries a stable ID, origin/source reference, capture time, media type, byte length, SHA-256 digest, and parent/derivation links where known.
- Unknown metadata stays explicitly unknown; never guess or silently substitute values.
- PONS approval governs controlled writes, with an append-only audit record.
- Keep independent backups; a Git branch alone is not an archival backup.

## Collection pipeline
See [Collector contract](COLLECTOR.md), [record schema](RECORD.schema.json), and [Collaboration workspace](COLLABORATION/README.md).
The initial engine is `tools/god_collective.py`: PONS-gated single-file ingestion, SHA-256 content addressing, provenance metadata, lineage events, collaboration references, and integrity verification. It is a library integration point, not yet an unattended directory watcher or connected ERIA runtime service.

## Collections
ALL, EVERYTHING, NOTHING, ANYTHING, WHATEVER, IDontKnow, COULDA, SHOULDA, WOULDA, HERITAGE, ANCESTRY, LINEAGE, ORIGINAL_DATA, ROOT_WORD_INTELLECT, FREQUENCIES, SOURCE_PROVENANCE, and COLLABORATION.

These are organizing categories, not a claim that all possible information has been captured. No deployment, merge to main, or background collection is authorized by this branch.


## Parent validation and repository forge

Every new GOD ingestion with parents passes through
`tools/god_parent_validation.py`, which verifies the complete parent chain,
object digests, byte lengths, safe storage paths, and the direct-parent digest
manifest before the child provenance is accepted.

ERIA's on-demand repository representation tool is
`tools/eria_repository_forge.py`. It creates a read-only structural inventory
of the selected Git worktree; it does not execute scanned code or modify the
repository. Its design is specified in
[SOW: Autonomous Repository Interpretation and Representation Forge](SOW/AUTONOMOUS_REPOSITORY_INTERPRETATION_REPRESENTATION_FORGE.md).
The parent-validation requirements remain specified in
[SOW: Ethical Information and Parent-Record Validation](SOW/ETHICAL_INFORMATION_PARENT_RECORD_VALIDATION.md).


## Derived descendants

Translations, interpretations, and corrections are separate, append-only
records created by `tools/god_derivatives.py`. Their bytes live in
`DERIVED_DATA/objects/`; original bytes remain in
`ORIGINAL_DATA/objects/`. Each descendant names its direct parent records,
stores parent digest/size proofs, and records the exact source-relative path,
filename, and source hash used for the derivation. Corrections are descendants,
not edits to originals or prior descendants.

The creation API requires a trusted PONS `god.derive` capability grant and
revalidates ancestry immediately before writing the new provenance record.
See [the collector and derivative API contract](COLLECTOR.md).
