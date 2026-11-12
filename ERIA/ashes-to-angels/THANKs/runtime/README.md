# THANKs simulated runtime

This directory contains a local-only actuator simulator and shell acceptance tests.

## Trigger override policy

`TRIGGER_OVERRIDE=ON` is the fixed policy; there is no OFF switch. It allows a manually authorized trigger path when automatic detection is unavailable or fails. It does not convert a detected trigger into permission.

For `--trigger manual`, supply both:
- `--manual-trigger-approval-id ID`
- `--manual-trigger-reason TEXT`

The manual-trigger authorization is additional to, not a replacement for, the Pheônix authorization gate and the Sure-rarity evidence gate. Both independent gates remain mandatory. An environment variable such as `TRIGGER_OVERRIDE=OFF` cannot change the fixed policy.

## Run: automatic detection path

```bash
bash ERIA/ashes-to-angels/THANKs/runtime/thanks-actuator.sh --simulate --trigger detected \
  --approval-id approval-test-001 --actor local-reviewer \
  --scope THANKs:simulated-motion:execute \
  --evidence-status SUPPORTED --evidence-id evidence-test-001 \
  --independent yes --reproducible yes \
  --requested-speed 1.5 --max-speed 2.0
```

## Run: manually authorized trigger path

```bash
bash ERIA/ashes-to-angels/THANKs/runtime/thanks-actuator.sh --simulate --trigger manual \
  --manual-trigger-approval-id manual-approval-001 \
  --manual-trigger-reason "automatic detector unavailable" \
  --approval-id approval-test-001 --actor local-reviewer \
  --scope THANKs:simulated-motion:execute \
  --evidence-status SUPPORTED --evidence-id evidence-test-001 \
  --independent yes --reproducible yes \
  --requested-speed 1.5 --max-speed 2.0
```

## Tests

```bash
bash ERIA/ashes-to-angels/THANKs/tests/test-thanks-actuator.sh
```

## Safety and trust boundary

- Pheônix authorization and Sure-rarity evidence are separate gates; both must pass.
- Manual trigger authorization is a third, additional requirement for the override path.
- Trigger detection alone never authorizes execution.
- The simulator emits a virtual command record only. It has no hardware driver, network client, webhook, external dispatch, or physical actuator.
- CLI authorization/evidence values are test fixtures, not cryptographic identity, signed authorization, or production security. A production authorization provider and independently verified evidence store must replace these inputs before any non-simulated integration.
- The simulator validates a speed ceiling and rejects an active emergency stop; it does not implement a physical fail-safe.
- Physical deployment is outside this implementation and would require target-specific hazard analysis, independent hardware interlocks, validated limits, and review.

No main-branch change, merge, force-push, or external action is performed by this runtime.
