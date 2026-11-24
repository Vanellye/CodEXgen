# DEALER Wordspace — Binary Language Encoding v0.1

Status: initial specification; experimental and reversible.

## 1. Canonical token

The wordspace token is `DEALER`. Its identity is the ordered six-letter sequence:

`D · E · A · L · E · R`

This encoding represents spelling, not a claim about the word's meaning or the identity of any person or business.

## 2. Encoding A — ASCII / UTF-8

Each uppercase character is encoded as one 8-bit ASCII byte (also valid UTF-8 for these characters).

| Character | Decimal | Hex | 8-bit binary |
|---|---:|---:|---|
| D | 68 | 44 | `01000100` |
| E | 69 | 45 | `01000101` |
| A | 65 | 41 | `01000001` |
| L | 76 | 4C | `01001100` |
| E | 69 | 45 | `01000101` |
| R | 82 | 52 | `01010010` |

Byte sequence:

```text
01000100 01000101 01000001 01001100 01000101 01010010
```

Hex sequence:

```text
44 45 41 4C 45 52
```

## 3. Encoding B — Wordspace-26

A compact alphabet-index encoding is defined for A–Z:

- A = 1, B = 2, …, Z = 26.
- Each letter is stored as a 5-bit unsigned integer.
- `00000` is reserved as a word separator and is not a letter.
- Values 27–31 are reserved.

| Character | Index | 5-bit code |
|---|---:|---|
| D | 4 | `00100` |
| E | 5 | `00101` |
| A | 1 | `00001` |
| L | 12 | `01100` |
| E | 5 | `00101` |
| R | 18 | `10010` |

Wordspace-26 sequence:

```text
00100 00101 00001 01100 00101 10010
```

Continuous form:

```text
001000010100001011000010110010
```

## 4. Minimal grammar

```ebnf
stream       = { word | separator } ;
word         = letter, { letter } ;
letter       = bit5 ; (* integer value 1 through 26 *)
separator    = "00000" ;
bit5         = "00001" | ... | "11010" ;
```

A decoder must preserve order and repeated letters. It must reject letter values outside 1–26 unless a later version assigns them.

## 5. Round-trip rule

A conforming implementation must satisfy:

`decode(encode("DEALER")) == "DEALER"`

Both encodings are lossless for the uppercase Latin alphabet under the rules above. ASCII/UTF-8 is interoperable with ordinary text tools; Wordspace-26 is a compact custom alphabet code and requires this specification to decode.

## 6. Provenance

- Repository: `Vanellye/CodEXgen`
- Branch: `dealer`
- Branch base: the inspected `main` commit
- Initial wordspace specification: this file
- No existing remote `dealer` branch history was present at inspection time.
- No `main` history was rewritten.

Any future change to the alphabet, token semantics, or bit layout should receive a new version and retain this v0.1 specification for reproducibility.
