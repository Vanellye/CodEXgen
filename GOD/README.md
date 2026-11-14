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
