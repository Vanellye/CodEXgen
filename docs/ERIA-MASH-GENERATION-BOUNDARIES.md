# ERIA M*ASH Generation Boundaries

## Purpose

This governance layer limits M*ASH to preparing reviewable artifacts. Its default
is deny. It does not implement credential extraction, hidden execution, external
dispatch or patching, hardware activation, or biological intervention.

## Allowed workflow

`code.generate -> code.validate -> tests.isolated -> evidence.record -> review.present`

These are separate capabilities. No stage implicitly authorizes the next stage.
Unknown capabilities are denied.

## Explicitly prohibited

- Credential extraction, token scraping, password harvesting, or secret disclosure.
- Hidden, background, self-triggered, or otherwise unapproved execution.
- External dispatch, covert webhooks, remote commands, or external patching.
- Hardware actuation or activation.
- Biological manipulation or intervention.
- Automatic repository merge, release publication, or deployment.

## Storage contract

`CreateOnlyArtifactStore` is a narrow artifact writer. It requires an existing
root and existing parent directories; rejects absolute paths, traversal, empty
path components, symlink traversal, and existing destination files. It uses
descriptor-relative directory traversal, `O_NOFOLLOW`, and `O_EXCL`. Files are
created with mode 0600. It never offers overwrite or delete methods.

The store is intended for supported POSIX platforms. It fails closed when the
required no-follow primitives are unavailable. It does not claim to defeat
privileged concurrent modification of the underlying filesystem.

## Enforcement integration

Call `ExecutionBoundaryGuard.authorize(capability)` at each actual capability
adapter before work begins. Call the storage adapter only after the
`evidence.record` capability is authorized. Do not treat a policy JSON file or
a successful unit test as proof that every runtime path is guarded.

The audit callback receives only a capability identifier, decision, and reason.
Do not place credential values, generated payloads, or secret-bearing arguments
in security logs.

## Validation

From the repository root:

```sh
python -m unittest discover -s tools -p 'test_mash_boundary.py' -v
```

Tests cover allowlisting, prohibited and unknown capabilities, create-only
writes, overwrite rejection, path traversal, symlink files, symlink directories,
and invalid content types.

## Governance

This PR is anchored to the original ERIA core commit
`0b134ed2770c789e42e850ea7be4228c4514b989`. It does not modify `main`, change
branch protection, merge code, publish a release, deploy software, contact
external systems, activate hardware, or perform biological intervention.

A human reviewer must inspect the exact PR head. Independent approval is
required before any merge decision.
