# DEALER Wordspace — Binary Language Encoding v0.2

Status: experimental, reversible specification carried forward from the old-antique prototype.

## Canonical token

`DEALER` is the ordered token `D · E · A · L · E · R`. The encodings describe spelling, not inferred meaning or identity.

## Encoding A: ASCII / UTF-8

| Letter | Decimal | Hex | Binary |
|---|---:|---:|---|
| D | 68 | 44 | `01000100` |
| E | 69 | 45 | `01000101` |
| A | 65 | 41 | `01000001` |
| L | 76 | 4C | `01001100` |
| E | 69 | 45 | `01000101` |
| R | 82 | 52 | `01010010` |

```text
01000100 01000101 01000001 01001100 01000101 01010010
```

Hex: `44 45 41 4C 45 52`.

## Encoding B: Wordspace-26

Alphabet mapping: A=1 through Z=26. Encode each value as an unsigned 5-bit integer. `00000` is the word separator; values 27–31 are reserved.

| Letter | Value | 5-bit |
|---|---:|---|
| D | 4 | `00100` |
| E | 5 | `00101` |
| A | 1 | `00001` |
| L | 12 | `01100` |
| E | 5 | `00101` |
| R | 18 | `10010` |

```text
00100 00101 00001 01100 00101 10010
```

Continuous: `001000010100001011000010110010`.

## Decoder contract

- Preserve token order and repeated letters.
- Values 1–26 decode to A–Z.
- Value 0 separates words.
- Values 27–31 are invalid until assigned by a later version.
- Round-trip invariant: `decode(encode("DEALER")) == "DEALER"`.

## Prototype relationship

The old-antique source is the historical `mold` branch. Its deprecated concatenated dump is retained as source evidence at `Cold.html` and `cold`; the actual split Kotlin/Python modules remain in the source tree. The rewrite does not erase or mutate `mold`.

See `dealer/provenance/OLD-ANTIQUE-REWRITE-LEDGER.md` for the old-to-new ref map and source ancestry.
