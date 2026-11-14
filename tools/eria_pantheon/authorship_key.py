"""Asymmetric verification for scoped ERIA authorship claims.

The module verifies Ed25519 signatures against a separately trusted public key.
It never creates, stores, or exports private keys and never edits Git metadata.
A valid signature proves that the holder of the corresponding private key signed
the claim; it does not independently prove that the claimed person authored it.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
from typing import Any

_SHA1 = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class AuthorshipKeyError(ValueError):
    """Invalid claim, key, or signature."""


def canonical_claim(claim: dict[str, Any]) -> bytes:
    """Validate and serialize a narrowly scoped, immutable claim payload."""
    if not isinstance(claim, dict):
        raise AuthorshipKeyError("Claim must be an object.")
    required = ("claim_id", "claimant", "claimed_author", "repository",
                "commit_sha", "contributions", "claim_status")
    if any(not claim.get(key) for key in required):
        raise AuthorshipKeyError("Claim is missing required attribution fields.")
    if not _SHA1.fullmatch(str(claim["commit_sha"]).lower()):
        raise AuthorshipKeyError("A full 40-character commit SHA is required.")
    if claim["claim_status"] not in {"ASSERTED", "DISPUTED", "WITHDRAWN"}:
        raise AuthorshipKeyError("Unsupported authorship claim status.")
    contributions = claim["contributions"]
    if not isinstance(contributions, list) or not contributions:
        raise AuthorshipKeyError("At least one specifically identified contribution is required.")
    for item in contributions:
        if not isinstance(item, dict) or not item.get("path"):
            raise AuthorshipKeyError("Each contribution must identify a repository-relative path.")
        path = str(item["path"]).replace("\\", "/")
        if path.startswith("/") or any(part in {"", ".", ".."} for part in path.split("/")):
            raise AuthorshipKeyError("Contribution paths must be normalized repository-relative paths.")
        if item.get("blob_sha") and not _SHA1.fullmatch(str(item["blob_sha"]).lower()):
            raise AuthorshipKeyError("Contribution blob SHA must be a full Git SHA.")
    # Exclude the signature envelope: only the claim itself is signed.
    payload = {key: value for key, value in claim.items()
               if key not in {"signature", "public_key", "verification", "signature_algorithm", "key_fingerprint"}}
    return json.dumps(payload, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def public_key_fingerprint(public_key_pem: str) -> str:
    """Return SHA-256 fingerprint of the DER-encoded trusted Ed25519 key."""
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key = serialization.load_pem_public_key(public_key_pem.encode("ascii"))
        if not isinstance(key, Ed25519PublicKey):
            raise AuthorshipKeyError("Trusted key is not Ed25519.")
        der = key.public_bytes(serialization.Encoding.DER,
                               serialization.PublicFormat.SubjectPublicKeyInfo)
    except AuthorshipKeyError:
        raise
    except Exception as exc:
        raise AuthorshipKeyError("Trusted Ed25519 public key could not be loaded.") from exc
    return hashlib.sha256(der).hexdigest()


def verify_authorship_claim(
    claim: dict[str, Any],
    *,
    trusted_public_key_pem: str | None = None,
    expected_fingerprint: str | None = None,
) -> dict[str, Any]:
    """Verify an Ed25519 claim using a separately provisioned trusted public key."""
    pem = trusted_public_key_pem or os.environ.get("ERIA_AUTHORSHIP_PUBLIC_KEY", "")
    if not pem:
        return {"status": "HOLD", "verified": False,
                "reason": "Trusted public key is not configured."}
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        fingerprint = public_key_fingerprint(pem)
        if expected_fingerprint and not re.fullmatch(r"[0-9a-fA-F]{64}", expected_fingerprint):
            raise AuthorshipKeyError("Expected key fingerprint must be SHA-256 hex.")
        if expected_fingerprint and fingerprint.lower() != expected_fingerprint.lower():
            return {"status": "HOLD", "verified": False,
                    "reason": "Trusted key fingerprint mismatch.",
                    "key_fingerprint": fingerprint}
        key = serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(key, Ed25519PublicKey):
            raise AuthorshipKeyError("Trusted key is not Ed25519.")
        signature_text = claim.get("signature", "")
        signature = base64.b64decode(signature_text, validate=True)
        if len(signature) != 64:
            raise AuthorshipKeyError("Ed25519 signature must be 64 bytes.")
        key.verify(signature, canonical_claim(claim))
        return {"status": "SIGNATURE_VALID", "verified": True,
                "key_algorithm": "Ed25519", "key_fingerprint": fingerprint,
                "claim_status": claim["claim_status"],
                "authorship_established": False,
                "meaning": "Signature verified; authorship still requires provenance review."}
    except AuthorshipKeyError as exc:
        return {"status": "HOLD", "verified": False, "reason": str(exc)}
    except Exception:
        return {"status": "HOLD", "verified": False,
                "reason": "Signature verification failed."}
