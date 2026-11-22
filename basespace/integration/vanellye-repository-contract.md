# Vanellye repository integration contract

## Authority model
- Canonical host: `Vanellye/CodEXgen`.
- Consumers: `Vanellye/Ash` and `Vanellye/CodEXgen-2`.
- CodEXgen owns the canonical schema and registry proposal.
- Ash and CodEXgen-2 consume published, versioned BaseSpace data read-only.
- No consumer may mutate the canonical registry or write back into source archives.

## Repository provenance
Every imported repository item records owner/name, visibility, default branch, immutable commit SHA, path, blob SHA, retrieval timestamp, and repository license/terms. Repository files are not automatically treated as historical primary sources.

## Change workflow
1. Read repository metadata and source files only.
2. Propose consumer manifests on isolated feature branches.
3. Open reviewable pull requests; never push to `main`, merge, force-push, or alter protections automatically.
4. Verify CI, diff, provenance, and access policy before human approval.
5. Keep consumer credentials read-only where technically available.

## Historical source workflow
Catalogue metadata may be indexed from public institutional sources. Content from licensed, permission-required, restricted, or sealed collections is not acquired unless the applicable terms and explicit authorization permit it. No access-control bypass, credential sharing, or impersonation.

## Hashing and revision lineage
SHA-256 is calculated over the exact acquired byte stream, not a URL or a rendered web page. Store digest, byte length, media type, timestamp, acquisition method, source URI, rights, and hash scope. Derived OCR, translations, transcriptions, and interpretations are separate descendants. Never overwrite a prior revision.
