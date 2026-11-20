# Ɣơ Encoding Profile — og-base5-syllables/0.1

## Byte encoding

Each input byte is an unsigned integer in the range 0..255.

Convert the byte to exactly four base-5 digits, most-significant digit first. Map each digit to a syllable using the profile table:

`0=ba, 1=be, 2=bi, 3=bo, 4=bu`.

Four base-5 digits cover values 0..624, so all byte values fit.

## Document envelope

```text
OG/0
kind:BYTES
length:3
payload:ba-ba-ba-ba, ba-ba-ba-be, ba-ba-bo-bu
codec:og-base5-syllables/0.1
```

This example is structural. The payload is a comma-separated list of fixed-width byte encodings.

For an empty byte string:

```text
OG/0
kind:BYTES
length:0
payload:empty
codec:og-base5-syllables/0.1
```

## Losslessness

Decoding performs the inverse operation:
1. Validate version, type, length, and codec identifier.
2. Split payload into byte tokens.
3. Require four known syllables per token.
4. Convert the four base-5 digits to an integer.
5. Reject values above 255.
6. Require token count to equal declared length.
7. Emit one byte per token in the original order.

Zero bytes are represented as `ba-ba-ba-ba`. Leading zero bytes remain separate tokens. No zero is dropped or substituted.

## Compression

Compression is not part of v0.1. A future run-length profile may represent repeated bytes with explicit run tokens and lengths. It must be lossless and must be separately versioned. Compression should only be selected if it reduces storage or transport size.

## Security and resource limits

An implementation should impose a documented maximum input size to prevent memory exhaustion. It must reject excessive declared lengths before allocating payload storage. The reference implementation uses a conservative default limit and has no network, filesystem-write, process-launch, or execution behavior.
