# Ɣơ (Yoro) — Worked Examples

**Specification:** [SPEC.md](SPEC.md)  
**Version:** 0.1

These examples illustrate the required behavior. The exact glyph tokens must match the version 0.1 glyph table and reference codec in the repository.

## 1. Empty input

Input bytes: *(empty)*

```text
Ɣơ/0.1
kind:BYTES
length:0
payload:
```

Decoding this envelope returns an empty byte sequence.

## 2. A zero byte

Input bytes: `00`

The encoded payload MUST contain the explicit token assigned to byte value zero. It MUST NOT be represented as an empty payload.

## 3. Leading zero bytes

Input bytes: `00 00 01`

The encoded envelope declares a length of `3`. Decoding MUST return exactly three bytes, preserving both leading zero bytes.

## 4. Byte sequence

Input bytes: `00 01 FF`

A conforming encoder produces three byte tokens in the same order and declares length `3`. A conforming decoder reconstructs exactly `00 01 FF`.

## 5. Round-trip test

```python
original = bytes([0x00, 0x01, 0xFF])
encoded = encode(original)
restored = decode(encoded)
assert restored == original
```

The example is conceptual pseudocode; use the repository reference codec for executable tests.
