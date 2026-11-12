# Ashes to Angels — The’s Pheônix Abnomaly

**Status:** proposed ERIA specification; runtime behavior is not enabled by this document.  
**Parent:** `integration/wantever-propagation`  
**Purpose:** define a provenance-preserving transformation cycle, explicit rewrite rights, evidence-sensitive certainty, and bounded motion influence.

> Let the ashes remain evidence of what came before. Let renewal create motion, not erase origin.

## 1. Core model

**Ashes to Angels** names a transformation and recovery directory. It preserves the original artifact, records what was learned, and creates a separately identifiable proposed successor.

**The’s Pheônix Abnomaly** names the controlled anomaly path: detect a discrepancy, isolate it, preserve its source, evaluate evidence, propose a transformation, obtain authorization, verify the result, and retain a recovery path. “Anomaly” is not permission to rewrite.

**Rewrite rights** are explicit, operation-specific permissions. This directory documents the permission model; it does not grant anyone repository, filesystem, or runtime rights.

**Sure rarity** is treated as a proposed evidence-quality concept: certainty must be earned by independent, relevant, reproducible support. Rarity of a claim, source, or event does not by itself make it true.

**THANKs** is retained as the exact user-supplied name for a proposed motion-influence layer. No acronym expansion or physical meaning is presumed. Its implementation is bounded, measurable, reversible, and subject to authorization.

## 2. Directory map

- `pheonix/` — anomaly lifecycle, rewrite-rights contract, resurrection/recovery cycle.
- `sure-rarity/` — evidence quality, uncertainty, and measure rules.
- `THANKs/` — motion influence, speed limits, and validation.
- `governance/` — authorization, provenance, and rollback requirements.

## 3. Non-negotiable invariants

1. Preserve the original source and its immutable revision reference.
2. A transformed artifact is a new artifact linked to its source, not a replacement identity.
3. No rewrite, deletion, dispatch, or motion change follows merely from anomaly detection, confidence, rarity, gratitude, or a trigger.
4. Authorization binds actor, repository, branch, paths, operation, expected prior revision, intended result, conditions, and recovery.
5. Evidence quality may change a recommendation; it cannot grant permission.
6. Motion influence must respect configured bounds, rate limits, a stop condition, and human override.
7. Record proposed, authorized, executed, verified, and recovered states distinctly.

## 4. Lifecycle

`ORIGIN → ANOMALY → ISOLATION → EVIDENCE → PROPOSAL → AUTHORIZATION → EXECUTION → VERIFICATION → RECOVERY / LEARNING`

If evidence or authorization is missing, the state is `BLOCKED` or `UNRESOLVED`; do not silently advance.

## 5. Related specifications

- [Pheônix anomaly and rewrite rights](pheonix/rewrite-rights.md)
- [Sure-rarity evidence measure](sure-rarity/evidence-measure.md)
- [THANKs motion influence](THANKs/motion-influence.md)

## 6. Implementation status

These documents define a proposed contract only. No runtime actuator, automatic rewrite, external dispatch, physical motion, or branch-protection change is enabled by this documentation. Implementation requires code, tests, explicit authorization, and review.
