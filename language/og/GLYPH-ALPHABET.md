# Ɣơ Glyph Alphabet — Profile 0.1

The v0.1 glyph profile maps base-5 digits to consonant-vowel syllables.

| Base-5 digit | Glyph | Interpretation |
|---:|:---:|---|
| 0 | `ba` | explicit zero digit |
| 1 | `be` | one |
| 2 | `bi` | two |
| 3 | `bo` | three |
| 4 | `bu` | four |

The consonant `b` is a stable syllable onset. The vowel distinguishes the digit. This is a reversible textual code, not a natural-language phonology.

## Reserved notation

| Glyph | Proposed role | v0.1 status |
|---|---|---|
| `Ɣ` | language/profile prefix | documentation marker only |
| `ñ` | namespace marker | reserved |
| `r` | run-length compression marker | reserved |
| `z` | explicit zero-run marker | reserved |

Reserved markers have no executable meaning in v0.1. A decoder must reject them if they appear in a byte payload.

## Canonical digit order

Digits are written most-significant first. Each byte has four digits, including all leading zero digits. This fixed width ensures byte boundaries and leading zeros are unambiguous.

## Compatibility

Never change a glyph mapping inside an existing profile version. A revised mapping requires a new profile identifier and test vectors.
