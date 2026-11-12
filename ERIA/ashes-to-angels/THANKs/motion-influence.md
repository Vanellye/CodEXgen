# THANKs — Motion Influence

**Status:** local simulated runtime implemented; physical actuation remains disabled.

## Intent

Preserve the exact name **THANKs** for a bounded motion-influence mechanism. The current runtime target is a virtual motion endpoint only; no physical target is assumed.

## Executable simulation

- Runtime: `runtime/thanks-actuator.sh`
- Acceptance tests: `tests/test-thanks-actuator.sh`
- Run instructions and trust boundary: `runtime/README.md`

The simulator requires explicit simulation mode, a detected trigger, an exact Pheônix authorization scope, independently qualifying Sure-rarity evidence, and a requested speed within the configured ceiling. It emits a virtual command record only.

## Independent gates

1. **Pheônix authorization:** requires an approval ID, actor ID, and exact scope `THANKs:simulated-motion:execute`.
2. **Sure-rarity evidence:** requires `SUPPORTED`, an evidence ID, independent support, and reproducibility.

Neither gate can satisfy or override the other. Missing or invalid data blocks execution. Trigger detection alone never executes an action.

## Motion bounds and stop

The simulator validates non-negative decimal speed values and enforces the supplied maximum. An emergency-stop request blocks the command. It does not claim physical emergency-stop capability.

## Trust boundary

CLI authorization/evidence values are test fixtures, not secure credentials or independently verified attestations. There is no network dispatch, webhook, hardware driver, hidden execution, or physical movement. Production integration requires a trusted authorization verifier, evidence verifier, target-specific engineering limits, and independent physical safety interlocks.

## Acceptance tests

Run `bash ERIA/ashes-to-angels/THANKs/tests/test-thanks-actuator.sh`. Tests cover success in simulation, each independent gate, trigger-only denial, speed-limit rejection, and emergency-stop rejection.
