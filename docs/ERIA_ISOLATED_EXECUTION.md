# ERIA Isolated Execution and Evidence Synthesis

## Runner model

`tools/eria_pantheon/isolated_runner.py` is an opt-in Linux runner. It requires `bubblewrap` (`bwrap`) and fails closed when unavailable. It does not run commands directly in the user's checkout.

1. Pin the exact checked-out Git commit.
2. Issue a one-use approval scoped to repository path, commit SHA, one fixed command ID, and a short expiry.
3. Export that commit with `git archive` into a temporary workspace; reject traversal, special files, symlinks, and credential-like paths.
4. Run only a fixed allowlisted command inside bubblewrap with unshared namespaces/network, read-only system mounts, a temporary writable workspace, no host home mount, and a bounded timeout.
5. Capture bounded stdout/stderr and hashes, then HMAC-sign the result with the local ERIA runner key.
6. Consume the approval even when later validation fails.

## Commands

From a Linux environment with bubblewrap installed:

    python -m tools.eria_pantheon.isolated_runner approve . python-tests
    # Type the exact approval phrase displayed.
    # Copy the approval_id from the JSON response.
    python -m tools.eria_pantheon.isolated_runner run . python-tests --approval-id APPROVAL_ID

Other fixed command IDs are `android-debug-build` and `make-check-review`. No arbitrary shell strings, command arguments, package install commands, or network access are accepted.

The key is stored at `~/.eria/runner.key` with mode 0600. One-use approvals live under `~/.eria/runner-approvals/`. Keep the key private. A compromised local account can misuse it; the design is not a substitute for a hardened VM/container host.

## ERIA API

- `POST /api/runner/run`: consumes a previously issued one-use approval and returns signed evidence.
- `POST /api/ai/execution-synthesis`: verifies the HMAC, exact repository, exact commit, source SHA-256, and joins execution evidence with Æị/Âï source analysis.
- `POST /api/repository/review` accepts up to 20 signed `execution_results` and passes only valid, same-commit results to the quality analyzer.

## Evidence interpretation

A `PASSED` result means only that the exact fixed command exited zero on the exact archived commit in the configured sandbox. It does not establish overall quality, security, correctness, or deployability. `FAILED` and `TIMEOUT` remain visible evidence. Results from another commit, invalid signatures, or unknown runner states are excluded.

Âï synthesis is deterministic aggregation of source evidence and the run record, not a generative LLM. Derived output remains NON_AUTHORITATIVE.

## PONS and preservation

PONS service remains ON. Execution permission is separate from service state. The CLI approval is scoped to one command and one commit; it does not authorize source edits, Git mutations, SQLite source-record changes, deployment, publication, or transmission. The runner never binds the host checkout or host home into the sandbox. `main` is not modified.

## Termux note

Termux on Android may not provide Linux bubblewrap/user namespaces. In that case the runner intentionally returns HOLD. Run this component on a supported isolated Linux host rather than weakening the sandbox or falling back to direct shell execution.
