# Sure-Rarity — Evidence Measure

**Status:** proposed evaluation model; not a truth oracle or permission system.

## Meaning

“Sure rarity” is modeled as a discipline for handling uncommon, high-confidence, or unusual claims without confusing rarity with reliability. A rare observation can be important, but rarity alone is not evidence that the observation is correct.

## Evidence dimensions

Evaluate each claim against separate dimensions:

- **Source integrity:** is the origin identifiable and preserved?
- **Directness:** does the evidence directly support the claim?
- **Independence:** are supporting observations genuinely independent?
- **Reproducibility:** can the result be repeated under documented conditions?
- **Consistency:** does it agree with other reliable evidence, or explain conflicts?
- **Uncertainty:** what is unknown, estimated, or contradicted?

Record each dimension as `SUPPORTED`, `PARTIAL`, `UNKNOWN`, or `CONTRADICTED`, with citations or test artifacts. Do not collapse missing evidence into a positive score.

## Rarity and confidence

Rarity describes frequency or unusualness; confidence describes support. Keep them separate:

`rarity ≠ confidence ≠ authorization`

An unusual event may justify investigation, not mutation. Confidence can inform whether a proposal merits review, but even very strong evidence cannot grant write, rewrite, delete, or dispatch rights.

## Measurement record

Each evaluated claim should include:

- claim ID and exact wording;
- source and immutable revision;
- observation window and measurement method;
- evidence items and their independence;
- uncertainty, assumptions, and known conflicts;
- result and reviewer;
- next verification step.

## Decision states

- `SUPPORTED`: evidence meets the stated test criteria.
- `PARTIAL`: some evidence supports the claim, but gaps remain.
- `UNRESOLVED`: evidence is insufficient or ambiguous.
- `CONTRADICTED`: reliable evidence conflicts with the claim.

No state automatically invokes an actuator or changes repository contents.
