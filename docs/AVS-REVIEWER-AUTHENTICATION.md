# PONS authenticated reviewer identity for AVS

## Trust model

AVS accepts evidence only after PONS verifies all of the following:

1. A reviewer certificate is signed by the operator-provisioned Ed25519 trust root.
2. The certificate is currently valid, grants the evidence_reviewer role, and includes avs:evidence:submit.
3. The certificate key is not present in the operator-provisioned revocation list.
4. PONS issued a short-lived, one-use challenge bound to that reviewer key.
5. The reviewer signed the exact canonical JSON evidence payload, including the challenge nonce and timestamp.
6. The signed reviewer identity is not the component being assessed.

PONS re-verifies the certificate and evidence signature from the ledger whenever it calculates a score. Unauthenticated or invalid records are excluded. A missing trust root disables evidence intake and score issuance (fail closed).

## Provision the trust root

Generate the trust root on a controlled offline machine. Keep its private key offline and backed up securely; never commit it or copy it to the ERIA runtime.

    import base64
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    root = Ed25519PrivateKey.generate()
    private = root.private_bytes(
        serialization.Encoding.Raw,
        serialization.PrivateFormat.Raw,
        serialization.NoEncryption(),
    )
    public = root.public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )
    print("ROOT_PRIVATE_B64=" + base64.b64encode(private).decode())
    print("ROOT_PUBLIC_B64=" + base64.b64encode(public).decode())

Store the root private key offline. Set only the public key on the ERIA host:

    export ERIA_PONS_REVIEWER_ROOT_PUBKEY='BASE64_ROOT_PUBLIC_KEY'

The environment variable must be set for the process that starts the ERIA conversation server. If it is absent, PONS reports NOT_CONFIGURED_FAIL_CLOSED.

## Issue a reviewer certificate

Generate each reviewer key pair separately. The reviewer's private key remains with that reviewer and must never be stored in the repository or shared with the component under review.

The root operator signs a certificate body with these fields:

- reviewer_id: stable unique reviewer identity
- key_id: unique key identifier
- public_key: base64 raw 32-byte Ed25519 public key
- role: exactly evidence_reviewer
- issuer: trust-root/operator identifier
- not_before, expires_at: timezone-aware ISO-8601 timestamps
- permissions: includes avs:evidence:submit

The certificate is the body plus root_signature, which is the base64 Ed25519 signature of the canonical JSON body (sorted keys, compact separators, UTF-8). See reviewer_identity.py for the canonicalization function.

## Reviewer evidence protocol

A trusted application calls PONS:

    challenge = pons.issue_reviewer_challenge(certificate)

The reviewer constructs this exact signed JSON object:

    payload = {
        "challenge_id": challenge["challenge_id"],
        "nonce": challenge["nonce"],
        "claim_id": "claim-123",
        "subject_component": "eria-translator",
        "evidence_ref": "sha256:<evidence-digest-or-controlled-reference>",
        "outcome": True,
        "weight": 1.0,
        "method": "independent_review",
        "signed_at": "<timezone-aware-ISO-8601-time>",
    }

The reviewer signs canonical_json(payload) using their Ed25519 private key, base64-encodes the signature, and submits:

    pons.submit_accuracy_evidence(
        certificate=certificate,
        challenge_id=challenge["challenge_id"],
        signed_payload=payload,
        signature_b64=signature_b64,
    )

Challenges expire after three minutes by default (configurable between 15 and 600 seconds), are bound to one reviewer key, and are consumed after successful signature verification. A replay is rejected. The signed timestamp must fall within the challenge window.

## Revocation

Set comma-separated revoked key IDs before starting ERIA:

    export ERIA_PONS_REVOKED_REVIEWER_KEYS='key:reviewer-a:01,key:reviewer-b:02'

A revoked key cannot submit new evidence, and evidence from that key is no longer counted in subsequent scores. Re-start the ERIA process after changing this setting.

## Install and test

    python -m pip install -r python/requirements.txt
    PYTHONPATH=tools python -m unittest discover -s tools/tests -p 'test_eria_avs.py' -v

## Security boundaries and limitations

- The root public key and revocation list are operator-controlled deployment configuration. Protect the ERIA host and its environment.
- The trust root's private key is the ultimate authority for issuing reviewer certificates. Use offline custody and a documented issuance/revocation process.
- Ed25519 proves possession of a certified private key and integrity of the signed statement; it does not prove that the reviewer performed a competent review or that the cited evidence is true.
- evidence_ref is a reference, not automatically fetched or independently inspected by AVS. A future evidence resolver should hash and preserve the referenced artifact.
- The JSONL hash chain detects accidental or partial tampering, but an attacker able to rewrite the entire ledger can recompute the chain. For stronger tamper evidence, periodically anchor ledger heads in an independently controlled append-only store or sign them with a separate audit key.
- This is an application-level trust boundary, not an OS sandbox. Keep private keys outside the repository and restrict host access.
