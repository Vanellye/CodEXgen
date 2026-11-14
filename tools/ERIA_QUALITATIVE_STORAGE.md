# ERIA Qualitative Storage, Æị and Âï Bridge

## Storage
Qualitative artifacts live outside the Git checkout at `~/.eria/qualitative/`:
- `reports/`: immutable JSON quality-report snapshots
- `proposals/`: approval-ready synthesis/review packets
- `qualitative.sqlite3`: append-only report/finding history, ranked candidates and proposal index

The existing conversation/source SQLite database is not replaced or migrated. The bridge reads
its `pull_files` table, when available, only to compare local and GitHub SHA-256 snapshots.

## Interface
- `GET /api/quality/summary`
- `GET /api/quality/findings?severity=high&path=...`
- `GET /api/quality/candidates`
- `GET /api/quality/inspect?path=repo/relative/file.py` (Æị source preview and fingerprint match)
- `GET /api/quality/proposals`
- `GET /api/quality/proposals`
- `POST /api/quality/refresh` with `{}`
- `POST /api/quality/proposals` with `{"symbol":"..." }`

Æị uses findings, file fingerprints and source provenance to inspect implementation candidates.
Âï receives the same bounded evidence context during quality-related conversations, allowing
explanations of purpose, dependencies, conflicts, security implications and comparisons.
The current repository conversation engine remains the response engine. Âï adds deterministic,
evidence-backed explanations for quality questions and explicitly distinguishes what the static
report proves from what requires deeper call-graph or runtime inspection; it is not represented as
a fully autonomous LLM reasoning service.

## Ranking and approvals
Candidate ranks are heuristic triage only (mean static score, implementation overlap and
severity-weighted findings). They are not correctness or security certifications.
Proposal packets include report identity, branch/commit provenance, file hashes and related
findings. Status remains `REVIEW_REQUIRED`. There is no apply/approve endpoint and no code
write path in this feature. A separate human authorization and reviewed patch workflow is
required before repository changes.

## Run tests
```bash
PYTHONPATH=tools python -m unittest discover -s tests -p "test_eria_quality_bridge.py" -v
```
