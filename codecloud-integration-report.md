# îïịþŧţ Codecloud integration staging

## Target
- Repository: `vanellyetm-ux/Ash`
- Base: `main`
- Isolated branch created: `feature/codecloud`
- Production deployment: not requested and not performed

## Imported components
- Mockingbird: Kotlin prompt-drafting core and Cloudflare Worker; outputs are explicitly synthetic and non-authorizing.
- Pantheon `ctypes` bridge: proposal-only adapter for external C99 NEW/FaCADE source files; those C files are not in the archive.
- ERIA Recovery Manager: dry-run-by-default quarantine/restore utility; purge is blocked.
- PONS Issuer and Signature Verifier: separated under distinct paths because each has a `pons_verifier` Python package; both are non-production references.
- ERIA Finance: Go and .NET IBAN-format/checksum services; no banking connection or payment execution.
- ERIA Forge Agent: plan-only Go agent; no repository write, merge, deployment, or payment capability.
- AIR GenUI renderer: isolated vendor distribution; all 59 files declared by its internal bundle manifest match the recorded size and SHA-256. It is not wired into the dashboard yet.

## Deliberately excluded from application source
- Duplicate copies of PONS Issuer and PONS Signature Verifier (same archive SHA-256 as their counterparts).
- Python `__pycache__` and `.pyc` files.
- The precompiled `go/eria-finance` executable; it is not in the archive's source checksum manifest and is not needed to build from source.
- The demo issuer private-key fixture from PONS Signature Verifier. The public demo trust and demo approval fixtures remain; they do not authorize real actions.

## Validation findings
- All 10 uploaded ZIP archive files passed `ZipFile.testzip()`; they represent 8 unique payloads. See `provenance/zip-archives.json` for exact duplicate groups and archive counts.
- PONS Issuer smoke tests: pass (2 tests).
- PONS Signature Verifier tests: pass (2 tests), only the demo TEST_ONLY fixture.
- Finance Go tests: pass.
- Forge Agent Go tests: pass.
- Mockingbird Kotlin source compiles with the available local Kotlin compiler.
- Recovery Manager and Pantheon bridge Python modules pass syntax compilation.
- Pantheon native integration tests cannot run because the required existing `NEW.c`, `FaCADE.c`, headers, and compiled shared library are not included.
- .NET tests were not run because the .NET SDK is not installed in this environment.
- Cloudflare Worker typecheck was not run because the ZIP has no lockfile and the Cloudflare type package is not installed in this environment.
- The Finance archive's internal `SHA256SUMS.json` disagrees with six of its 13 listed files. The per-file comparison is preserved in `provenance/finance-source-checksums.json`; do not rely on that manifest as a clean attestation.
- The Forge Agent workflow in its source ZIP had a malformed `ame:` key; the staging copy was corrected to `name:`. Its original file hash remains in the ZIP archive provenance record. The integrated CI workflow uses read-only GitHub permissions and has no deployment or repository-write steps.

## Write boundary
The `feature/codecloud` branch was created from `main` and its README blob matches the base branch at branch creation; branch existence was rechecked after creation. No code commits were pushed. The imported PONS tooling cannot authorize writes to this repository as configured. A correctly scoped, independently trusted PONS approval bound to the final tree digest and an explicit review is required before committing this staged tree. Main remains untouched; nothing was deployed.
