# Ɣơ/2 — Reversible Star-Bit Profile

Status: experimental draft.

- Prefix: `Ɣơ/2:`
- Bit zero: `☆`
- Bit one: `k`
- Each byte is exactly eight symbols, most-significant bit first.
- A period separates byte groups.
- Empty input is represented by the prefix with an empty payload.
- UTF-8 is used only by the text convenience functions; the core codec accepts arbitrary bytes.

Example: byte `0x41` (binary `01000001`) becomes `☆k☆☆☆☆☆k`.

This profile is reversible: decoding restores the exact input bytes. Reject malformed groups and unknown symbols; never silently repair data.

Implementation: `language/og/reference/star_reversible.py`.
