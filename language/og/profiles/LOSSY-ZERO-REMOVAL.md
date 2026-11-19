# Ɣơ/L1 — Lossy Zero-Removal Profile

Status: experimental and intentionally non-reversible.

- Prefix: `Ɣơ/L1:`
- Zero bits are omitted.
- One bits are represented by `k`.
- A period separates source-byte groups; an empty group means that source byte contained zero one-bits.
- The count of one-bits remains visible, but their original positions are lost.

Example: byte `0x41` (`01000001`) becomes `kk`.

**There is no decoder.** This profile cannot reconstruct the original bytes. Do not use it for source code, credentials, keys, financial records, backups, signatures, or any data requiring integrity. The profile must be labelled lossy in every UI and export.

Implementation: `language/og/reference/star_lossy.py`.
