# THANKs simulated runtime

This directory contains a runnable, local-only actuator simulator and shell acceptance tests.

## Run

From the repository root:

```bash
bash ERIA/ashes-to-angels/THANKs/runtime/thanks-actuator.sh --simulate --trigger detected \
  --approval-id approval-test-001 --actor local-reviewer \
  --scope THANKs:simulated-motion:execute \
  --evidence-status SUPPORTED --evidence-id evidence-test-001 \
  --independent yes --reproducible yes \
  --requested-speed 1.5 --max-speed 2.0
```

Run tests:

```bash
bash ERIA/ashes-to-angels/THANKs/tests/test-thanks-actuator.sh
```

## Safety and trust boundary

- The **Pheônix authorization gate** and **Sure-rarity evidence gate** are evaluated separately; both must pass.
- Trigger detection is not permission to execute.
- The simulator emits a virtual command record only. It has no hardware driver, network client, webhook, external dispatch, or physical actuator.
- The command-line approval/evidence fields are test fixtures, **not cryptographic identity, signed authorization, or production security**. A production authorization provider and independently verified evidence store must replace these inputs before any non-simulated integration.
- The simulator has a configured speed ceiling and an emergency-stop rejection path.
- This code does not implement a physical fail-safe. Physical deployment requires a target-specific hazard analysis, independent hardware interlocks, validated limits, and review.

No main-branch change, merge, force-push, or external action is performed by this runtime.
