# ALEPH — Origin Failsafe and Reverse Recovery

**Status:** Implemented as a C++11 host-runtime feature on `feature/aleph-origin-failsafe`; execution and build verification remain pending.

ALEPH (א) is Pantheon's origin-aware recovery coordinator. It preserves a path back through explicitly registered compensating actions and automatically places the runtime into safe hold when an execution fails or is denied.

## Runtime behavior

1. Callers register compensating actions before an operation, in forward dependency order.
2. A failed module result, missing module, or authorization denial automatically engages ALEPH.
3. Safe hold records the first failure reason and blocks further recovery-action registration.
4. Reverse recovery is available only through an authenticated `AlephApproval`.
5. Compensating actions execute in reverse registration order.
6. A failed compensation stops the sequence and records `RECOVERY_INCOMPLETE`; already completed actions remain marked, so a later approved attempt resumes without replaying them.
7. Full completion enters `RECOVERED`.

## Boundaries

- ALEPH does not automatically undo arbitrary module side effects. A caller must register a truthful compensating action before execution.
- Reversal requires owner approval; automatic engagement is not automatic permission to mutate state.
- A compensating action must be idempotent or otherwise safe to retry if it reports failure after a partial effect.
- ALEPH does not reset Git refs, rewrite commit history, merge branches, deploy firmware, or actuate hardware.
- Original records and provenance remain intact. Corrections and recovery outcomes should be appended as new evidence.
- The current coordinator is in-process and host-testable; it is not a durable crash-recovery journal.

## States

| State | Meaning |
|---|---|
| `READY` | Accepting compensating actions |
| `SAFE_HOLD` | Failure observed; await review and owner authorization |
| `RECOVERY_INCOMPLETE` | A reverse action failed; completed actions are retained |
| `RECOVERED` | All registered reverse actions completed |

## Verification

`pantheon_aleph_test` checks automatic safe hold, denial without approval, and reverse-order recovery. Run the Pantheon CMake/CTest suite with a C++11 toolchain before treating the feature as verified.
