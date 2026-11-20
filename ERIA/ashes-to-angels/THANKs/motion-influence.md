# THANKs — Motion Influence

**Status:** local simulated runtime implemented; physical actuation remains disabled.

## Intent

Preserve the exact name **THANKs** for a bounded motion-influence mechanism. The current runtime target is a virtual motion endpoint only; no physical target is assumed.

## Trigger override

`TRIGGER_OVERRIDE=ON` is the fixed policy. The OFF switch is removed. If automatic trigger detection is unavailable or fails, the runtime accepts a manual trigger only with a separate manual-trigger authorization ID and a non-empty reason. This override substitutes only for trigger detection; it cannot bypass either independent gate.

A detected trigger alone is never permission to execute. A manual trigger is not permission by itself either.

## Independent gates

1. **Pheônix authorization:** requires an approval ID, actor ID, and exact scope `THANKs:simulated-motion:execute`.
2. **Sure-rarity evidence:** requires `SUPPORTED`, an evidence ID, independent support, and reproducibility.
3. **Manual-trigger authorization (override path only):** requires a distinct manual approval ID and reason.

Neither independent gate can satisfy or override the other. Missing or invalid data blocks execution.

## Motion bounds and stop

The simulator validates non-negative decimal speed values and enforces the supplied maximum. An emergency-stop request blocks the command. It does not claim physical emergency-stop capability.

## Trust boundary

CLI authorization/evidence values are test fixtures, not secure credentials or independently verified attestations. There is no network dispatch, webhook, hardware driver, hidden execution, or physical movement. Production integration requires trusted authorization and evidence verifiers, target-specific engineering limits, and independent physical safety interlocks.

## Acceptance tests

Run `bash ERIA/ashes-to-angels/THANKs/tests/test-thanks-actuator.sh`. Tests cover automatic detection, manual override, missing manual authorization, both independent gates, speed-limit rejection, emergency-stop rejection, and resistance to an environment-supplied OFF value.
