# ERIA Linux Sandbox Readiness

## Scope

This milestone adds a read-only host-capability probe for a future isolated runner. It is not an execution runner and does not execute generated or candidate code.

## Probe

Run:

```bash
python tools/eria_sandbox_readiness.py
```

The probe checks for:
- Linux host identification
- Bubblewrap executable presence
- A non-zero unprivileged user-namespace limit
- cgroup v2 and the CPU, memory, and pids controllers

It reads only the supplied host's `/proc` and `/sys` metadata. It does not invoke Bubblewrap, spawn a process, alter mounts, change cgroups, or write files.

## Interpretation

`HOST_PREREQUISITES_PRESENT_REVIEW_REQUIRED` means only that the listed prerequisite indicators are present. It does not prove namespace creation, network isolation, read-only mounts, seccomp enforcement, or resource limits work.

The result always reports:
- `execution_enabled: false`
- `candidate_code_executed: false`
- `source_write_enabled: false`
- `pons_decision: HOLD`

## Remaining gates

Before any candidate execution can be considered, ERIA needs:
1. A separately reviewed runner implementation with disposable, unprivileged namespaces, no network, read-only source mounts, bounded CPU/memory/PIDs/time, and a disposable output area.
2. Negative tests proving mount, network, privilege, path, and resource boundaries.
3. An independently trusted PONS verifier for authentic, expiring, revocable grants bound to the exact candidate digest, test command, and resource policy.
4. A policy change explicitly authorizing this narrow operation. The current red-write-only policy denies shell execution and generated-content execution; this probe does not override it.

No source mutation, Git mutation, merge, deployment, or PONS grant is performed by this milestone.
