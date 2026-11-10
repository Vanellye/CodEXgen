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


## Seven governing invariants

These statements are normative requirements for every future cognitive-layer extension:

1. **Historical memory remains immutable.** Existing evidence is never silently edited or deleted; corrections are appended as new, linked records.
2. **New knowledge retains its source and lineage.** Every promoted claim must identify its source and preserve derivation links to earlier evidence.
3. **Conflicting memories are reconciled, not silently overwritten.** Conflicts remain visible with their competing records and temporal context until an authorized review resolves or classifies them.
4. **Outdated assumptions can be challenged without erasing their history.** A superseding conclusion is a new versioned claim, not a rewrite of the historical record.
5. **Learning and adaptation require evidence, validation, and rollback.** Proposed changes need a rationale, reproducible checks, an approval record, and a documented reversal path before promotion.
6. **Human authorization remains above automated mutation.** Automation may detect, compare, summarize, and propose. It may not independently approve reconciliations, rewrite protected records, propagate changes, or mutate shared foundations.
7. **Every generation can extend the system without destroying its foundations.** Extensions are additive, traceable, compatibility-aware, and independently testable; legacy artifacts remain preserved.

### Acceptance gate for future extensions

A future component is not eligible for promotion unless reviewers can verify all of the following:

- Original records and their source references remain retrievable and unchanged.
- Each new claim has source metadata and complete derivation links where applicable.
- Conflicts are surfaced with uncertainty intact; no recency-only or confidence-only winner is selected.
- Superseding claims preserve the earlier claim and explain what evidence changed.
- Tests cover expected behavior, failure paths, and rollback/recovery.
- A human approval is recorded before any shared-state mutation or branch propagation.
- The extension can be disabled or reverted without destroying the historical ledger.

These invariants extend the Zero-Dissipation Anchor; they do not supersede it.

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
