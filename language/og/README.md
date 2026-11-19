# Ɣơ (.og) — ERIA Glyphic Language

Ɣơ (working name: Gamma-O) is a proposed symbolic language and reversible intermediate representation for ERIA. The source extension is `.og`.

## Status

**Prototype package, version 0.1.0.** The reference codec in this directory encodes and decodes byte strings. It is not yet a general-purpose programming-language compiler, virtual machine, or native-code replacement.

## Design promises

- Preserve all source bytes, including zero bytes and leading zero bytes.
- Make lengths and types explicit.
- Use a deterministic, versioned textual representation.
- Keep encoding/decoding distinct from optimization and compilation.
- Retain source provenance and transformation metadata.
- Reject malformed or unsupported input rather than guessing.
- Never execute generated output as part of parsing or validation.

## Package map

- [Language specification](../../docs/OG-LANGUAGE-SPEC.md)
- [Grammar](GRAMMAR.md)
- [Glyph alphabet](GLYPH-ALPHABET.md)
- [Encoding profile](ENCODING.md)
- [Filesystem contract](FILESYSTEM.md)
- [Compiler roadmap](COMPILER-ROADMAP.md)
- [Local quickstart](QUICKSTART.md)
- [Reference codec](reference/og_codec.py)
- [Unit tests](tests/test_og_codec.py)
- [Examples](examples/)

## Quick start

From the repository root:

```bash
python3 -m unittest discover -s language/og/tests -v
python3 language/og/reference/og_codec.py encode 00007fff
python3 language/og/reference/og_codec.py decode OG/0:00007fff
```

The CLI accepts hexadecimal byte input. This keeps the v0 prototype independent of arbitrary source-code parsing.

## Encoding model

The codec uses a base-5 vowel alphabet for each byte's numeric value, with a fixed consonant prefix in the human-readable glyph profile. The byte sequence length is stored explicitly. A byte with value zero is represented explicitly and cannot disappear.

For a byte value, each base-5 digit is mapped to a syllable:
- 0 → `ba`
- 1 → `be`
- 2 → `bi`
- 3 → `bo`
- 4 → `bu`

A byte is represented by a fixed-width sequence of four base-5 digits (because 5^4 = 625, covering 0..255). Each byte is therefore four syllables. Separators make byte boundaries visible.

Example: byte 1 becomes `ba-ba-ba-be` (digits 0001 in base 5, most significant first). This is a notation only; it does not make the payload positive or change its value.

## Scope boundaries

The current codec is a data representation utility. It does not:
- parse Kotlin, C++, Python, Java, or shell;
- remove or replace native application sources;
- claim to make code more efficient;
- prove semantic equivalence of arbitrary programs;
- execute, deploy, or transmit generated artifacts.

See the parent specification and Runflow protocol before any expanded compiler work.
