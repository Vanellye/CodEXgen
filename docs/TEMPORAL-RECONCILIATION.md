# Counterclockwise Temporal Reconciliation

**Status:** Partially implemented; temporal JOB adapter and read-only comparisons are available  
**Working branch:** `olpirt/stride-next`  
**Source commits:** [`53221f1`](https://github.com/Vanellye/CodEXgen/commit/53221f1a87d59523864727418c62d839f406bd69) — legacy preservation and independent peering; [`13d2d94`](https://github.com/Vanellye/CodEXgen/commit/13d2d94f66103315b3e1b84440a2d83b441e89ef) — correction of an unresolved historical reference.

## Purpose

Combine preservation with correction into a reversible temporal-navigation model: move backward through recorded seconds to inspect the path that led to a day, move forward through recorded events to understand consequences, and explore explicitly labeled speculative futures without confusing fiction with evidence.

“Counterclockwise seconds” is a navigation metaphor and proposed interface behavior. It does not reverse physical time, alter clocks, or change astronomical events.

## Two source commitments, one operating model

- **Preservation (53221f1):** retain original events, source identity, provenance, and historical behavior.
- **Correction (13d2d94):** amend an inaccurate interpretation while retaining the original statement and showing why it changed.
- **Combined rule:** never repair a misunderstanding by erasing the evidence that it existed. Append a correction with its source, author, timestamp, rationale, and affected views.

## Temporal navigation

Represent a timeline as an ordered event ledger. Each event has an immutable identifier, source reference, observed timestamp (if known), logical sequence, confidence/evidence label, and links to prior and subsequent events.

### Counterclockwise: inspect the past

1. Begin at a selected second or event.
2. Step backward through the ledger in reverse sequence: seconds → minutes → hours → days.
3. At each step, expose the source event, its dependencies, and the context available at that time.
4. Allow replay and comparison, but never mutate the original record.
5. Mark gaps as unknown; do not invent missing seconds or dates.

### Clockwise: follow consequences

1. Resume from a selected event.
2. Traverse later recorded events in their original order.
3. Show verified outcomes separately from inferred consequences.
4. Permit a branch into a forecast or scenario, clearly marked as a projection rather than a recorded future.

### From days to known space and science fiction

Use two separate navigation layers:

- **Known Space:** evidence-backed astronomical objects, coordinate systems, observation dates, catalog/source versions, and uncertainty. Preserve units and reference frames; never silently mix incompatible coordinate epochs or systems.
- **Science-Fiction Space:** imagined destinations, alternate histories, speculative physics, and narrative timelines. Label these as fictional or hypothetical, with their assumptions visible.

A user may travel between these layers in the interface, but a speculative result must never be promoted to a factual astronomical record without independent evidence.

## Reverting misunderstandings and rebuking wrongs

“Rebuke” means challenge a claim with evidence and a clear explanation—not attack a person or suppress a viewpoint.

A correction record must include:

| Field | Meaning |
|---|---|
| Original event/claim | Immutable source and exact reference |
| Correction | The amended interpretation or value |
| Evidence | Sources, tests, observations, or reason for uncertainty |
| Change type | Correction, retraction, clarification, or unresolved dispute |
| Scope | Views, projections, or derived outputs affected |
| Provenance | Contributor, timestamp, and tool/version |
| Recovery | How to restore the prior derived view |

Corrections update derived interpretations and indexes; they do not rewrite source history. If evidence is incomplete or disputed, preserve both positions and label the status unresolved.

## Reversal, replay, and safety boundaries

- Rewind is read-only by default.
- Replaying an event must not repeat external side effects.
- Any consequential action requires fresh authorization and an explicit preview.
- A rollback restores a derived state or configuration; it does not pretend the original event never occurred.
- Use deterministic ordering for events with equal or missing wall-clock timestamps.
- Keep real timestamps, logical sequence numbers, simulated time, and fictional dates in separate fields.
- Record time-zone and calendar assumptions; never infer precision that the source does not provide.

## Minimum verification

- Reverse traversal returns the exact inverse order of the selected event sequence.
- Forward traversal restores the original order without dropping events.
- A correction leaves the original event and its hash/reference intact.
- Replaying an event is idempotent and does not repeat external side effects.
- Fictional and projected events cannot enter the Known Space evidence layer without explicit review.
- Unknown timestamps, conflicting records, and missing provenance remain visibly unresolved.

## Relationship to preservation and peering

This specification is governed by the [Legacy Preservation & Independent Peering Protocol](LEGACY-PEERING-PROTOCOL.md). Temporal navigation is a consumer of preserved records, not an authority over their origins. Any connection to another branch or component must document its interface, provenance, permissions, and tests before peering.

## Cognitive-layer consumer\n\n[Holified Inception](HOLIFIED-INCEPTION.md) consumes this temporal model to trace origins, inspect recorded context, surface contradictions, and explore clearly labeled possibilities. It must preserve the event ledger, keep simulated and fictional time separate from observed time, and return derived interpretations with provenance. The optional JOB-history adapter is implemented in `python/stride_core/job_history.py` and exposed through `read_with_job_history()` in `python/stride_core/holified_inception.py`. Access requires `authorized=True` and explicit JOB identifiers. It reads event ledgers only, retains source references and recorded timestamps, supports forward and reverse recall, and compares repeated scalar payload fields within each JOB. Conflicting values are preserved; no winner is selected. The adapter does not enumerate JOBs, mutate records, replay actions, or make JOB storage subordinate to the reader. Full chronology across other stores and correction-ledger workflows remain future work.\n\n## Governing statement

**Turn the record backward to understand. Turn the view forward to learn. Correct the interpretation without erasing the origin. Keep known space factual and imagined space honestly imagined.**
