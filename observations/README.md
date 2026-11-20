# Artifact Observation Network

This directory records artifacts for future observation, comparison, provenance analysis, and historical continuity. It is intentionally additive and non-destructive.

## Rules
- Source artifacts remain unchanged; observations are appended as new records.
- Preserve original source bytes/locations when accessible. Hash exact bytes; never normalize before hashing.
- A fingerprint proves content identity only. It does not prove authorship, consent, approval, or authority.
- Assistant-generated output, imported files, generated artifacts, and user-approved decisions must be separately attributed.
- Unknown values stay unknown; conflicting observations are retained and linked.
- Read-only by default. This folder does not grant repository write access or authorize execution.
- Any future consequential change requires a separately verified, independent authorization artifact bound to exact scope and content.

See the schema, policy, registry, events, integrity, and watch documents in this folder.
