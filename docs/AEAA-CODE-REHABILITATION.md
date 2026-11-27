# ÆĀÄÂ — Code Rehabilitation

## Mission

ÆĀÄÂ (Code Rehabilitation) identifies potentially harmful or unhealthy software behavior, preserves evidence, and guides a controlled path toward verified recovery. It is a software quality and safety mechanism, not a medical or psychological treatment system.

## Rehabilitation cycle

1. **Detect:** Inspect explicitly selected source, configuration, workflow, and test inputs using documented checks.
2. **Diagnose:** Preserve exact paths, line references, commit identity, evidence, and tool version. Distinguish deterministic findings from heuristic warnings.
3. **Contain:** Recommend pausing or isolating an affected operation. A detector does not independently kill processes, revoke credentials, or modify infrastructure.
4. **Propose:** Prepare a minimal patch or remediation plan in an isolated branch/workspace. Include risks and alternatives.
5. **Authorize:** Require a human grant naming actor, target, paths, permitted operation, reason, and expiry. Authorization to inspect is not authorization to write.
6. **Repair:** Apply only the approved patch within its stated scope. No self-approval or scope expansion.
7. **Verify:** Run relevant tests, security checks, regression checks, and recovery validation. A clean scan alone does not prove correctness.
8. **Record:** Retain original finding, patch, review, approvals, test evidence, and final disposition.

## Finding model

Each finding should carry a stable finding ID; repository and exact commit SHA; file path and line/range; detector and version; observed evidence; classification (FACT, HEURISTIC, HYPOTHESIS, or UNKNOWN); severity and confidence with rationale; suggested next step; and status (OPEN, TRIAGED, APPROVED, REPAIRED, VERIFIED, REJECTED, or BLOCKED).

A warning is not a verdict. Context, reachability, intent, and compensating controls must be reviewed before labeling code harmful.

## Permission boundaries

Default mode is read-only. ÆĀÄÂ must not edit, delete, move, or overwrite source files; change branches, refs, permissions, credentials, or protected history; run flagged code or exploit a suspected weakness; send findings externally without destination-specific approval; deploy, publish, or actuate hardware; or convert a detected trigger into an execution command.

A separate repair executor may be added only behind an independently reviewed authorization contract. It must verify the exact base commit and patch scope, reject stale approvals, preserve originals, and stop on any mismatch.

## Quality gates

A repair is not VERIFIED until the patch matches the approved scope; relevant tests pass and exact commands/results are recorded; regression and security implications are reviewed; recovery or rollback is demonstrated where applicable; and an accountable reviewer accepts the result.

If any gate is missing or fails, the outcome remains BLOCKED or OPEN; do not claim recovery.

## Integration

ÆĀÄÂ is intended to run as a non-blocking CI audit initially. Its reports are advisory and must not be interpreted as proof of safety. Any future blocking policy must be separately reviewed, documented, tested against false positives, and explicitly enabled.

## Relationship to Code Ethics

ÆĀÄÂ operates under [ERIA Code Ethics](./CODE-ETHICS.md). Provenance, least privilege, human authorization, privacy, reversibility, and no covert actuation are mandatory constraints.
