#!/usr/bin/env python3
"""PONS reviewer identity: root-signed certificates and Ed25519 evidence signatures."""
from __future__ import annotations

import base64
import hashlib
import json
import secrets
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def canonical_json(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def b64decode(value: str) -> bytes:
    try:
        return base64.b64decode(value, validate=True)
    except (ValueError, TypeError) as exc:
        raise ReviewerAuthenticationError("Malformed base64 field.") from exc


class ReviewerAuthenticationError(PermissionError):
    """Identity, certificate, challenge, scope, or signature verification failed."""


@dataclass(frozen=True)
class VerifiedReviewer:
    reviewer_id: str
    key_id: str
    certificate_sha256: str
    public_key_sha256: str
    role: str
    issuer: str


class ReviewerIdentityAuthority:
    """Authenticates reviewer certificates and signed, one-use AVS challenges.

    The trust-root public key must be provisioned out-of-band by an operator.
    This class never creates reviewer identities or trusts self-asserted keys.
    """

    def __init__(self, trust_root_public_key_b64: str, *, revoked_key_ids: set[str] | None = None):
        root_bytes = b64decode(trust_root_public_key_b64)
        if len(root_bytes) != 32:
            raise ReviewerAuthenticationError("Ed25519 trust-root public key must be 32 bytes.")
        self._root = Ed25519PublicKey.from_public_bytes(root_bytes)
        self._revoked = set(revoked_key_ids or ())
        self._challenges: dict[str, dict[str, Any]] = {}
        self._lock = threading.RLock()

    @staticmethod
    def _certificate_body(certificate: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(certificate, dict):
            raise ReviewerAuthenticationError("Reviewer certificate must be an object.")
        return {key: value for key, value in certificate.items() if key != "root_signature"}

    def verify_certificate(self, certificate: dict[str, Any], *, now: datetime | None = None) -> VerifiedReviewer:
        body = self._certificate_body(certificate)
        signature = b64decode(certificate.get("root_signature", ""))
        try:
            self._root.verify(signature, canonical_json(body))
        except InvalidSignature as exc:
            raise ReviewerAuthenticationError("Reviewer certificate is not signed by the configured trust root.") from exc

        required = ("reviewer_id", "key_id", "public_key", "role", "issuer", "not_before", "expires_at", "permissions")
        if any(not body.get(key) for key in required):
            raise ReviewerAuthenticationError("Reviewer certificate is missing required fields.")
        if body["role"] != "evidence_reviewer":
            raise ReviewerAuthenticationError("Certificate does not grant the evidence_reviewer role.")
        if not isinstance(body["permissions"], list) or "avs:evidence:submit" not in body["permissions"]:
            raise ReviewerAuthenticationError("Certificate lacks AVS evidence submission permission.")
        if body["key_id"] in self._revoked:
            raise ReviewerAuthenticationError("Reviewer key is revoked.")
        try:
            public_bytes = b64decode(body["public_key"])
            if len(public_bytes) != 32:
                raise ValueError("wrong key length")
            Ed25519PublicKey.from_public_bytes(public_bytes)
            current = now or datetime.now(timezone.utc)
            not_before = datetime.fromisoformat(body["not_before"])
            expires_at = datetime.fromisoformat(body["expires_at"])
            if not_before.tzinfo is None or expires_at.tzinfo is None:
                raise ValueError("certificate times must include timezone")
        except (ValueError, TypeError) as exc:
            raise ReviewerAuthenticationError("Invalid reviewer certificate fields.") from exc
        if current < not_before or current >= expires_at:
            raise ReviewerAuthenticationError("Reviewer certificate is not currently valid.")
        cert_hash = hashlib.sha256(canonical_json(certificate)).hexdigest()
        key_hash = hashlib.sha256(public_bytes).hexdigest()
        return VerifiedReviewer(
            reviewer_id=body["reviewer_id"],
            key_id=body["key_id"],
            certificate_sha256=cert_hash,
            public_key_sha256=key_hash,
            role=body["role"],
            issuer=body["issuer"],
        )

    def issue_challenge(self, certificate: dict[str, Any], *, ttl_seconds: int = 180) -> dict[str, str]:
        if not 15 <= ttl_seconds <= 600:
            raise ReviewerAuthenticationError("Challenge lifetime must be between 15 and 600 seconds.")
        reviewer = self.verify_certificate(certificate)
        challenge_id = secrets.token_urlsafe(24)
        nonce = secrets.token_urlsafe(32)
        issued = datetime.now(timezone.utc)
        expires = issued + timedelta(seconds=ttl_seconds)
        with self._lock:
            self._challenges[challenge_id] = {
                "issued_at": issued,
                "reviewer_id": reviewer.reviewer_id,
                "key_id": reviewer.key_id,
                "nonce": nonce,
                "expires_at": expires,
            }
        return {
            "challenge_id": challenge_id,
            "nonce": nonce,
            "reviewer_id": reviewer.reviewer_id,
            "key_id": reviewer.key_id,
            "certificate_sha256": reviewer.certificate_sha256,
            "issued_at": issued.isoformat(),
            "expires_at": expires.isoformat(),
        }

    def authenticate_evidence(
        self, *, certificate: dict[str, Any], challenge_id: str,
        signed_payload: dict[str, Any], signature_b64: str,
    ) -> VerifiedReviewer:
        reviewer = self.verify_certificate(certificate)
        with self._lock:
            challenge = self._challenges.get(challenge_id)
            if challenge is None:
                raise ReviewerAuthenticationError("Unknown, expired, or already-used challenge.")
            if challenge["expires_at"] <= datetime.now(timezone.utc):
                del self._challenges[challenge_id]
                raise ReviewerAuthenticationError("Reviewer challenge expired.")
            if challenge["reviewer_id"] != reviewer.reviewer_id or challenge["key_id"] != reviewer.key_id:
                raise ReviewerAuthenticationError("Challenge is bound to a different reviewer key.")
            expected = {
                "challenge_id": challenge_id,
                "nonce": challenge["nonce"],
            }
            if any(signed_payload.get(k) != v for k, v in expected.items()):
                raise ReviewerAuthenticationError("Signed payload does not bind the issued challenge.")
            try:
                signed_at = datetime.fromisoformat(signed_payload.get("signed_at"))
                if signed_at.tzinfo is None:
                    raise ValueError("timezone required")
            except (TypeError, ValueError) as exc:
                raise ReviewerAuthenticationError("Signed evidence timestamp is invalid.") from exc
            if signed_at < challenge["issued_at"] or signed_at > challenge["expires_at"]:
                raise ReviewerAuthenticationError("Evidence signature timestamp falls outside its challenge window.")
            if signed_at > datetime.now(timezone.utc) + timedelta(seconds=30):
                raise ReviewerAuthenticationError("Evidence signature timestamp is in the future.")
            public_key = Ed25519PublicKey.from_public_bytes(b64decode(certificate["public_key"]))
            try:
                public_key.verify(b64decode(signature_b64), canonical_json(signed_payload))
            except InvalidSignature as exc:
                raise ReviewerAuthenticationError("Reviewer evidence signature is invalid.") from exc
            # Consume only after successful verification; failed signatures cannot burn a valid challenge.
            del self._challenges[challenge_id]
        return reviewer

    def verify_stored_attestation(
        self, *, certificate: dict[str, Any], signed_payload: dict[str, Any],
        signature_b64: str,
    ) -> VerifiedReviewer:
        """Re-verify a persisted signed claim without reusing its consumed challenge."""
        signed_at = signed_payload.get("signed_at")
        try:
            signed_time = datetime.fromisoformat(signed_at)
            if signed_time.tzinfo is None:
                raise ValueError("timezone required")
        except (TypeError, ValueError) as exc:
            raise ReviewerAuthenticationError("Signed evidence timestamp is invalid.") from exc
        reviewer = self.verify_certificate(certificate, now=signed_time)
        public_key = Ed25519PublicKey.from_public_bytes(b64decode(certificate["public_key"]))
        try:
            public_key.verify(b64decode(signature_b64), canonical_json(signed_payload))
        except InvalidSignature as exc:
            raise ReviewerAuthenticationError("Persisted reviewer signature is invalid.") from exc
        return reviewer

    def revoke_key(self, key_id: str) -> None:
        if not key_id:
            raise ReviewerAuthenticationError("key_id is required.")
        with self._lock:
            self._revoked.add(key_id)
