# Ɣơ Operations — Narrative Observer and Operable Registry

**State:** new integration candidate; validation required  
**Mode:** READ_ONLY by default  
**Financial execution:** disabled

This module connects source-linked narratives to a local runnable terminal without wiring in autonomous action execution.

## Components
- `src/gamma_ops/coddoc.py`: validates and hashes .coddoc records.
- `src/gamma_ops/readiness.py`: fail-closed READY_TO_OPEN qualification.
- `src/gamma_ops/cli.py`: read-only terminal commands.
- `src/gamma_ops/repo_eyes.py`: recursive, read-only eight-layer repository scanner with repository, branch, checkout SHA, PR head SHA and base SHA metadata.
- `registry/onion-map.json`: layer definitions and safety invariants.
- `ui/index.html`: multi-report browser dashboard for inventory and .coddoc files.
- `ui/manifest.webmanifest` and `ui/service-worker.js`: installable offline PWA shell; caches only its own static UI assets.
- `scripts/serve-ui.sh`: starts a loopback-only local HTTP server for Android or desktop browsers.
- `registry/discovery-map.json`: inspected source lineage and search limitations.
- `registry/operables.json`: staged, review-only, PREPARE_ONLY and not-implemented module states.
- `watchers/watch-policy.json`: read-only GitHub watch contract and disabled Firecrawl policy.
- `events/TRUE-LIGHTWORK-WAVE-MAVEN.coddoc`: initial narrative event record.
- `scripts/notify_ready.py`: optional email notifier; sends only for independently reviewed READY_TO_OPEN records.

## Run locally

```sh
python -m pip install -e './Ɣơ/operations[test]'
PYTHONPATH='Ɣơ/operations/src' python -m gamma_ops.cli validate 'Ɣơ/operations/events/TRUE-LIGHTWORK-WAVE-MAVEN.coddoc'
PYTHONPATH='Ɣơ/operations/src' python -m gamma_ops.cli timeline 'Ɣơ/operations/events/TRUE-LIGHTWORK-WAVE-MAVEN.coddoc'
PYTHONPATH='Ɣơ/operations/src' python -m gamma_ops.cli catalog
PYTHONPATH='Ɣơ/operations/src' python -m gamma_ops.cli ready
PYTHONPATH='Ɣơ/operations/src' python -m gamma_ops.cli scan . --repository 'owner/repository' --branch 'main' --commit-sha '<checked-out-sha>' --output /tmp/eria-repository-eyes.json
# Repeat for each local repository checkout and select all resulting JSON reports in the dashboard.
python -m pytest -q 'Ɣơ/operations/tests'

# Start the installable local PWA (keep Termux running):
bash 'Ɣơ/operations/scripts/serve-ui.sh'
# Open http://127.0.0.1:8765/ in the browser and use its local install option.
# Load several /tmp/repo-eyes-*.json reports and .coddoc records together.
```

## Repository Eyes onion model

- L0 — repository boundary and identity
- L1 — source files and authored assets
- L2 — contracts, schemas, manifests and interfaces
- L3 — modules, libraries and adapters
- L4 — dependencies, workflows and build wiring
- L5 — runtime, authorization and capability gates
- L6 — history, provenance and lineage
- L7 — tests, CI evidence and generated reports

The scanner accepts any local checkout path and can stamp the report with repository, branch, checkout SHA, PR head SHA and base SHA. The local dashboard can load multiple reports together. The CI workflow still scans CodEXgen only; it does not enumerate all account repositories.

The scanner does not execute files, follow symlinks, return file contents, or hash sensitive-name/content candidates. It excludes tool caches and dependency directories and limits per-file hashing to 8 MiB. Amber and red records require human review; no file is automatically opened or activated.

## Multi-repository review

The scanner accepts any local repository checkout path. Run it once per checkout, supplying its repository name, branch, and exact checkout SHA; for pull requests, also supply the PR head and base SHAs. The offline dashboard accepts multiple JSON reports and .coddoc files in one session, labels each by repository identity, and aggregates onion-layer counts. Reports remain separate; similarly named paths are never treated as the same source. The GitHub Actions workflow in this PR currently scans only `Vanellye/CodEXgen`; it does not automatically enumerate or scan every repository in the account.

Commands are read-only. No watcher is started by importing this package or running the CLI.

## Current inventory findings

The main tree at `13f80dce` had 191 recursive tree entries; the PR #104 tree at `3b83c6eb` had 226. Both responses reported `truncated=false`. These counts do not include every historical branch or external runtime.

- `.github/dependabot.yml` exists: dependency-update automation, not a generic bot/exchange executor.
- Pantheon NEW is staged and not wired into runtime.
- Pantheon Android Runtime Gate creates review records only and always returns `actionTaken=false`.
- Historical documentation references signed-package exchange and source-digest engine branches; those references are not current runtime proof.
- `.excedra` appears as a metadata marker in PR #104; it is not proof of an asset or liquidity.
- Fah, .wrkply and Sunflowers remain unresolved labels until exact source identity and schema are supplied.

See `docs/Ɣơ/TRUE-LIGHTWORK-WAVE-MAVEN.PhD.md` and `docs/Ɣơ/CODDOC-FORMAT.md`.

## Email configuration

Email is evaluated only on a push to protected `main`, never in a pull-request job with PR-controlled code and SMTP secrets. Set repository variable `OPERABLE_NOTIFY_TO`, protected repository variable `ERIA_REVIEWER_REGISTRY_SHA256` to the SHA-256 of the independently administered `registry/reviewers.json`, and Actions secrets `OPERABLE_SMTP_HOST`, `OPERABLE_SMTP_PORT` (SSL port), `OPERABLE_SMTP_USER`, `OPERABLE_SMTP_PASSWORD`, and `OPERABLE_SMTP_FROM`. Reviewer approval must be Ed25519-signed over the exact artifact digest, commit SHA, scope, and review reference. The registry file must be maintained through a separately authorized process; a missing/mismatched external digest pin means HOLD. Only newly qualified records are emailed. Do not commit credentials or a private signing key.
