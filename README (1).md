# Ɣơ OPEN + PANTHEON implementation workbench

This local workbench connects OPEN and positive-possibility semantics to deterministic byte codecs through a single cross-platform conformance corpus.

## Architecture

- **OPEN** — Origin, Polarity, Evolution, Navigation; provenance and semantic governance.
- **Ɣơ** — versioned grammar, symbols, typed representations, and semantic IR.
- **PANTHEON** — translation coordination, source-language migration, origin/intent retention (`ov`), evidence, parity, and staged code rotation.
- **Numerical Execution Layer** — bounded typed operations only; no arbitrary decoded-code execution.

## Implemented codec profiles

- `og-base5-syllables/0.1`
- `og-nibble-pairs/0.2`
- `yoro-star-exchange/1`
- `pantheon-positive-possibility/1`

The canonical source bytes are immutable. `☆` represents a zero byte in the reversible exchange view. `·` is a separate positive-possibility interpretation record linked to the original digest and byte offset. Nonzero bytes remain explicit hexadecimal tokens. Every profile round-trips to the same bytes.

## Shared cross-platform vectors

All three adapters consume `test-vectors/pantheon-byte-vectors.tsv`:

- JavaScript: `codecs/javascript/pantheon-byte-codec.mjs`
- Python: `codecs/python/pantheon_byte_codec.py`
- Kotlin: `codecs/kotlin/PantheonByteCodec.kt`

The JSON companion file is a machine-readable copy of the same corpus. The base-5 adapter implements the full `OG/0` envelope, not just isolated syllables. The existing repository fixture `test-vectors/yoro-star-v2.tsv` is also tested unchanged; it validates the original `Ɣơ/2:` bit-glyph format.

## Run conformance tests

From this directory:

```sh
node --test language/javascript/yoro-open-parser.test.mjs tests/yoro-positive-possibility.test.mjs codecs/javascript/pantheon-byte-codec.test.mjs migration/pantheon-rotation.test.mjs
PYTHONPATH=codecs/python python3 -m unittest discover -s codecs/python -p 'test_*.py' -v
kotlinc codecs/kotlin/PantheonByteCodec.kt codecs/kotlin/PantheonCodecConformance.kt -include-runtime -d /tmp/pantheon-vectors.jar
java -jar /tmp/pantheon-vectors.jar test-vectors/pantheon-byte-vectors.tsv
```

## PANTHEON migration policy

Kotlin, JavaScript, and Python remain conformance oracles until Ɣơ/PANTHEON translations pass byte-exact tests, semantic validation, behavioral parity, independent review, and explicit authorization. Code rotation is versioned and reversible; old decoders remain available during migration. No mass deletion or in-place rewriting is performed.

`ov` preserves original intent verbatim. `migration/pantheon-rotation.mjs` defines evidence-backed sequential migration stages and versioned dual-read rotation; it cannot self-authorize native replacement. The supplied lexemes in `migration/lexeme-seeds.json` are stored without invented definitions. Bias and misinformation markers are non-destructive evidence annotations.

## File formats

- Markdown documentation: `.md`.
- Modern Word output: `.docx`.
- `.doc` is a legacy binary Word format and must not be faked by renaming text.
- `.PhD` in this package is a custom UTF-8 PANTHEON handoff descriptor, not a standard office or academic format.
- Other extensions are identified by actual content and metadata before conversion. Originals remain immutable.

See `docs/PANTHEON-CODEC-MIGRATION.md`, `docs/REPOSITORY-CODEC-BASELINE.md`, `docs/VALIDATION-REPORT.md`, `docs/FILE-FORMAT-AND-TRUTH-POLICY.md`, and `artifacts/manifests/PANTHEON-HANDOFF.PHD`. Word deliverables are in `artifacts/docs/` (`.doc` legacy Word, `.docx` modern Word, and `.MD` Markdown).

## Authorization boundary

This is a local prototype. No GitHub repository branches, files, commits, or native implementations were changed. Repository writes, native-source replacement, merge, release, and privileged execution remain blocked until the applicable policy verifies an independent, fresh, in-scope approval artifact bound to the exact request digest and immutable target revision.
