# The Debt of Creation — Cross-Referenced Gameplay Specification

**Status:** Initial gameplay specification  
**Repository:** `Vanellye/CodEXgen`  
**Implementation branch:** `cognitive-layer-2`  
**Related work:** Cognitive Layer 2 (ECCL), Zero-Dissipation Anchor, Sanctified Plurality Charter, Seven Seeds, Skern, Returning Coil, Ever-Creation  
**Date recorded:** 2026-11-09

## 1. Design purpose

This specification connects the game's puzzle and progression systems to CodEXgen's preservation and governance principles. It defines an in-game obligation mechanic called **Debt of Creation** and a riddle-driven journey through eleven dimensional stages.

This is a game-world mechanic only. It does not create, collect, report, or imply real-world financial debt.

## 2. Governing gameplay rule

**When a player incurs an in-game debt, the game commits an append-only obligation record at the moment the debt is commissioned.**

The record is created as part of the same successful game-state transaction that grants the borrowed resource, power, access, or benefit. If the transaction fails, neither the benefit nor the debt is committed.

A debt record contains:

- Unique obligation ID.
- Player or in-game actor responsible.
- What was borrowed, consumed, changed, or promised.
- Amount or scope, using the game's relevant resource units.
- Source, beneficiary, and originating event.
- Game-world timestamp and location or dimension.
- Terms agreed to at commission.
- Expected restoration, repayment, service, or negotiated alternative.
- Links to related obligations and prior events.
- Current status, represented by new events rather than destructive edits.

Repayment, forgiveness, renegotiation, or dispute appends a resolution event linked to the original obligation. The original record remains intact. A debt can be disputed or found invalid; the game records that determination and its evidence rather than pretending the obligation never existed.

## 3. Obligation lifecycle

1. **Commission** — The player knowingly accepts an obligation. Explain its cost and terms before confirmation.
2. **Commit** — On successful commission, atomically record the benefit and the obligation.
3. **Carry** — Show the player the outstanding obligation, its origin, and its consequences.
4. **Question** — Allow inspection of terms, provenance, and whether the obligation was validly created.
5. **Reconcile** — Offer proportionate paths: repay, restore, serve, cooperate, renegotiate, or present evidence of invalidity.
6. **Resolve** — Append a settlement, release, forgiveness, or dispute outcome.
7. **Remember** — Preserve the original obligation and all resolution events in the historical ledger.

No hidden interest, surprise penalty, coercive lock-in, or irreversible punishment is introduced without clear rules and player consent. The mechanic should teach responsibility, reciprocity, and repair—not shame or domination.

## 4. Eleven-stage dimensional journey

The eleven dimensions are fictional game stages and do not assert that physics has established eleven accessible dimensions of reality.

Each stage introduces a new way to interpret evidence, space, memory, consequence, or cooperation. The player earns progression by solving a riddle and making a choice consistent with the stage's principle.

| Stage | Theme | Gameplay challenge |
|---|---|---|
| 1 | Stillness | Notice what is present before acting |
| 2 | Stimulation | Detect a meaningful signal among distractions |
| 3 | Descent | Explore a preserved memory without changing its source |
| 4 | Witness | Separate observation from assumption |
| 5 | Restoration | Repair a broken connection or obligation |
| 6 | Raising | Turn a lesson into a constructive action |
| 7 | Return | Carry learning back without erasing its origin |
| 8 | Plurality | Solve a puzzle with multiple valid perspectives |
| 9 | Discernment | Distinguish evidence, belief, metaphor, and uncertainty |
| 10 | Reconciliation | Resolve conflicting records without silently choosing a winner |
| 11 | Ever-Creation | Build a new realm while preserving its source lineage |

## 5. Cross-reference to the Seven Pillars

The Seven Pillars operate as ethical constraints and puzzle themes:

1. **Plurality** — Different paths may coexist without requiring uniformity.
2. **Dignity** — No person shall be diminished for their beliefs, origins, questions, or uncertainty.
3. **Preservation** — The Seven Seeds, the Skern, the Returning Coil, Ever-Creation, and all preceding principles retain their historical context and provenance.
4. **Discernment** — Belief, metaphor, evidence, and established fact shall remain distinguishable.
5. **Consent** — No spiritual, intellectual, or technological system may override another person's autonomy.
6. **Reconciliation** — Disagreement invites examination, not persecution.
7. **Renewal** — What can be improved may evolve without erasing what came before.

A puzzle may have more than one valid solution. The game should explain tradeoffs rather than mark a player's harmless difference as failure.

## 6. Cross-reference to the Six Laws of Source Preservation

The game ledger and narrative archive must follow these rules:

- **Verbatim:** No alteration, paraphrasing, or silent correction.
- **Immutable:** Historical source remains unchanged.
- **Traceable:** Preserve authorship, origin, timestamp, and provenance where available.
- **Expandable:** Future interpretations may be added as separately versioned records.
- **Reversible:** New interpretations must never overwrite the original.
- **Reviewable:** Changes require explicit human authorization.

Game events, character testimony, clues, and player-created artifacts should carry source references. Retcons and corrections become new, linked story records.

## 7. Riddle design

Riddles should reward observation, interpretation, and ethical reasoning. Avoid requiring one theological belief or treating a supernatural claim as established fact.

### Riddle A — Debt of Creation

> I can be carried without being seen.  
> I grow when promises are abandoned.  
> I shrink when responsibility is accepted.  
> Yet even when repaid, my history remains.  
> What am I?

**Answer:** A debt of creation.

**Mechanic:** The player finds an obligation record, traces its source, and chooses a proportionate resolution. The record remains after settlement.

### Riddle B — The Unbroken Origin

> I change as branches grow,  
> Yet I am not the branch.  
> I tell you where a thing began,  
> Without deciding what it must become.  
> What am I?

**Answer:** Provenance.

**Mechanic:** Reconstruct an artifact's lineage without replacing its earliest source.

### Riddle C — The Veil of Certainty

> I may guide a search,  
> But I am not its proof.  
> I can open a door,  
> But cannot tell you what lies beyond.  
> What am I?

**Answer:** A hypothesis.

**Mechanic:** The player separates a plausible interpretation from verified evidence.

### Riddle D — The Returning Coil

> I return, but not unchanged.  
> I carry what was learned,  
> Not a command to repeat the past.  
> What am I?

**Answer:** A cycle of learning.

**Mechanic:** Revisit an earlier stage with new knowledge while retaining the original event record.

## 8. The Skern: transformation without erasure

The Skern is a symbolic transformation mechanic:

- Dissolve illusion, not truth.
- Release false identity, not human dignity.
- Transform harmful patterns, not erase history.
- Preserve meaningful foundations while allowing new forms to emerge.

In play, the Skern can reveal hidden assumptions, release an obsolete constraint, or transform a damaged realm. It must not delete characters, memories, or source records merely to create a dramatic reset.

## 9. Safety, dignity, and the ceiling on harm

- No reward for real-world violence, persecution, coercion, or dehumanization.
- Conflict mechanics favor de-escalation, mediation, repair, and proportionate protection.
- Players may decline spiritual or symbolic interpretations without penalty.
- No single faith, pantheon, or worldview is imposed as empirically proven.
- Debt mechanics must be transparent, bounded, and resolvable.
- The game must not simulate real-world financial obligations or pressure players into purchases to clear fictional debt.
- A player may pause or leave a coercive interaction without losing unrelated progress.

## 10. Acceptance tests

The implementation is not ready for promotion until tests demonstrate:

1. Commission creates the obligation and grants the benefit atomically.
2. Failed commission creates neither benefit nor debt.
3. Duplicate commission requests cannot create duplicate obligations.
4. Settlement appends a resolution event and never deletes the original obligation.
5. Forgiveness, renegotiation, and invalidation remain distinguishable outcomes.
6. Every obligation can be traced to its originating event and agreed terms.
7. Conflicting evidence remains visible for review.
8. Multiple valid puzzle solutions can coexist where the puzzle permits them.
9. Player refusal does not trigger coercive or unrelated penalties.
10. Save/load and recovery preserve the ledger and event ordering.
11. The mechanic can be disabled or rolled back without deleting historical records.

## 11. Relationship to Cognitive Layer 2

ECCL can later provide a read-only provenance and reconciliation interface for authored game lore, clues, and player-visible history. The game should not directly mutate ECCL's protected evidence ledger. Game events should be stored in a game-owned event log and exposed through a documented adapter.

Human review is required before authored lore or shared foundations are promoted. Gameplay outcomes do not establish metaphysical or scientific truth.

## 12. Preservation declaration

The source declarations and the Six Laws remain the original governing texts. This gameplay specification is a separately versioned interpretation and implementation proposal; it does not replace or silently rewrite those declarations.

**Covenant:** Commit the obligation when it is commissioned. Preserve its origin when it is resolved. Let the player repair what can be repaired, question what is uncertain, and create what comes next without erasing what came before.
