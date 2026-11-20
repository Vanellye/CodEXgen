# Ɣơ .og intelligence record format v1

The .og format is a UTF-8 JSON Lines presentation envelope. Each record is independent and machine-readable.

Required envelope fields:
- format: "og"
- version: 1
- record_id: stable unique identifier
- source: source reference and SHA-256 when available
- decoded: reversible codec output or a pointer to it
- interpretation_en: human-readable interpretation, explicitly marked as derived
- calculations: named operations, operands, exact result, and units
- status: OBSERVED, DERIVED, HOLD, DENY, or PREPARED

Rules:
- Original source bytes and source digest are retained outside the presentation layer.
- Interpretation is not a substitute for source evidence.
- A derived calculation records its inputs and transformation; no implicit zero deletion or positive-value substitution.
- Financial values use currency code plus integer minor units.
- Medical/environmental observations cannot be promoted into funding evidence without an explicit, reviewed mapping.
- Unknown fields are rejected by strict consumers or preserved in a quarantined extension map; never silently discarded.
