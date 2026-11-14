# ERIA Repository-wide Quality Assessment & Synthesis

## Scope
Run the assessor across the entire checked-out repository, including Kotlin, Java,
C/C++, Python, Bash, web, configuration, SQL, and documentation sources. Files are
fingerprinted with SHA-256 and tied to the observed branch, HEAD commit, and working
tree status. Likely secret files, binary files, caches, generated build directories,
and files larger than 2 MiB are excluded.

## Run
```bash
python tools/eria_quality_mixer.py assess . --output .eria/quality/latest.json
python -m unittest tests.test_eria_quality_mixer -v
```

The report contains static triage scores, rule-based findings, exact duplicate groups,
and shared declaration candidates. Scores are heuristics, not proof of security or
correctness. Candidate overlap is a synthesis queue, not permission to concatenate
or replace source files.

## Code synthesis / approval boundary
- Acquired source is treated as untrusted input and is never executed by this assessor.
- Candidate code is compared by declared symbol and provenance; no source merge occurs.
- Any proposed implementation must be reviewed, tested in an isolated environment, and
  explicitly approved before it is written to repository source paths.
- The workflow has `contents: read` permission and uploads reports as artifacts only.
- Git history, `main`, and SQLite source records are not modified by assessment.

## Audio mixing
```bash
python tools/eria_quality_mixer.py mix-audio --output ./mix.wav track-a.wav track-b.wav
```
Supports uncompressed 16-bit PCM WAV with matching channel count and sample rate.
The mixer averages tracks and applies peak-safe normalization. It writes only to the
explicit output path; it does not overwrite input tracks.

## Automation
The GitHub Actions workflow runs on a six-hour schedule, manual dispatch, and relevant
pushes to the ERIA file-pull feature branch. It performs static assessment and tests,
then uploads a versioned report artifact. No write token or repository-content write
permission is granted to the workflow.
