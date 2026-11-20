# STAR — Steady TAG Algo Rhythm

**Status:** Proposed documentation and data-contract addition
**ASH anchor:** [Vanellye/Ash README](https://github.com/Vanellye/Ash/blob/docs/star-anchor/README.md)
**ERIA implementation:** [STAR C99 registry](../pantheon/NEW/STAR/README.md)

## Definition
**STAR** means **Steady TAG Algo Rhythm**. It names a repeatable software sequence: preserve an input's origin, assign stable identifiers, validate a proposed transformation, preview the result, and record what happened.

"Frequency" and "rhythm" are software metadata or workflow descriptors here. A software value, glyph, generated file, or signal label does not establish a biological or physical effect. No instrument calibration, exposure, or hardware operation is implied.

## Glyphs as code data
STAR's initial registry includes selected Unicode Egyptian hieroglyphs and cuneiform signs. Each entry retains a stable token ID, Unicode script label, Unicode character name, scalar code point, and UTF-8 glyph representation.

| Token ID | Script | Unicode name | Code point | Glyph |
|---|---|---|---|---|
| `EG_D010` | Egyptian hieroglyphs | EGYPTIAN HIEROGLYPH D010 | U+13080 | 𓂀 |
| `EG_N005` | Egyptian hieroglyphs | EGYPTIAN HIEROGLYPH N005 | U+131F3 | 𓇳 |
| `EG_Z001` | Egyptian hieroglyphs | EGYPTIAN HIEROGLYPH Z001 | U+133E4 | 𓏤 |
| `CU_AN` | Cuneiform | CUNEIFORM SIGN AN | U+1202D | 𒀭 |
| `CU_EN` | Cuneiform | CUNEIFORM SIGN EN | U+12097 | 𒂗 |
| `CU_KI` | Cuneiform | CUNEIFORM SIGN KI | U+121A0 | 𒆠 |

These are Unicode-coded tokens, not translations or claims about historical meaning. Do not infer a message from appearance.

## Generation of filesystems
Filesystem generation is a separate ERIA workstream documented in [ERIA Filesystem Generation](ERIA-FILESYSTEM-GENERATION.md). Its proposed lifecycle is: describe with a manifest; validate paths and quotas; preview deterministically; obtain explicit approval for the exact target root and plan hash; stage; verify; then publish or recover.

The current STAR module does not create, delete, overwrite, or scan files.

## Governance
- Preserve original inputs and provenance; generated output is a derivative.
- Glyphs are data, never shell, SQL, source code, or executable instructions.
- No implicit permissions, hidden execution, external dispatch, or background mutation.
- Record unknowns and failed validation instead of guessing.
- Require independent review before runtime integration.

## Related work
- [ASH anchor](https://github.com/Vanellye/Ash/blob/docs/star-anchor/README.md)
- [ERIA TeSt Rhythmatic Remedy](../pantheon/NEW/RHYTHMATIC_REMEDY/README.md)
- [STAR C99 registry](../pantheon/NEW/STAR/README.md)
