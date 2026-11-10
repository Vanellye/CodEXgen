# Stride Context Map — Holified Inception

**Status:** Point-in-time source map; no binding agreements or contracts  
**Branch inspected:** `olpirt/stride-next`  
**Purpose:** Identify existing Stride perception and creativity capabilities, their actual interfaces, and a safe way to add Holified Inception beside them.

## Reading this map

This is an observational map of source files and callable behavior, not a contract, mandate, compatibility guarantee, or transfer of ownership. The existing components remain independent. The Holified Inception engine is an additive reader and does not replace, rewrite, or take control of them.

## Existing components observed

| Component | Existing interface / behavior | How Holified Inception relates |
|---|---|---|
| `python/stride_core/faculty_engine.py` | `assess_perception(observations, weights=None)` ranks supplied numeric features; `generate_ideas(concepts, max_combinations=12)` creates deterministic pair prompts. | Reuses these existing functions as optional local helpers. Their outputs remain feature scores and idea prompts, not comprehensive perception or established knowledge. |
| `python/stride_core/job_engine.py` | `JobStore` creates and retrieves local SQLite Journeys of Becoming, records lifecycle events, branches, and contextual metrics. | Optional adapter reads only explicitly selected JOB event ledgers after caller authorization; no writes or global enumeration. |
| `python/semantic_vector_memory.py` | Chroma-backed persistent semantic trace storage and similarity retrieval; imports Chroma dependencies. | Optional future context source only. Not imported by the new engine; retrieval scope, consent, provenance, and privacy must be examined before any connection. |
| `python/adaptive_governance.py` | Async telemetry and prompt-tuning orchestration; imports NumPy and writes telemetry to SQLite; includes simulated judgement and self-correction behavior. | Not called by the first engine. Its automatic rewrite/lock behavior is intentionally not inherited. |
| `python/olpirt/rise_wisdom_bridge.py` | Existing Rise/Wisdom bridge. | Candidate for later contextual mapping after its complete source and tests are inspected; not called by this initial implementation. |
| `hypotheticals/*` | Explicitly fictional model family, including perfect-perception and resonance-fiction concepts. | Can inspire labeled creative exploration, but fictional material is not treated as evidence or imported as factual knowledge. |

## First implementation added

New independent module: `python/stride_core/holified_inception.py`

Public entry point:
- `read_beyond_present(present, context=(), observations=None, creative_concepts=())`

New data structures:
- `ContextItem`: immutable source-bearing context item with an explicit evidence label.
- `ContextLink`: relationship only when a context item explicitly references another supplied item.
- `HolifiedReport`: present reading, origins, links, tensions, possibilities, discernment, return summary, next steps, and execution boundaries.

The engine:
- imports only the existing local `faculty_engine` helpers;
- accepts context supplied by the caller and does not retrieve external or private records;
- preserves source/evidence labels and flags unavailable references as unknown;
- keeps idea combinations labeled as hypotheses;
- does not persist data, mutate source items, write to JOBs, invoke telemetry, call networks, or perform external actions.

## Contextual flow

```text
Caller supplies present + optional context
                 |
                 v
       Holified Inception reader
                 |
       +---------+----------+
       |         |          |
       v         v          v
     Origin   Explicit    Tensions
     labels   references  and gaps
       |         |          |
       +---------+----------+
                 |
        Optional Stride helpers
        - faculty perception
        - creative recombination
                 |
                 v
       Evidence-aware report
                 |
          Human interpretation
```

This is a one-way read-only composition for the first phase. It does not establish a new shared runtime, shared storage, or automatic data propagation.

## Known limits and next mapping targets

- Numeric feature ranking is not broad semantic understanding. It reports the existing helper's bounded score behavior.
- Deterministic concept pairing is not proof of novelty, usefulness, or truth.
- Explicit references are not proof of causation.
- The supplied-context reader remains independently usable. Optional JOB temporal recall is now available through `read_with_job_history()` and `python/stride_core/job_history.py`; vector memory remains unconnected.
- The map does not establish runtime compatibility across every Stride module.
- Existing source SHAs should be refreshed before any deeper integration.

## Verification record

New tests: `tests/test_holified_inception.py`

The test file covers origin preservation, explicit-link mapping, unresolved references, disputed evidence, optional reuse of perception and creativity helpers, no-context limitations, invalid labels/duplicate identifiers, and read-only behavior.

Execution status: the original Holified Inception test run exposed one assertion wording mismatch. That assertion was corrected. New JOB history and reader-bridge tests are committed; the latest CI run is pending, so no pass is claimed yet.

## Preservation boundary

Existing files remain untouched:
- `python/stride_core/faculty_engine.py`
- `python/stride_core/job_engine.py`
- `python/semantic_vector_memory.py`
- `python/adaptive_governance.py`
- `python/olpirt/rise_wisdom_bridge.py`
- `hypotheticals/*`

No branch merge, history rewrite, deletion, external data transfer, or automatic action is part of this work. JOB history access requires `authorized=True` and explicit JOB IDs; comparisons preserve both values and do not adjudicate truth.

**Working principle:** Map the context. Respect each component's identity. Add new capability beside existing capability. Let evidence—not declarations—establish what works.
