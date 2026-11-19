# Ɣơ (Yoro) — Worked Examples

**Format:** `OG/0`  
**Codec profile:** `og-base5-syllables/0.1`

## 1. Empty input

```text
OG/0
kind:BYTES
length:0
payload:empty
codec:og-base5-syllables/0.1
```

Decoding returns an empty byte sequence.

## 2. One zero byte

```text
OG/0
kind:BYTES
length:1
payload:ba-ba-ba-ba
codec:og-base5-syllables/0.1
```

The zero byte has an explicit token. It is not the same as an empty payload.

## 3. Leading zero bytes

Input bytes: `00 00 01`

```text
OG/0
kind:BYTES
length:3
payload:ba-ba-ba-ba, ba-ba-ba-ba, ba-ba-ba-be
codec:og-base5-syllables/0.1
```

Decoding returns exactly `00 00 01`.

## 4. Mixed byte values

Input bytes: `00 01 FF`

```text
OG/0
kind:BYTES
length:3
payload:ba-ba-ba-ba, ba-ba-ba-be, bi-ba-be-ba
codec:og-base5-syllables/0.1
```

Decoding returns exactly `00 01 FF`.

## 5. Round-trip property

```python
original = bytes([0x00, 0x01, 0xFF])
encoded = encode(original)
restored = decode(encoded)
assert restored == original
```

Use the repository reference codec to run executable tests.
