"""Cryptographic reviewer verification for Ruble-I v4.

Requires the 'cryptography' package at deployment. Public keys are supplied by
an independently governed trust registry; private keys never belong here.
"""
from __future__ import annotations

import base64
import json
from datetime import datetime, timezone


class ReviewerVerificationError(Exception):
    pass


def _utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ReviewerVerificationError("signed timestamps must include timezone")
    return parsed.astimezone(timezone.utc)


def canonical_signed_payload(artifact: dict) -> bytes:
    fields = (
        "reviewer_id", "key_id", "intent_sha256", "policy_version",
        "issued_at", "expires_at", "nonce", "scope",
    )
    if any(field not in artifact for field in fields):
        raise ReviewerVerificationError("approval artifact is missing signed fields")
    payload = {field: artifact[field] for field in fields}
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


class Ed25519ReviewerVerifier:
    """Verify an independent reviewer's Ed25519 signature and trust status."""

    def __init__(self, trusted_public_keys: dict[str, str],
                 revoked_key_ids: set[str] | None = None,
                 max_age_seconds: int = 900):
        self._keys = dict(trusted_public_keys)
        self._revoked = set(revoked_key_ids or set())
        self._max_age = max_age_seconds

    def verify(self, prepared: dict, artifact: dict) -> bool:
        try:
            key_id = artifact["key_id"]
            reviewer_id = artifact["reviewer_id"]
            if not reviewer_id or reviewer_id == "self" or key_id in self._revoked:
                return False
            encoded_key = self._keys.get(key_id)
            if not encoded_key:
                return False
            if artifact["intent_sha256"] != prepared["intent_sha256"]:
                return False
            if artifact["policy_version"] != prepared["policy_version"]:
                return False
            expected_scope = {
                "intent_sha256": prepared["intent_sha256"],
                "provider": prepared["provider"],
                "rail": prepared["rail"],
                "beneficiary_id": prepared["beneficiary_id"],
                "asset": prepared["asset"],
                "amount_minor": prepared["amount_minor"],
                "fee_limit_minor": prepared["fee_limit_minor"],
            }
            if artifact["scope"] != expected_scope:
                return False
            now = datetime.now(timezone.utc)
            issued = _utc(artifact["issued_at"])
            expires = _utc(artifact["expires_at"])
            if issued > now or expires <= now or (now - issued).total_seconds() > self._max_age:
                return False
            if not artifact["nonce"] or len(artifact["nonce"]) < 16:
                return False
            signature = base64.b64decode(artifact["signature_b64"], validate=True)
            public_key = base64.b64decode(encoded_key, validate=True)
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
            Ed25519PublicKey.from_public_bytes(public_key).verify(
                signature, canonical_signed_payload(artifact))
            return True
        except Exception:
            # Missing crypto dependency, malformed encoding, invalid signature,
            # invalid fields, and parsing errors all fail closed.
            return False
