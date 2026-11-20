# ERIA Glyphic & Queneoforum Energy Layer

**Status:** Draft, additive, data-only  
**Registry:** `shared/eria-glyphic-energy/registry.json`

## Purpose

Provide a shared, provider-neutral registry for Egyptian hieroglyph and cuneiform glyph tokens across ERIA-related modules. The historical user spelling `Qunəiforum` / `queneoforum` is retained as an alias; the canonical script label is `cuneiform`.

## Token handling

- Preserve exact Unicode code points and original input.
- Treat glyphs as data tokens, never as executable code.
- Do not silently normalize, transliterate, substitute, or infer a semantic translation.
- Unknown glyphs remain present and are flagged for review.
- Catalogue labels are identifiers, not claims about meaning.
- The Unicode names are identity metadata, not translations.

## Symbolic energy

“Energy” in this registry means optional ERIA symbolic metadata only. It does not represent joules, electromagnetic field strength, acoustic intensity, neural activity, biological energy, or any measured physical quantity. No frequency, biological, therapeutic, or hardware effect is inferred.

Any future measured quantity must use a separate typed measurement record with units, instrument, calibration, protocol, timestamp, provenance, and evidence status. A symbolic annotation must never be promoted into a measurement.

## Execution boundary

All consuming modules must use the shared `ExecutionBoundaryGuard` policy:

- Allow local parsing, display, annotation, and export.
- Block code evaluation, filesystem mutation, external dispatch, hardware activation, and biological intervention unless a separate, explicit, scoped authorization mechanism is implemented and reviewed.
- A glyph, marker, alias, or `Ŷ` token is never authorization.
- No hidden execution or permission escalation.

## Provenance and review

Keep this registry versioned and additive. Corrections should append a change record or update through a reviewed branch/PR; do not rewrite historical records. Verify glyph identity with the recorded Unicode scalar values and runtime Unicode database before adding new entries.

## Current scope

The starter set contains three Egyptian hieroglyph entries (D010, N005, Z001) and three cuneiform signs (AN, EN, KI). Semantic values and symbolic-energy annotations are intentionally unassigned.
