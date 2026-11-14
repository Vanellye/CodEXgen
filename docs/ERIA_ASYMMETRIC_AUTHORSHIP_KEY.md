# ERIA Asymmetric Authorship Key

## Purpose

This module verifies signed, specifically scoped authorship claims. It is separate
from the isolated-runner execution key and from Git commit author metadata.

## Trust configuration

Configure `ERIA_AUTHORSHIP_PUBLIC_KEY` as a GitHub Actions environment-scoped
(or otherwise protected) variable containing the PEM-encoded Ed25519 public key.
The verifier may additionally require a separately pinned SHA-256 fingerprint.
Do not trust a public key merely because it arrived beside the signed claim.

The corresponding private key must remain in a protected signing environment or
hardware-backed key store. It must never be placed in an artifact, repository,
workflow log, or client response. This implementation does not generate, persist,
or retrieve private keys and does not read private-key material.

## Claim format

A claim must identify a repository, full commit SHA, claimant, claimed author,
claim ID, status, and one or more exact repository-relative contribution paths.
Optional Git blob SHAs bind individual contributions to exact objects. The
canonical JSON payload is signed with Ed25519; the detached signature is Base64.

Supported claim states: `ASSERTED`, `DISPUTED`, and `WITHDRAWN`.

## Meaning and limits

A valid signature proves that the signer approved the exact claim payload. It
does not prove the claimed author created the work, transfer copyright, establish
ownership, or override existing Git metadata. ERIA must separately compare
commit history, blob identity, review records, and other available provenance.
Conflicting claims remain independently represented.

This feature does not force-push, rewrite commits, change author/committer fields,
modify `main`, or alter existing source records. Missing keys, malformed claims,
unknown fingerprints, or invalid signatures return `HOLD`.

## Python API

```python
from tools.eria_pantheon.authorship_key import verify_authorship_claim

result = verify_authorship_claim(
    claim,
    expected_fingerprint="trusted-public-key-sha256-hex",
)
```

The `cryptography` package must be available in the runtime for Ed25519 PEM
handling. If it is unavailable, verification fails closed.

## Protected GitHub Actions signing workflow

Manual workflow: `.github/workflows/eria-authorship-signing.yml`.

It runs only on the ERIA feature branch and requires the protected Actions
environment `eria-signing`. It consumes:

- Variable `ERIA_AUTHORSHIP_PUBLIC_KEY`: PEM public key.
- Variable `ERIA_AUTHORSHIP_KEY_FINGERPRINT`: SHA-256 fingerprint of the
  DER SubjectPublicKeyInfo bytes.
- Secret `ERIA_AUTHORSHIP_PRIVATE_KEY`: PEM private key; never printed or
  included in the artifact.

The workflow checks that the private key derives the configured public key,
checks the separately supplied fingerprint, validates the claim scope, signs
the canonical claim with Ed25519, verifies the signature, writes a temporary
artifact, and atomically renames it to `signed-authorship-claim.json`.
Only that signed claim is uploaded.

Before enabling the environment secret, an administrator must configure
required reviewers and restrict deployment branches. Review the workflow code
and branch protection before approving a signing run: anyone able to alter
trusted signing workflow code could otherwise attempt to misuse its secret.
Do not dispatch this workflow until the protected environment and all three
settings have been configured and independently checked.

The workflow does not force-push, modify source files, rewrite Git metadata,
or change `main`. Its signature establishes signer approval of the claim
payload, not the truth of authorship.
