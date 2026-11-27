# Pantheon IC — Integration Core

**Component:** `pantheon/IC`  
**Language:** C99  
**Role:** A small, deterministic state/gate contract for repository CI and future hardware-design validation workflows.

IC means **Integration Core** in this software layer. It is not an integrated-circuit netlist, a chip layout, a CI provider, or an executor.

## Contract

- Model a gate as pending, running, passed, failed, or blocked.
- Require dependencies to pass before a gate starts.
- Require explicit approval for gates marked as protected.
- Treat missing approval as hold and explicit denial as blocked.
- Keep validation success separate from permission to publish.
- Never run shell commands, invoke GitHub Actions, write files, upload artifacts, synthesize RTL, or control hardware.

## Aðð qualification

The IC exposes a read-only, fail-closed seven-check qualification contract:
Intent, Consent, Evidence, Forward, Reverse, Review, and Bridge Integrity.
`ic_aedd_qualifies` returns true only when all seven caller-supplied
flags are nonzero. These flags are inputs to a software gate, not verified
identity, cryptographic evidence, or authorization to execute an action.

## API

- `ic_can_start`: read-only eligibility check.
- `ic_start`: transition pending to running, or blocked if prerequisites are not met.
- `ic_finish`: record the result of an already-running check.
- `ic_can_publish`: read-only publication eligibility check; it does not publish.
- `ic_aedd_qualifies`: read-only qualification of the seven Aðð checks.

## Test

The suite is wired into `pantheon/run-contract-tests.sh` and therefore into the repository's existing `Pantheon C99 contract integration tests` CI job.

Compile manually:

```sh
cc -std=c99 -Wall -Wextra -Werror -Ipantheon/IC \
  pantheon/IC/IC.c pantheon/IC/tests/test_IC.c -o /tmp/pantheon-ic-test
/tmp/pantheon-ic-test
```

## Boundary

This first version is a software contract and testable component. It does not automatically approve merges, create releases, dispatch jobs, or grant permissions. Repository mutation, merge, deployment, and external dispatch remain separate authorized operations.
