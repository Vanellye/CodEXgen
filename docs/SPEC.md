# Ɣơ (Yoro) — Encoding Specification

**Format version:** 0.1  
**Codec profile:** `og-base5-syllables/0.1`  
**Suggested extension:** `.og`  
**Status:** Draft

## 1. Purpose and scope

Ɣơ (Yoro) is an experimental, reversible notation for representing arbitrary bytes with vowel-and-consonant symbols. This specification defines a byte encoding format only. It does not define a programming-language compiler, translate program semantics, or make encoded content executable.

## 2. Glyph alphabet

The profile maps base-5 digits to syllables:

| Base-5 digit | Glyph |
|---:|:---:|
| 0 | `ba` |
| 1 | `be` |
| 2 | `bi` |
| 3 | `bo` |
| 4 | `bu` |

Digits are written most-significant first. Each byte is represented by exactly four syllables, retaining all leading zero digits.

## 3. Canonical envelope

A version 0.1 document has exactly five lines:

```text
OG/0
kind:BYTES
length:<decimal-byte-count>
payload:<empty-or-byte-tokens>
codec:og-base5-syllables/0.1
```

For non-empty input, byte tokens are separated by comma followed by one space. For empty input, the payload value is the literal `empty`.

## 4. Byte mapping

Interpret each byte as an unsigned integer from 0 through 255. Convert it to exactly four base-5 digits, most-significant first, then map each digit through the glyph table.

Examples:
- Byte `00` → `ba-ba-ba-ba`
- Byte `01` → `ba-ba-ba-be`
- Byte `FF` → `bi-ba-be-ba`

The declared length is the number of original bytes, not the number of glyphs or Unicode characters.

## 5. Required properties

A conforming encoder and decoder MUST:
- Preserve every input byte, including zero bytes and leading zero bytes.
- Preserve byte order and input length.
- Produce deterministic output for the same input.
- Reject malformed envelopes, invalid glyphs, invalid token counts, and unsupported codec profiles.
- Enforce the implementation's documented size limit.

For every supported byte sequence `B`:

```text
decode(encode(B)) = B
```

## 6. Versioning

Changes that alter tokenization, byte mapping, envelope interpretation, or decoding behavior MUST use a new codec profile version. A decoder MUST reject unknown versions unless it explicitly implements them.

## 7. Non-goals

Version 0.1 does not parse or compile Kotlin, C++, Python, or other source languages; preserve program meaning through source transformation; execute or evaluate payloads; or claim improved storage efficiency over binary or conventional byte encodings.
