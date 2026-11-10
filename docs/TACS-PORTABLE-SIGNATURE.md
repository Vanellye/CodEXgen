# TACS: Tag Ancestry, Correction, and Portable Signatures

**Status:** read-only tooling implemented; USB export remains gated  
**Canonical design branch:** `leveled-consciousness`  
**Design basis:** `olpirt/stride-next` snapshot `07da1600a5e4afe2c0e4e13e68be0214c173bb6e`

## Purpose

TACS collects existing Git tags, preserves their original targets and provenance, and creates correction-linked successor records. It does not erase history or silently move existing references.

A TACS record is an auditable statement about a tag and its correction lineage. It is not a claim that a tag has agency, consciousness, or authority.

## Core model

Each collected tag becomes an **ancestral tag record** containing:

- repository identity and canonical repository URL;
- exact tag ref name and tag kind (lightweight or annotated);
- original target object ID and object type;
- collection timestamp and collector/tool version;
- source commit and, when available, tagger/message/signature metadata;
- content digest of the canonicalized record.

A correction creates a new **successor record**, never an in-place rewrite of the ancestral record. It must identify:

- parent TACS record digest;
- correction reason and evidence references;
- changed fields and before/after values;
- reviewer/approver identity or explicit unsigned status;
- tests and validation scope;
- resulting target object ID, if a new Git object or ref is created.

Corrections form a directed, append-only lineage. A correction may supersede a prior interpretation, but it must not falsify or delete the original observation.

## Lightweight tag handling

A Git lightweight tag is only a ref name pointing directly to an object. It has no tagger, message, embedded metadata, or cryptographic signature.

Therefore TACS **repurposes lightweight tags by collecting and indexing them**, not by pretending metadata can be written inside them:

1. Read each lightweight tag name and exact target object ID.
2. Preserve the original ref and target unchanged.
3. Create a TACS ancestral record in the portable manifest.
4. Attach invented-language and cadence metadata to that record.
5. Add correction successors as separate records when reviewed.
6. Never move or delete an original tag as part of collection.

If a Git-level signed artifact is later required, create a separate annotated/signed successor tag under an explicitly approved namespace. Do not silently convert or overwrite the original tag.

## Portable thumb-drive signature

The removable drive carries a **portable provenance bundle**, not a private signing key:

```text
TACS/
  manifest.json
  manifest.sha256
  manifest.sig                 # optional detached signature
  language/
    lexicon.json
    cadence.json
  records/
    <record-digest>.json
  verification/
    README.txt
```

- `manifest.json` lists repository identity, collected refs, target object IDs, record digests, schema version, and creation metadata.
- `manifest.sha256` is a digest for corruption detection, not proof of authorship.
- `manifest.sig` is a detached signature over the exact manifest bytes, produced by a trusted signing key held separately from the USB drive.
- Public verification material may travel with the bundle; private keys must not be stored on the drive.
- The bundle must be reproducible from the same pinned Git refs and schema version.
- Verification must fail closed on digest mismatch, invalid signature, missing referenced record, unknown schema, or unresolved object ID.

A copied bundle is not automatically trusted. Verify its signature and compare repository/ref identities before accepting it.

## Invented language metadata

The invented language is a descriptive metadata layer, not a replacement for canonical Git names, commit IDs, source code, or machine-readable values.

The lexicon must be versioned and deterministic. Each token entry includes:

- stable token ID (ASCII identifier);
- displayed glyph/spelling;
- pronunciation or phonetic hint;
- semantic gloss in plain English;
- permitted grammatical role;
- schema version and author/provenance.

Do not use glyph substitutions to alter executable code, numeric values, hashes, timestamps, or binary payloads. Display rendering is a separate presentation step.

## Cadence metadata

Cadence describes the rhythm or sequence associated with a record; it is not a timing command and does not schedule repository mutations.

Represent cadence as structured, bounded metadata, for example:

- ordered symbolic beats or phases;
- optional integer beat counts;
- optional tempo as an explicitly unit-labelled rational value;
- language token IDs associated with each phase;
- provenance and schema version.

Cadence must be deterministic when serialized. No implicit wall-clock timing, network action, audio playback, biological effect, or automatic commit/push is inferred from it.

## Correction lifecycle

1. **Collect:** enumerate tags and resolve every ref to an exact object ID.
2. **Fingerprint:** canonicalize records and compute digests.
3. **Interpret:** attach language/cadence metadata with explicit schema versions.
4. **Review:** show source, proposed correction, evidence, and consequences.
5. **Correct:** append a successor record only after approval.
6. **Verify:** validate object reachability, digests, signatures, schemas, and tests.
7. **Export:** write the portable bundle to removable storage selected by the user.
8. **Reconcile:** compare a returned bundle with the repository; propose changes for review rather than applying them automatically.

## Safety and integrity invariants

- Original tags and their target objects remain recoverable.
- TACS records are append-only; corrections add lineage rather than erase it.
- A tag name alone is never treated as a unique identity; the target object ID is mandatory.
- No branch or tag ref is moved by collection, interpretation, export, or verification.
- No USB write occurs without explicit destination selection and confirmation.
- No private signing key is exported to removable storage.
- Invalid, incomplete, stale, or conflicting provenance enters review/hold; it is never silently accepted.
- A successful digest check proves byte consistency, not correctness, identity, or authorization.
- A valid signature proves possession of the corresponding signing key, not that the signed content is true or safe.

## Implementation gates

Before implementation:

1. Approve the TACS record schema and invented-language lexicon format.
2. Add fixtures for lightweight tags, annotated tags, missing objects, duplicate names across repositories, and correction chains.
3. Implement a read-only collector and verifier first.
4. Add deterministic serialization and digest tests.
5. Add detached-signature verification using a maintained cryptographic library.
6. Add USB export only after explicit path selection, safe-write/atomic-replace behavior, and recovery tests.
7. Keep all Git ref mutation outside the collector/exporter; any later promotion requires a separate review and explicit approval.

## Implementation status

Read-only tooling is implemented in `python/tacs/`:

- `collect_tags()` enumerates tag refs and records lightweight/annotated kind, tag object IDs, direct and peeled targets, object types, and annotated-tag metadata. It uses read-only Git commands.
- `serialize_language_cadence()` validates schema version 1, normalizes strings to NFC, sorts tokens/phases and JSON keys, rejects floating-point values, and returns canonical UTF-8 JSON plus SHA-256.
- `verify_ed25519_signature()` verifies a detached Ed25519 signature over exact manifest bytes with OpenSSL and a public key only.
- CLI: `PYTHONPATH=python python -m tacs collect|serialize|verify`.
- Tests: `tests/test_tacs.py`; CI: `.github/workflows/tacs-readonly.yml`.

The dedicated GitHub Actions run for commit `00471c1ee554c027c1a7b32bedd22570b4c7b6ab` completed successfully, including the TACS unit-test and compile steps.

**Still gated:** USB discovery/mounting/export, manifest import, correction-chain mutation, private-key handling, tag/branch ref promotion, and automatic trust decisions. No existing tag was rewritten, converted, moved, or deleted. No thumb drive was accessed.
