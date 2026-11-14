# ERIA Resonance and acquisition storage

- `inbox/`: operator-selected files eligible for acquisition scans.
- `acquisitions/index.jsonl`: append-only acquisition records with source SHA-256, source path, capture time, approval reference, and transformation lineage.
- `compiled/` and `manifests/`: Æị derived inspection snapshots and their manifests.
- `settings.json`: Resonance Console policy.

Resonance mode is `both` (scientific and musical translation). The requested
777% value is metadata only; it is never an audio gain. Actual synthesized
playback is capped at 50% peak amplitude. Tone synthesis creates a WAV payload;
it does not itself play audio or select an output device. Playback must be
initiated by an explicit local user action.

Automatic acquisition is requested but disabled by default. It is not a
background watcher. A scan requires a verified exact-scope approval for
`storage/inbox/`. Only UTF-8 CSV, JSON, and TXT files are currently eligible.
Unsupported inputs are marked HOLD. SHA-256 identifies duplicates. Source
files are never moved, rewritten, or deleted.

All acquired and derived data remains NON_AUTHORITATIVE. No medical or
biological effect is implied by sonification. No external hardware or network
transmission is enabled.
