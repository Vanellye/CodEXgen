# Existing repository codec baseline inspected

Read-only inspection was performed against `Vanellye/CodEXgen`, branch `feature/yoro-adapters-grammar-parser` (baseline SHA recorded in the working context: `93f4ef96efd36fc89a748b50d7cc8c69ec71a6a4`). No repository writes were made.

Existing adapter sources inspected:

- `language/og/javascript/yoro-star-codec.mjs`
- `language/og/python/yoro_star_codec.py`
- `language/og/kotlin/YoroStarCodec.kt`
- `language/og/fixtures/byte-vectors.json`
- `language/og/test-vectors/yoro-star-v2.tsv`

The three language adapters implement the same `Ɣơ/2:` profile: each byte becomes eight symbols, `☆` for bit zero and `k` for bit one, with `.` separating byte groups. Empty input is exactly `Ɣơ/2:`. The original repository fixture has eight vectors and is included as `test-vectors/yoro-star-v2.tsv` for direct compatibility tests.

The new local PANTHEON adapters implement this existing profile alongside the base-5 and nibble-pair profiles, and test all three languages against the expanded shared TSV. The custom one-token-per-zero exchange representation remains a separate profile and is not confused with `Ɣơ/2:`.
