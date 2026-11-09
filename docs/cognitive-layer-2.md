# CodEXgen Cognitive Layer 2 — Ever-Creation Cognitive Layer (ECCL)

**Implementation branch:** `cognitive-layer-2`  
**Foundation:** `zero-dissipation-anchor`  
**Governing anchor:** `7f7a43a973a96a06dd432bf94843213d09133323`

## Purpose

ECCL is an additive cognitive-memory layer for provenance-aware learning and temporal reconciliation. It preserves historical records, connects derived knowledge to its sources, and surfaces conflicting claims for human review.

It does not claim consciousness, determine metaphysical truth, infer that a newer claim is automatically better, or autonomously rewrite source material.

## Relationship to the committed preservation specifications

ECCL implements the Zero-Dissipation Anchor safeguards as software behavior:

- **Preserve:** evidence records are append-only; SQLite triggers reject update and delete operations through the layer's database.
- **Provenance:** every entry requires a source reference and may identify earlier entries in `derived_from`.
- **Temporal reconciliation:** claims can carry effective-time intervals. Different statements with overlapping or unknown intervals are surfaced as review-required.
- **No silent winner:** reconciliation returns every relevant record and conflicting identifier pair; it does not choose which claim is true.
- **Reversibility:** the first implementation is additive and isolated on its own branch; it does not alter legacy modules or historical artifacts.
- **Human authority:** conflict review and any downstream promotion remain explicit human decisions.

## Initial interface

Module: `python/cognitive_layer.py`

- `MemoryEntry`: immutable record with identity, subject, statement, source, recording time, optional effective period, and lineage.
- `TemporalCognitiveLayer.append(entry)`: append-only insertion with source, timestamp, and parent validation.
- `entries(subject=None)`: chronological retrieval with lineage.
- `reconcile(subject)`: review report for potentially overlapping, non-identical claims.
- `lineage(entry_id)`: direct source ancestry.
- `ReconciliationReport.status`: `NO_OVERLAP_CONFLICTS` or `REVIEW_REQUIRED`.

Unknown effective-time bounds are treated conservatively. They may create extra review work, but cannot silently suppress a possible conflict. Identical normalized statements are retained as separate records and are not treated as proof of independent corroboration.

## Explicit non-goals

- No edits to `cold`, `Cold.html`, extracted legacy modules, or existing application behavior.
- No autonomous branch propagation, force-push, history rewrite, or source deletion.
- No automatic truth-ranking based on recency, popularity, embedding distance, or confidence alone.
- No inference that spiritual beliefs, memory, or identity continuity are experimentally established facts.
- No connection to biological systems or claims of changing DNA/RNA or consciousness.

## Validation

Run from the repository root:

```bash
PYTHONPATH=python python -m unittest discover -s tests -v
python -m py_compile python/cognitive_layer.py
```

The tests cover append-only behavior, duplicate protection, lineage validation, overlapping and non-overlapping time periods, conservative handling of unknown periods, timezone validation, and database-level update/delete rejection.

## Next phases

1. Review this isolated implementation and its tests.
2. Run the branch CI and record the actual result.
3. Design an adapter to existing semantic memory only after reviewing its persistence and metadata contract.
4. Add explicit review/approval records for reconciliations.
5. Integrate with adaptive governance only through a documented interface and tests.
6. Consider promotion through a reviewed pull request; do not propagate automatically.

**Covenant:** Preserve without imprisoning. Transform without betraying. Evolve without erasing.
