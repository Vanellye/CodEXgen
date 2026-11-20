# Native / source / binary / Excedra migration inventory

Status: NOT YET INVENTORIED. No existing native source, binary, or Excedra artifact has been changed by this module.

## Required inventory record
- repository path and object/blob digest
- detected format and version (or UNKNOWN)
- file size and executable bit
- source language/toolchain and target architecture, when evidenced
- provenance: commit, branch, author metadata where available
- dependency and licensing notes
- proposed conversion and expected semantic preservation
- test fixture and round-trip or equivalence evidence
- reviewer and approval reference

## Migration protocol
1. Enumerate files without modifying them.
2. Hash and classify; unknown formats remain UNKNOWN.
3. Preserve originals and source-control history.
4. Convert only to a separate staging directory.
5. Compare behavior with golden fixtures and independent review.
6. Promote by reviewable PR only; no bulk replacement or deletion.
7. Record rejected, superseded, and trashed candidates as tombstone metadata rather than erasing provenance.

No "Excedra" parser or binary converter is assumed to exist until an actual format specification and fixtures are supplied.
