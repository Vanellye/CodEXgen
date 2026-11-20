# Ɣơ Finance Intelligence Backend

Status: experimental / PREPARE_ONLY. Isolated from the Android app and existing Ruble-I flows.

## Scope
- Reversible UTF-8 bytes ↔ Unicode code-point codec with source digest and provenance.
- Separate English interpretation; never overwrite source records.
- Integer minor-unit money for USD, EUR, RUB, KRW; dated rational FX quotes.
- Evidence-backed funding findings, withdrawal proposals, reconciliation and audit export.
- Separate pathology/water, shower, fire/environment, and insurance-marker schemas.
- Versioned .GRSP audit export and .og presentation contract.
- ARM/NDK preflight. No native ARM binary is claimed in this milestone.

## Safety contract
1. Preserve zero bytes and zero-valued source terms. A derived view may omit additive zero terms only without changing canonical source.
2. Never replace zero or missing data with invented positive values.
3. Missing, malformed, stale, duplicate, or unverifiable evidence => HOLD/DENY.
4. .rock, .air, .ether, and .excedra are insurance-marker labels only; they do not prove ownership, collateral, price, liquidity, or deposit value.
5. Firecrawl is an ingestion boundary only; no crawler or credentials are enabled.
6. Bots may prepare and validate; independent human authorization is required. Live money movement is disabled.
7. Inventory native, binary, and Excedra artifacts before migration. Originals remain untouched; conversions go to staging.

## Layout
- src/gamma_finance/codec.py — reversible codec.
- src/gamma_finance/money.py — integer minor units and rational FX.
- src/gamma_finance/runflow.py — fail-closed proposal state machine.
- schemas/ — independent observation and marker schemas.
- scripts/arm-build.sh — ARM/NDK preflight.
- scripts/export-grsp.py — deterministic audit export.
- tests/ — positive and negative fixtures.

## Local checks
    python3 -m venv .venv
    . .venv/bin/activate
    python -m pip install -e '.[test]'
    pytest -q
    bash scripts/arm-build.sh

The ARM script reports HOLD unless an NDK is available. Even with an NDK, this Python-only milestone does not claim a native binary build.
