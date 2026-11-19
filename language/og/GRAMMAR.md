# Ɣơ / .og Grammar — Draft 0.1

This grammar describes the byte-envelope prototype, not a complete programming language.

## EBNF

```ebnf
document    = "OG/0", newline,
              "kind:BYTES", newline,
              "length:", integer, newline,
              "payload:", payload, newline,
              "codec:og-base5-syllables/0.1", newline ;

payload     = "empty" | byte_value, { ",", byte_value } ;
byte_value  = syllable, "-", syllable, "-", syllable, "-", syllable ;
syllable    = "ba" | "be" | "bi" | "bo" | "bu" ;
integer     = "0" | nonzero_digit, { digit } ;
digit       = "0" | nonzero_digit ;
nonzero_digit = "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
newline     = ? LF byte ? ;
```

## Semantic checks

1. `length` is a non-negative decimal integer.
2. `length` equals the number of byte values in payload; for `empty`, length must be zero.
3. Each byte value has exactly four syllables.
4. Each syllable maps to one base-5 digit.
5. The resulting base-5 integer must be in the inclusive range 0..255.
6. Unknown fields, duplicate fields, unsupported versions, and malformed input are rejected by the reference decoder.

The parser is intentionally stricter than the illustrative EBNF. It does not silently skip unrecognized text.
