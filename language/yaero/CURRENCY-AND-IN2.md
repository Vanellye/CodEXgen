# Ŷæṛö currency decode and singular dimensional split

## Goal

Provide two composable, provenance-preserving semantic operations:

1. Decode exact currency records into typed monetary values and plain-English descriptions.
2. Apply `in2` to split a preserved source into singular semantic projections, then translate those projections into plain English.

These are data interpretation operations. They do not move money, fetch exchange rates, or authorize transactions.

## Currency record v1

Canonical JSON shape:

```json
{
  "schema": "yaero.currency/1",
  "currency": "USD",
  "minorUnits": "12345",
  "exponent": 2,
  "sourceRef": "ledger:entry-123",
  "asOf": "2026-11-23"
}
```

- `minorUnits` is a canonical base-10 integer string. It is never parsed through floating-point arithmetic.
- `exponent` is checked against currency metadata.
- Initial verified metadata: USD, EUR, RUB (2 decimal places); KRW (0).
- Unsupported but syntactically valid codes return `UNKNOWN_CURRENCY`, not a fabricated conversion.
- Malformed input returns `INVALID`; unsupported schema returns `UNSUPPORTED`.
- Original serialized input is returned unchanged as `sourceSnapshot`.
- No FX conversion is performed. A conversion requires a separately sourced, dated rate and explicit source/target currency.

## English translation and intent

The literal English renderer spells out the exact amount. Example: 12345 USD minor units becomes “one hundred twenty-three dollars and forty-five cents.”

The intent interpreter does not guess from the amount. It accepts only explicit action evidence: `payment`, `receipt`, `refund`, `transfer`, `quote`, or `balance`. Without that evidence it returns `UNKNOWN` and explains why. Intent evidence carries its source reference.

## Singular dimensional split: `in2`

The operation preserves the original source snapshot and creates separate, read-only projections:

- **Identity (X):** what the subject is.
- **Relationship (Y):** how it connects to other subjects.
- **State (Z):** what is established about it.
- **Time (T, optional fourth axis):** when it applies or how it progresses.

The prior navigation vocabulary remains available:

- **OVER:** whole-system context.
- **UNDER:** nested, hidden, or residual material.
- **THROUGH:** lineage and dependency paths.

Each projection contains exactly one semantic axis, the original `sourceRef`, and the original `sourceSnapshot`. Missing or null values are `UNKNOWN`, not zero. The source is never destructively split or rewritten.

## “True intent” interpretation contract

The interpreter produces two layers:

1. **Literal decode:** what the bytes/fields explicitly say.
2. **Intent interpretation:** a constrained explanation backed by explicit fields and evidence references.

It must label unsupported conclusions as `UNKNOWN`; distinguish observed facts from inferred possibilities; retain uncertainty and conflicting evidence; and never convert an interpretation into a fact. “True intent” is an evidence-seeking goal, not a claim of mind-reading or certainty.

## Composition

1. Preserve raw input and provenance.
2. Decode currency into exact minor units.
3. Apply `in2` to independently inspect identity, relationship, state, and optional time.
4. Render literal English.
5. Interpret intent only from explicit, source-linked evidence.
6. Publish diagnostics and uncertainty alongside results.

## Test

From `apps/yaero-frontpage` run:

```sh
npm test
```

Tests cover exact minor units, zero-decimal currency, unknown codes, intent uncertainty, source preservation, dimensional projections, and provenance requirements.
