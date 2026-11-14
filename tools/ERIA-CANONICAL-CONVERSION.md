# ERIA Canonical Conversion Engine

## Purpose

ERIA uses one canonical envelope between source formats and derived formats. This
keeps format conversion separate from natural-language translation and semantic
interpretation.

## Pipeline

1. Detect the input format and decode the source.
2. Hash and describe the original bytes.
3. Parse into a canonical payload.
4. Render a separate derived file.
5. Write a provenance manifest containing source/output hashes and validation status.

The source is read-only. Existing output paths are rejected rather than overwritten.
The converter does not execute source code, make network calls, or mutate Git.

## Termux use

From the repository root:

```bash
python tools/eria_conversion_engine.py records.json --to csv
python tools/eria_conversion_engine.py records.csv --to json
python tools/eria_conversion_engine.py notes.txt --to json
```

Optional explicit output path:

```bash
python tools/eria_conversion_engine.py records.json --to csv \
  --output "$HOME/storage/shared/ERIA/derived/records.csv"
```

The engine creates a companion file named
`<output-name>.eria-manifest.json`. It refuses to overwrite either output.
Keep derived outputs outside tracked source directories when appropriate.

## Supported formats

Initial adapters support JSON, CSV and plain UTF-8/UTF-16/Windows-1252 text.
Additional codecs can be registered in later versions without changing the
canonical envelope contract.

## Translation is a separate adapter

A file-format conversion is not a translation of meaning. Natural-language
translation must be supplied through a named `TranslationAdapter` implementation
that reports source language, target language, provider and optional confidence.
No translation provider is bundled or implied by this module. If no provider is
configured, ERIA must report translation as not performed rather than fabricate
a translated result.

## Validation semantics

The manifest intentionally distinguishes:
- `format-rendered`: output serialization completed;
- `semantic_accuracy`: not evaluated by the basic converter;
- `information_loss`: not assessed by the basic converter.

A later validator can add schema checks, round-trip comparisons, field-level
diffs and human-reviewed translation quality scores.

The optional 11.11 ratio marker is retained as metadata only. It does not scale
the data, establish correctness, or substitute for semantic validation.

## Tests

From the repository root:

```bash
python -m unittest tests.test_eria_conversion_engine -v
```
