# ERIA OS Sandbox and Automatic Code Progression

## Security boundary

The progression runner requires Linux bubblewrap (bwrap) and fails closed when
it is absent or cannot create namespaces. It does not fall back to proot, plain
subprocess execution, or unsandboxed tests.

The runner mounts the host root read-only, gives the job a writable disposable
workspace and temporary filesystem, hides common home/shared-storage paths,
drops Linux capabilities, creates namespaces including network isolation, and
kills child processes when the runner exits.

This is defense-in-depth, not a formally verified sandbox. On Android/Termux,
bubblewrap user namespaces may be unavailable or restricted. If so, use a
dedicated Linux VM or a separate Android application UID with OS-enforced
isolation. Do not describe proot as an OS sandbox.

## Progression model

1. A human or authorized code-generation agent creates a unified diff.
2. ERIA requires a clean source worktree.
3. The patch is applied only to a disposable snapshot of HEAD.
4. The fixed Python unittest suite runs inside bubblewrap with network isolation.
5. If tests pass, ERIA exports a candidate patch outside the source repository.
6. A human reviews the candidate diff.
7. A separate PONS-authorized local Git adapter can apply, stage and commit it.

The engine advances proposed patches; it does not invent source code by itself.
It never commits, pushes, merges, changes branches, or rewrites history.
Missing bwrap, sandbox failure, timeout, malformed patch or failed tests yields HOLD.

## Commands

Check prerequisites:

    command -v bwrap
    bwrap --version

Run an isolated workspace:

    python tools/eria_os_sandbox.py --workspace /path/to/workspace -- python -m unittest discover -s tests -v

Progress a proposed patch:

    python tools/eria_evolution.py --repo . --patch /path/to/proposal.patch --output /path/to/candidate.patch

The candidate diff must be reviewed before applying it to the working repository.

## Roadmap

Stage A: patch intake, disposable snapshots, isolated tests and candidate export.
Stage B: independent AVS scoring and evidence ledger integration.
Stage C: PONS-governed local promotion after explicit human authorization.
Stage D: scheduled progression over a human-approved backlog, with per-job
resource limits, audit records and network disabled by default.

No autonomous remote Git writes, deployment, or self-modification of the
progression controller is enabled.
