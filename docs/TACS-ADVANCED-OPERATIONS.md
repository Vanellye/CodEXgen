# TACS Advanced Operations

This phase adds embedded Git tag signature verification, removable-media discovery, portable bundle export, append-only correction records, and signed successor-tag promotion.

## Safety model

- Media discovery lists already-mounted removable devices. It never mounts, formats, ejects, or writes.
- Export requires an exact destination confirmation and creates a new TACS directory. Existing TACS directories are never overwritten.
- Correction writes require the explicit --approve flag and use exclusive file creation; records are immutable.
- Git tag promotion is a dry-run by default. The --apply flag is required to create a successor tag.
- Promotion requires an embedded signature on the source annotated tag, a signer identity on the explicit allowlist, an approved correction record, and a configured Git signing key for the new successor.
- Original tags are never moved or deleted. Successors use refs/tags/tacs/<source>/<correction-digest>.
- No private key is copied to removable media.

## Commands

\`\`\`sh
PYTHONPATH=python python -m tacs.advanced discover-media
PYTHONPATH=python python -m tacs.advanced verify-tag --repo . --tag release-1 --trusted-signer FULL_GPG_FINGERPRINT
\`\`\`

For SSH-signed tags, provide a Git allowed-signers file:

\`\`\`sh
PYTHONPATH=python python -m tacs.advanced verify-tag --repo . --tag release-1 --trusted-signer release@example.invalid --ssh-allowed-signers-file ~/.ssh/allowed_signers
\`\`\`

Append a reviewed correction. The parent can be an ancestral tag record exported by the collector:

\`\`\`sh
PYTHONPATH=python python -m tacs.advanced correct \\
  --chain-dir .tacs/records --parent-record .tacs/ancestral-record.json \\
  --source-tag-ref refs/tags/release-1 --target FULL_GIT_OBJECT_ID \\
  --reason "Correction supported by review evidence" --evidence "review:change-123" \\
  --before-json '{"status":"old"}' --after-json '{"status":"corrected"}' \\
  --reviewer "reviewer-id" --test "python -m unittest discover -s tests" --approve
\`\`\`

Export requires a detected mounted removable-media root and exact path confirmation:

\`\`\`sh
PYTHONPATH=python python -m tacs.advanced export --repo . --metadata language-cadence.json \\
  --destination /media/USER/USB --confirm-destination /media/USER/USB
\`\`\`

An optional detached Ed25519 signature can be included only when it verifies against the exact generated manifest bytes. Supply --signature and --public-key together.

Promotion first prints a dry-run plan. The apply invocation creates a signed annotated successor tag and never force-updates an existing ref:

\`\`\`sh
PYTHONPATH=python python -m tacs.advanced promote --repo . \\
  --correction-record .tacs/records/CORRECTION_DIGEST.json --trusted-signer FULL_GPG_FINGERPRINT
# After reviewing the plan, repeat with --apply.
\`\`\`

## Verification details and limitations

- OpenPGP signatures use Git's configured GPG verifier. A full VALIDSIG fingerprint must match a supplied trusted signer.
- SSH signatures use Git's SSH verifier and an allowed-signers file; the verified principal must match a supplied trusted signer.
- A cryptographically valid signature is not automatically trusted: signer pinning is mandatory.
- The new TACS successor is signed by the local Git signing configuration. Promotion fails if signing cannot complete.
- Linux discovery requires a mounted block device marked removable in sysfs. macOS checks Disk Utility's removable-media property. Windows lists drives reported as removable by the OS. Some devices/enclosures may not expose removable status and will not be listed.
- Export requires the destination to be the detected mount root, not an arbitrary subdirectory. Existing TACS folder means fail-closed.
- The correction record reviewer field is provenance metadata, not an identity credential. A future approval-signature extension can cryptographically bind reviewer approval.
- No command mounts media or runs in the background. No physical removable device was accessed during implementation.
