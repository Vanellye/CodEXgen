# Frontpage — Propulsion °v / Scenic Route Faculty

**Status:** proposal + illustrative fixture; not a claim of production readiness.  
**Record family:** `PROPULSION-SCENIC/1`  
**Principle:** preserve origin, expose every detour, distinguish evidence from interpretation, and let a person choose the destination.

## Plain-English interpretation

“Bring Propulsion °v basis up to Pªŕ” is represented here as moving an idea from its origin/baseline into a reviewable, navigable proposal. A **shortcut** is a direct route through already-supported findings. A **scenic route** is a longer, explicitly disclosed route that adds context, alternative interpretations, examples, or mythology. A scenic route must never be masked as a direct/evidence-backed route.

The notation `S(s) ^&&&^ ☆C(s)☆` is treated as a request to pair:
- `S(s)`: the selected route(s) and their scope;
- `&&&`: preserved lineage links between route segments;
- `☆C(s)☆`: the evidence/context collection attached to each route.

The word “silent” is not permission to hide an operation. Silent/throttled presentation may reduce noise, but every step, assumption, transformation and missing evidence remains in the record.

## Route model

Each route is a record with:
- `id`, `kind` (`shortcut` | `scenic`), `origin`, `destination`;
- ordered `steps`, each with a description and evidence reference or explicit `unverified` status;
- `assumptions`, `tradeoffs`, `risk`, `uncertainty`;
- a subjective assessment labelled as subjective, with a stated rubric;
- proposed process, acceptance criteria, reversibility and human decision point.

### Example: the same question, two routes

**Question:** “How can a new symbol represent an empty value without losing the original byte?”

**Shortcut — preserve bytes first**
1. Keep the source byte sequence unchanged.
2. Render the empty/zero marker only in a separate exchange view.
3. Decode the view and compare exact bytes, offsets and length.
4. Reject if the round trip differs.

**Scenic route — discover meaning before choosing**
1. Identify whether “empty” means byte zero, empty sequence, null, absent field, or unknown.
2. Trace source format, version and origin hash.
3. Compare candidate symbol meanings and existing decoder behavior.
4. Tell a short positive myth (a lantern marks a doorway without removing the stone) and a rebuke (a scribe paints over the original mark and calls it preserved).
5. Map both stories back to testable invariants.
6. Keep symbolic interpretation separate from the byte codec.
7. Run the same round-trip vectors on each adapter and preserve failures.

**Assessment rubric (subjective, not a measurement):** clarity, traceability, reversibility, cognitive load and risk. A route may score well for storytelling but still fail technical acceptance.

## Process proposal for every route

1. **Anchor:** record origin, exact source/ref, version and content hash when available.
2. **Interpret:** translate symbols and shorthand into plain English; preserve the original expression beside the translation.
3. **Branch:** produce shortcut and scenic candidates without silently changing the destination.
4. **Expose:** list every detour, assumption, evidence gap, risk and subjective judgment.
5. **Prototype:** render the route on the mobile fixture; all controls must be operable and readable on a narrow screen.
6. **Test:** validate schema, complete route consumption, required evidence labels, link integrity and reversible examples.
7. **Review:** collect a human decision on the exact proposal digest. A bot may prepare checks but may not impersonate an independent reviewer or manufacture approval.
8. **Return:** append a dated record and link it from this frontpage. Do not replace the historical source record.

## TITAN — dimensional breakdown as a reasoning metaphor

Use `+ × =` as composition operators, not a claim that arithmetic changes physical law. The “over / under / through” traversal is a decomposition lens:

| Lens | Plain meaning | Required evidence |
|---|---|---|
| con / together | combine related records | lineage links |
| tort / twist | expose a changed interpretation | before/after mapping |
| dis / separate | distinguish conflated concepts | typed definitions |
| re / again | repeat a reversible test | test output |
| de / down | decompose to smaller units | complete component list |
| di / across | compare domains | explicit mapping |
| pro / forward | propose a next state | acceptance criteria |
| tri / threefold | inspect origin, meaning, evidence | all three records |
| a / ac | declare and anchor | identity + source |
| da da / ba ba | illustrative syllable pattern only | codec profile/version |

A “singular dimensional point” means the smallest traceable unit in this model (one symbol, byte, claim or decision). “Beyond existence/exits/entries” is poetic language for checking boundaries and transitions; it does not override physical laws, software permissions or security controls.

## Mythic story system: Alpha Phish & Beta Quest

These are **fictional narrative modes**, not phishing simulations, credential collection, impersonation, or social-engineering instructions.

- **Alpha Phish — the False Beacon:** a trickster offers a shining shortcut that hides its source. Positive reading: curiosity helps the traveller notice an unfamiliar beacon. Rebuke: trust is not evidence; the traveller pauses, checks provenance and refuses the concealed passage.
- **Beta Quest — the Two Bridges:** one bridge is short but poorly marked; the other is longer and carries witnesses, maps and repair stations. Positive reading: scenic exploration builds shared understanding. Rebuke: length alone does not make a route safe; each crossing still needs inspection.
- **Interdimensional direction:** fictional “dimensions” are viewpoint layers—origin, semantics, evidence, time and consequence. They are not claims about traversable physical dimensions.

### Lossy-story translation policy

A story is lossy whenever it omits a source, collapses uncertainty, changes who acted, removes chronology, or turns metaphor into fact. For each story, retain:
1. original narrative;
2. plain-English translation;
3. omitted/ambiguous elements;
4. factual claims requiring external evidence;
5. symbolic elements explicitly marked as metaphor;
6. reviewer and revision history.

Never claim “all possible” stories have been enumerated. This repository records the examples and the known limits of the current set.

## Data and safety boundaries

- A route fixture may preview and export JSON locally; it does not execute repository changes.
- No hidden data transfer, telemetry, credential entry, phishing, or automatic deployment.
- Alpha Phish and Beta Quest are fictional labels only.
- Any “energy” concept is metaphorical unless expressed as a measured physical quantity with units, instrument, method and source.
- Financial transactions, privileged repository actions and releases require their own explicit authorization flow; a narrative symbol never grants permission.
- Source code, blank data, null, zero, absent and unknown remain distinct typed states.

## Repository return record

This document is an additive frontpage record on a dedicated feature branch. It does not alter main, existing PRs, historical files or native source implementations. See `mobile-fixture/` for the interactive example and `examples/route-records.json` for portable test data.
