# PONS Universal Status and Provenance Integration

**Implementation branch:** `integration/pons-provenance`  
**Canonical anchor branch:** `zero-dissipation-anchor` (read-only reference)  
**Anchor identifier:** `7f7a43a973a96a06dd432bf94843213d09133323`  
**Anchor branch head at integration start:** `df5ead3b55cfabd0ba40e902b4080946cba794dc`

## Non-negotiable boundary

PONS treats the canonical anchor identity and its pinned branch-head reference as immutable inputs. This integration branch is additive and descends from the recorded anchor branch head. No commit, file, ref, tag, or history operation is made against `zero-dissipation-anchor`.

The GitHub API reported branch protection disabled at integration start. Immutability is therefore enforced procedurally in this work; repository administrators should enable branch protection and restrict direct updates independently.

## Shared contract

Every component adapter must provide:
- a stable component identifier;
- exact source path and source commit/ref;
- a PONS status observation (`READY`, `DEGRADED`, `HOLD`, or `UNKNOWN`);
- source bytes or a retrievable source object for digest verification;
- an expected SHA-256 from a separately reviewed, pinned manifest.

PONS computes the digest itself. Components cannot submit an `ACCURATE` state. Operational status is a component observation; provenance is a separate PONS result. Missing evidence remains `UNKNOWN`; mismatches become `HOLD`.

## Current adapter coverage

The canonical anchor branch inventory at the recorded head contains the following relevant code areas:
- Android UI: `app/src/main/java/com/vanellye/codexgen/`
- Git Freedom bridge: `GitFreedomBridge.kt`
- generated modules: `generated_modules/`
- Python services: `python/`
- hypothetical research: `hypotheticals/`

The branch does not contain the later Termux conversation engine, a verified music engine, or independently identifiable Stride/Pantheon runtime modules. Those must be registered only after their exact source refs and expected digests are supplied or discovered on their own branches. This branch therefore supplies the common PONS authority and adapter contract; it does not falsely claim every runtime is already connected.

## Ledger semantics and limitations

The JSONL event ledger is append-only through this API and hash-chained. Startup verifies sequence, previous-hash linkage, event hashes, and anchor identity. A hash chain detects accidental or unsophisticated edits; it is not tamper-proof storage, an external signature, a trusted timestamp, or authenticated reviewer identity. Protect the ledger with filesystem permissions, backups, and independent signed checkpoints.

Expected digests must be supplied by a separately reviewed manifest. This first implementation does not authenticate the manifest or reviewer. It therefore reports digest matches, not signer trust or factual accuracy. Do not use component self-registration as a trust decision.

## Integration protocol

1. Register each component from a reviewed manifest, never from an untrusted self-asserted digest.
2. Capture component operational status independently from provenance checks.
3. Retrieve exact source bytes and let PONS compute SHA-256.
4. Record missing source/digest as `UNKNOWN`; mismatch as `HOLD`.
5. Preserve raw observations and append corrections as new events.
6. Do not automatically execute, rewrite, deploy, push, merge, or promote a component because its provenance matches.
7. Add per-runtime adapters only after source paths, versions, and tests are verified.

## Test command

```bash
python -m unittest discover -s tests -v
```

Tests cover frozen anchor identity, rejection of anchor substitution, digest matching and mismatch, missing evidence, prohibition on self-declared accuracy, hash-chain tamper detection, and anchor identity in status reports.
