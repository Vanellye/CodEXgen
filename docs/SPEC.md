# Ɣơ (Yoro) — Encoding Specification

**Version:** 0.1  
**Status:** Draft  
**Suggested extension:** `.og`

## 1. Purpose and scope

Ɣơ (Yoro) is an experimental, reversible notation for representing arbitrary bytes with vowel-and-consonant symbols. This specification defines a byte encoding format only. It does not define a programming language compiler, translate program semantics, or make encoded content executable.

## 2. Design requirements

A conforming version 0.1 encoder and decoder MUST:
- Preserve every input byte, including zero bytes and leading zero bytes.
- Preserve byte order and input length.
- Produce deterministic output for the same input.
- Reject malformed or unsupported envelopes rather than guessing.
- Identify the format version explicitly.

## 3. Envelope

A version 0.1 document uses this logical envelope:

```text
Ɣơ/0.1
kind:BYTES
length:<decimal-byte-count>
payload:<encoded-byte-tokens-or-empty>
```

The exact token alphabet and byte mapping are defined by the repository's versioned glyph table and reference codec. Implementations MUST NOT silently substitute a different alphabet or mapping.

An empty byte sequence has length `0` and an empty payload. A zero byte is a real byte and MUST have an explicit token; it is not equivalent to an empty payload.

## 4. Reversibility

For every byte sequence `B`:

```text
decode(encode(B)) = B
```

This equality is the primary conformance condition. Length metadata is measured in bytes, not glyphs or Unicode characters.

## 5. Versioning

Changes that alter tokenization, byte mapping, envelope interpretation, or decoding behavior MUST use a new format version. A decoder MUST reject unknown versions unless it explicitly implements them.

## 6. Non-goals

Version 0.1 does not:
- Parse or compile Kotlin, C++, Python, or other source languages.
- Preserve program meaning through a source-to-source transformation.
- Execute, load, or evaluate encoded payloads.
- Claim that a glyph representation is more efficient than binary or a conventional byte encoding.

## 7. Reference implementation

The repository reference codec is an implementation aid. The specification and test vectors define expected behavior; an implementation is conforming only when it passes the version 0.1 round-trip and malformed-input tests.
