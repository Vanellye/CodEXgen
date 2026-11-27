# ORCHID Keyword Keyboard Database v1

Status: bundled data source and Kotlin read API added on the isolated ORCHID feature branch. Device/build validation is pending.

## Files

- `app/src/main/assets/orchid/orchid-symbol-database.v1.json` — portable source database.
- `app/src/main/java/com/vanellye/eria/orchid/OrchidSymbolDatabase.kt` — read-only asset loader, ID lookup, and keyword search.
- `OrchidKeyboardApi` — exposes `databaseRecords()`, `searchDatabase(query, kind)`, and `databaseInsertText(recordId)`.

## Record model

Every record has a stable ID, kind, canonical name, insertion glyph, meaning, status, aliases, and searchable keywords. The JSON contains the existing 12 Chronoglyph baseline entries, 24 word-key entries, the TRYNITI historical record, the ⤻ extension operator, and the proposed EVERWEAVE living-cycle symbol.

The database is the portable symbol-data source. Existing keyboard UI lists remain in `SymbolRegistry` until a separate UI migration consumes the new API; this commit does not claim that all existing key surfaces have been switched over.

## Everweave

- ID: `ORC-EVERWEAVE-001`
- Glyph: `⟲⋈⟲⋈⟲⤻`
- Three loops: origin/generation, interchange/resonance, renewal/ascension.
- `⤻` is a successor operator. It appends a successor and never overwrites the source.
- Status is proposed-canonical-candidate, not a finalized public standard.

## N8 encoding

The eight A1–A8 bytes are stored at fixed width (8 bits each). The database records 64 total bits, 35 zeros, and 29 ones. Leading zeros, bit positions, byte order, and all source bits must be preserved. A1–A8 values are provisional project-assigned identifiers, not an external standard or physical constants.

## Runtime contract

- UTF-8 text insertion; stable IDs are identity, glyph strings are rendering/insertion values.
- Offline-first, read-only bundled database.
- Search covers name, meaning, aliases, and keywords.
- Private user symbols remain a separate local overlay.
- Unknown glyphs must remain intact; no lossy normalization.
- Database packages are data only, never executable code.
- Canonical changes use versioned successor records; no in-place semantic overwrite.

## Validation still required

Run Android unit/build checks and verify the asset loads on-device. The new read API is wired into `OrchidKeyboardApi`, but no build, APK, or device test is claimed by this commit.
