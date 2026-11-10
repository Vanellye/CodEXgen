# Legacy Python syntax quarantine

## Decision

The file `hypotheticals/bio_resonance_fiction.py` is preserved as historical fictional source and excluded from automated Python syntax compilation. This is quarantine, not a semantic repair.

## Exact preserved artifact

- Path: `hypotheticals/bio_resonance_fiction.py`
- Git blob SHA-1: `2d689a275e0a2bf39a1c1fa14afe3d84fb5589c2`
- Baseline commit: `b76f107ce29a44cf8afa9626e05047de44a6fbe4`
- The source itself states that it is fictional, does not interact with biological systems, and is kept off `main` on purpose.

CI checks the file's Git blob hash before excluding exactly this path from Python compilation. If its bytes change, the workflow fails and requires review. All other discovered Python files remain in the syntax compilation pass.

## Recorded parse blockers

The preserved source contains these malformed expressions:

- `range(ơ, 16, 2)`
- `int(level * 2ơ)`
- `level * 1ọ / 9`

No replacement values or intended semantics are inferred.

## Boundaries

- The original source is not edited, renamed, deleted, imported, or executed by this change.
- The CI exclusion applies only to syntax compilation; it does not certify the quarantined module as valid or safe to run.
- The rest of the Python source tree remains subject to syntax validation.
- A future repair requires author-confirmed intent or other explicit evidence, a separate reviewed patch, and focused tests.
- The pinned hash deliberately makes any change to the quarantined source visible rather than silently accepting it.

A passing syntax job means the non-quarantined Python files compile and the quarantined artifact is unchanged. It does not mean the quarantined module compiles or that its intended behavior is known.
