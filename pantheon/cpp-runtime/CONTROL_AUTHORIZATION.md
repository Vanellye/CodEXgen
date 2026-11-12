# Pantheon 38/38 Control Authorization Standard

## Hard gate

Pantheon control modules are denied by default. A control module must declare `requiresControlAuthorization() == true`. Calling it through the ordinary runtime execution path is rejected.

The controlled execution path requires all of the following:

1. Exactly 38 standards are supplied.
2. Standard numbers 1 through 38 are each present exactly once.
3. Every standard is marked passed.
4. Every standard has a non-empty evidence reference.
5. An authenticated owner-approval adapter explicitly confirms approval.

The 38th standard is not a shortcut: it is checked identically to standards 1–37. Missing, duplicated, failed, or unevidenced standards deny activation. Owner approval cannot compensate for a failed standard.

## What "control" means

This gate authorizes only a registered Pantheon module invocation within the host application. It does not grant operating-system administrator rights, unrestricted Android permissions, control over unrelated apps, remote devices, physical actuators, biological systems, or other people's accounts. Those capabilities require separate platform permissions, explicit consent, device-specific safety interlocks, and their own authorization reviews.

## Evidence and owner approval

`StandardEvidence` carries an evidence reference, not proof that the evidence is genuine. Production adapters must resolve references to an append-only audit store and validate the evidence, identity, and approval cryptographically or through the host platform's authenticated authorization mechanism. The included test approval provider is a test double only.

This repository does not yet define the substantive content of all 38 standards. Until a reviewed canonical catalogue and evidence validators exist, 38/38 is a structural gate, not a claim that the system has passed a complete safety certification.

## Fail-closed behavior

- No implicit grant at startup.
- No automatic grant from a score or progress counter.
- No cached grant across process restarts.
- No fallback when evidence or owner approval is unavailable.
- Control modules cannot execute through the ordinary `Runtime::execute` path.
