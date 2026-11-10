# TACS Read-only Tooling

The first implementation deliberately stops before USB export. It provides three independently callable operations:

- **Collector:** enumerates \`refs/tags\`, distinguishes lightweight and annotated tags, records direct and peeled object identities, and emits canonical JSON. It invokes only read-only Git commands.
- **Language/cadence serializer:** validates schema version 1, NFC-normalizes strings, sorts object keys/tokens/phases, rejects floating-point values, and emits stable UTF-8 JSON plus a SHA-256 digest.
- **Signature verifier:** verifies Ed25519 detached signatures over the exact manifest bytes using OpenSSL's public-key verification command. It accepts a public key only; it never loads a private key.

## Run

From the repository root:

\`\`\`sh
PYTHONPATH=python python -m tacs collect --repo .
PYTHONPATH=python python -m tacs serialize --input metadata.json > metadata.canonical.json
PYTHONPATH=python python -m tacs verify --manifest manifest.json --signature manifest.sig --public-key trusted-public.pem
PYTHONPATH=python python -m unittest discover -s tests -p "test_tacs.py" -v
\`\`\`

The serializer prints the SHA-256 digest to stderr and canonical JSON to stdout. Verification exits 0 for a valid signature, 1 for an invalid signature, and 2 for an operational/input error.

## Metadata schema

\`\`\`json
{
  "schema_version": 1,
  "language": {
    "schema_version": 1,
    "tokens": [
      {
        "token_id": "rise",
        "glyph": "ơ",
        "pronunciation": "oh",
        "gloss": "emergence",
        "role": "state"
      }
    ]
  },
  "cadence": {
    "schema_version": 1,
    "phases": [
      {"index": 0, "token_ids": ["rise"], "beats": 1}
    ],
    "tempo": {"numerator": 60, "denominator": 1, "unit": "bpm"}
  }
}
\`\`\`

Tempo is optional and represented as an integer rational, never a float. Cadence is descriptive metadata only; it cannot trigger timers, audio, biological effects, or Git actions. Glyphs do not replace numeric zeros or machine-readable data.

## Read-only and trust boundaries

- Collector never writes to refs, the index, worktree, or Git configuration.
- Collector emits to stdout; redirecting output is an explicit shell-level file write by the operator.
- Signature verification checks only authenticity/integrity relative to the supplied public key. It does not establish that the signed content is correct, safe, current, or authorized.
- The detached signature covers the exact bytes, including the final newline. Canonicalize before signing and verify the same bytes.
- The private signing key stays outside the repository and removable media.
- No USB discovery, mounting, writing, or export code is included.
- No tag, branch, or repository reference is modified.

## Current implementation limits

- Ed25519 detached signatures only; OpenSSL must be installed and available as \`openssl\`.
- The collector records tag names, object IDs/types, annotated-tag message/tagger, and whether a common PGP/SSH signature armor marker is present. That marker is descriptive only; this verifier does not validate Git's embedded tag signatures.
- Repository identity uses a sanitized origin URL when available; otherwise it uses the local repository directory name.
- No manifest import, correction-chain mutation, USB export, automatic trust-on-first-use, or Git ref promotion is implemented.
