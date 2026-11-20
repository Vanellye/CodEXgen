# ERIA Manifest Energy → Fusion → Matter Fulfilment

This module turns the concept into a reviewable, provenance-carrying software artifact.

## Flow

1. **Manifest energy** records intent, the original anchor, source branch snapshots, and explicit boundaries.
2. **Fusion** links source references in a contract. It does not merge branches or execute source content.
3. **Matter fulfilment** is the inspectable Bash verifier, detached checksum, and isolated tests.

## Provenance

- Base: `main` at `0b134ed2770c789e42e850ea7be4228c4514b989`.
- Original anchor tree: `a326ae27f427bf1c4b73f8d983609c8d6d11e7ae`.
- The anchor commit was GitHub-verified when inspected.
- ASH and Bash branch heads are point-in-time snapshots. Git branch refs remain mutable and are not made immutable by this manifest.
- This PR is based directly on the original anchor, preserving its ancestry.

## Bash bridge

Run from this directory:

```bash
bash verify_manifest.sh manifest.json integrity.sha256
bash -n verify_manifest.sh && bash -n tests/test_manifest_bridge.sh
bash tests/test_manifest_bridge.sh
```

The verifier is read-only. It checks the detached SHA-256 and validates JSON syntax. It does not source, evaluate, dispatch, or execute manifest values. The test creates and removes only a temporary directory.

## Integrity limits

The checksum detects accidental or unauthorized changes to the manifest when compared with the separately reviewed checksum. It does not prove who authored the file, authenticate GitHub branch heads, freeze Git refs, or replace a signed commit/review.

## Governance boundary

No merge, release, deployment, external dispatch, hardware activation, or biological intervention is performed or authorized by this module. Human review of the exact PR head is required.
