# Ɣơ Operations — Narrative Observer and Operable Registry

**State:** new integration candidate; validation required  
**Mode:** READ_ONLY by default  
**Financial execution:** disabled

This module connects source-linked narratives to a local runnable terminal without wiring in autonomous action execution.

## Components
- `src/gamma_ops/coddoc.py`: validates and hashes .coddoc records.
- `src/gamma_ops/readiness.py`: fail-closed READY_TO_OPEN qualification.
- `src/gamma_ops/cli.py`: read-only terminal commands.
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
python -m pytest -q 'Ɣơ/operations/tests'
```

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

Set repository variable `OPERABLE_NOTIFY_TO` and Actions secrets `OPERABLE_SMTP_HOST`, `OPERABLE_SMTP_PORT`, `OPERABLE_SMTP_USER`, `OPERABLE_SMTP_PASSWORD`, and `OPERABLE_SMTP_FROM`. The workflow will skip mail when no operable is READY_TO_OPEN or when configuration is missing. Do not commit credentials.
