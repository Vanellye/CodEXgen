# Pantheon Signed Package Exchange

Status: design specification with a partial read-only verifier implementation
Version: 0.2-draft

## Purpose

Allow Pantheon participants to exchange improvements through packages that are authenticated, reviewed, explicitly approved by the receiver, and safely reversible. Distribution is not installation authority. A publisher signature proves who signed the package and that its signed contents have not changed; it does not prove that the package is safe or grant permission to install it.

## Non-negotiable invariants

1. No package installs, executes, activates, or propagates without an explicit receiver action.
2. Signature verification, policy checks, and receiver approval are separate gates.
3. A valid signature is necessary but never sufficient for installation.
4. The receiver sees package identity, version, publisher, content hashes, dependency graph, requested capabilities, and change summary before approval.
5. Installation is staged and atomic. Existing versions remain available for rollback.
6. No package may silently add publishers, grant capabilities, alter trust roots, or approve another package.
7. Network, filesystem, process, device, and inter-module access are denied by default and granted only as narrowly scoped capabilities.
8. Historical source, manifests, approval records, and audit events are preserved; no automatic deletion or history rewriting.
9. No self-replication, stealth installation, persistence, privilege escalation, or automatic forwarding.
10. Revocation prevents future trust and installation decisions but does not silently delete an installed package; the receiver decides whether to disable or remove it.

## Package envelope

A package is a deterministic archive with a canonical, versioned manifest and content-addressed payload files. The manifest is canonicalized before signing.

Required manifest fields:
- format: package format identifier and version.
- package_id: stable package identifier.
- version: immutable semantic version.
- publisher_key_id: fingerprint of the signing public key.
- created_at: UTC creation timestamp.
- runtime_compatibility: Pantheon language/runtime versions and target platforms.
- entries: sorted relative payload paths, media types, sizes, and SHA-256 digests.
- dependencies: exact package IDs, versions, and content digests; no floating versions during installation.
- capabilities_requested: explicit capability names and scopes.
- change_summary: human-readable description and optional machine-readable change list.
- signature: algorithm, key ID, and signature over the canonical manifest plus payload digest list.

Reject duplicate paths, absolute paths, traversal segments, symlinks, hard links, device nodes, path collisions, oversized archives, undeclared files, missing files, and digest mismatches. Enforce configurable limits before extraction.

## Cryptographic design

- Use Ed25519 signatures for publisher authenticity and integrity.
- Use SHA-256 for content addressing and file digests.
- If confidentiality is required, encrypt payloads with a vetted authenticated-encryption construction such as XChaCha20-Poly1305 or AES-256-GCM. Encryption is optional and independent of signing.
- Never invent cryptography or reuse a signing key as an encryption key.
- Private signing keys remain with the publisher in an OS-backed keystore or hardware-backed store where available. They are never embedded in packages or committed to the repository.
- Receivers obtain public keys through an independently authenticated trust channel, pin the key fingerprint, and can inspect key history and revocation status.
- Key rotation requires a receiver-verifiable transition signed by the old and new keys, or explicit re-trust by the receiver. A new key cannot silently inherit trust.

## Receiver approval state machine

RECEIVED -> QUARANTINED -> SIGNATURE_VERIFIED -> POLICY_CHECKED -> REVIEWED -> APPROVED -> STAGED -> VALIDATED -> INSTALLED

Any failed check moves the package to REJECTED or QUARANTINED; it must not proceed automatically.

- RECEIVED: store bytes in a non-executable quarantine area.
- QUARANTINED: enforce archive limits and reject unsafe paths and file types.
- SIGNATURE_VERIFIED: verify signature, signer fingerprint, canonical manifest, and every payload digest.
- POLICY_CHECKED: resolve exact dependencies and check runtime compatibility and requested capabilities against receiver policy.
- REVIEWED: show publisher, key fingerprint, package/version, diff, dependency tree, requested capabilities, and warnings.
- APPROVED: record an explicit receiver decision bound to the exact package digest, signer, version, and capability grants. Any package change invalidates approval.
- STAGED: unpack into an isolated staging directory with no execution rights.
- VALIDATED: run static checks and tests in a sandbox with no ambient credentials, network, or host filesystem access.
- INSTALLED: atomically activate only after all gates pass. Keep the prior version and approval record for rollback and audit.

Approval must be an explicit user gesture or a documented receiver-controlled policy deliberately configured in advance. Default policy is manual approval. A sender cannot set or change receiver policy.

## Capability model

Capabilities are declarative, deny-by-default, and scoped. Examples:
- storage.read for an approved relative path.
- storage.write for a dedicated module data path.
- network.connect for an explicit host and port.
- module.call for an approved module ID and interface.

No wildcard capability grants. No implicit inheritance from the publisher or dependency. Dependencies receive only their own receiver-approved capabilities. Capability changes require fresh review and approval.

## Audit and rollback

Record append-only local audit events for receipt, verification result, signer fingerprint, review, approval/rejection, granted capabilities, validation result, installation, update, rollback, and revocation. Do not log private keys, credentials, or secret payload contents.

Keep each installed version in a separate immutable content-addressed directory. Activation points to a selected version. Rollback changes the active pointer to a previously validated version; it does not rewrite or erase package history. Provide receiver-controlled disable and uninstall actions.

## Exchange protocol

1. Sender exports a package and its signed manifest.
2. Receiver imports it into quarantine through an explicit local file, approved transport, or user-authorized peer connection.
3. Receiver verifies the package offline before any optional network lookup.
4. Receiver independently resolves signer trust and exact dependencies.
5. Receiver reviews and approves the exact digest and requested capability set.
6. Receiver stages, validates, and installs locally.
7. Any onward sharing is a separate export action by the receiver; receiving a package never authorizes forwarding it.

The protocol must work offline. Online transports are replaceable adapters, not trusted authorities.

## Threat model and required defenses

| Threat | Required defense |
|---|---|
| Package tampering | Signed canonical manifest and per-entry digest verification |
| Malicious trusted publisher | Receiver review, sandbox validation, narrow capabilities, rollback |
| Dependency substitution | Exact versions and digests; no floating dependency resolution |
| Archive/path traversal | Strict path normalization and archive-entry rejection |
| Replay or downgrade | Monotonic version policy and receiver-configurable minimum version |
| Compromised signing key | Key revocation, fingerprint pinning, explicit re-trust |
| Approval bypass | Approval bound to exact package digest, signer, version, and grants |
| Resource exhaustion | Archive, file-count, nesting, memory, CPU, and time limits |
| Malicious module behavior | Sandboxed validation and runtime capability enforcement |
| Unauthorized propagation | Separate receiver-initiated export; no auto-forwarding |

## Implementation phases

1. Specification and test vectors: canonical manifest format, signature test vectors, path validation rules, and state-machine tests.
2. Native verifier: C++ library/CLI that verifies signatures and hashes without executing payloads.
3. Quarantine and reviewer: local package inspection UI with explicit approval and capability diff.
4. Sandbox and installer: staged validation, atomic activation, version retention, and rollback.
5. Transport adapters: opt-in file exchange and authenticated peer transfer; transport must not bypass receiver gates.

## Acceptance tests

- Modified manifest or payload fails verification.
- Unknown or revoked signer is rejected or held for explicit re-trust.
- Valid signature without receiver approval cannot install or execute.
- Approval for one digest cannot authorize a changed package.
- Missing, substituted, or floating dependencies cannot install.
- Traversal paths, symlinks, duplicate entries, and oversized archives are rejected.
- Requested capabilities are displayed and denied unless explicitly granted.
- Validation runs without ambient network, credentials, or unrestricted filesystem access.
- Failed validation leaves the active installation unchanged.
- Rollback restores the previous validated version without deleting audit history.
- Receiving a package never triggers forwarding or installation on another device.

## Current implementation status

**Implemented and tested on this branch:** `python/pantheon/package_exchange.py` provides a read-only directory-bundle verifier.

- Requires a canonical, versioned JSON manifest and detached Ed25519 signature.
- Verifies the manifest with OpenSSL against a public key supplied out-of-band.
- Pins that key by an independently supplied SHA-256 fingerprint.
- Checks sorted unique relative paths, source repository/ref/commit provenance, exact file inventory, byte sizes, and SHA-256 payload digests.
- Rejects duplicate manifest keys, non-canonical JSON, traversal paths, symlinks, unlisted files, mismatched payloads, and bundles that exceed the configured manifest, key, file-count, per-file, or total-payload limits.
- Does not extract, install, execute, forward, promote, or authorize adoption. A successful report explicitly returns `adoption_authorized: false`.

Focused tests create ephemeral Ed25519 keys and exercise successful verification, key-pin mismatch, payload tampering, unlisted files, non-canonical manifests, traversal rejection, and resource-limit enforcement. These are test keys, not a production trust root.

**Not implemented:** deterministic archive parsing, encryption, dependency resolution, capability review, signer revocation/key rotation, receiver approval UI, sandboxed validation, atomic installation, version activation, rollback, or transport adapters. The current verifier is a partial Phase 1 implementation and must not be described as a complete package exchange or installer. The existing native source analyzer remains a separate non-executing inventory tool.
