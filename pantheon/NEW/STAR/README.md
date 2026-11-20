# STAR — Steady TAG Algo Rhythm

**Status:** Proposed, bounded C99 data contract; not wired to a runtime entry point.
**Purpose:** Preserve stable symbolic identifiers and rhythm metadata across ERIA workflows.

"Rhythm" describes an ordered, repeatable software workflow; it does not assert a biological, medical, spiritual, or physical effect.

## Glyph token registry
| Token ID | Script | Unicode name | Code point | Glyph |
|---|---|---|---|---|
| `EG_D010` | Egyptian hieroglyphs | EGYPTIAN HIEROGLYPH D010 | U+13080 | 𓂀 |
| `EG_N005` | Egyptian hieroglyphs | EGYPTIAN HIEROGLYPH N005 | U+131F3 | 𓇳 |
| `EG_Z001` | Egyptian hieroglyphs | EGYPTIAN HIEROGLYPH Z001 | U+133E4 | 𓏤 |
| `CU_AN` | Cuneiform | CUNEIFORM SIGN AN | U+1202D | 𒀭 |
| `CU_EN` | Cuneiform | CUNEIFORM SIGN EN | U+12097 | 𒂗 |
| `CU_KI` | Cuneiform | CUNEIFORM SIGN KI | U+121A0 | 𒆠 |

Entries are Unicode identifiers, not translations or semantic interpretations. Preserve the script label, Unicode name, code point, token ID, and UTF-8 glyph.

## Code boundary
- The C99 registry exposes immutable data and indexed read access only.
- It does not evaluate glyphs, execute embedded text, compile generated source, invoke a shell, load plugins, or dispatch network/hardware actions.
- Treat external glyph strings as data. Never concatenate them into executable source, SQL, shell commands, paths, or templates without context-specific encoding.
- Unknown token IDs remain unknown; do not silently substitute another glyph.

## Filesystem generation
See [ERIA Filesystem Generation](../../../docs/ERIA-FILESYSTEM-GENERATION.md). The proposed generator is plan-first: validate a manifest, produce a preview, and require explicit authorization before any filesystem write. This STAR module itself does not create, delete, overwrite, or scan files.

## Build and test
From this directory:
```sh
cc -std=c99 -Wall -Wextra -Werror -I. STAR.c tests/test_STAR.c -o star-test
./star-test
```

## Related contracts
- [STAR concept and glyph mapping](../../../docs/STAR-STEADY-TAG-ALGO-RHYTHM.md)
- [ERIA Runflow operating protocol](../../../docs/ERIA-RUNFLOW-OPERATING-PROTOCOL.md)
- [TeSt Rhythmatic Remedy](../RHYTHMATIC_REMEDY/README.md)

This contract is additive and staged for independent review. It grants no permissions and does not alter existing runtime behavior.
