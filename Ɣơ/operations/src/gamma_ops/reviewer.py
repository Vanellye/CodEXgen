"""Independent Ed25519 approval verification for READY_TO_OPEN records."""
from __future__ import annotations
import base64, hashlib, json, os, time
from pathlib import Path
from typing import Any
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import load_pem_public_key

def canonical_payload(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def _inside_root(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative.strip():
        raise ValueError("required evidence path is missing")
    raw = root / relative
    cursor = raw
    while cursor != root and cursor != cursor.parent:
        if cursor.is_symlink():
            raise ValueError("symlink paths are not accepted for approval evidence")
        cursor = cursor.parent
    resolved = raw.resolve(strict=True)
    resolved.relative_to(root)
    if not resolved.is_file():
        raise ValueError("approval evidence path is not a regular file")
    return resolved

def verify_readiness_approval(review: dict[str, Any], *, repository_root: str | Path,
                              expected_artifact_sha256: str, now_epoch: int | None = None) -> tuple[bool, str]:
    """Verify exact artifact, commit and scope against a protected external registry hash pin."""
    try:
        root = Path(repository_root).resolve(strict=True)
        pin = os.getenv("ERIA_REVIEWER_REGISTRY_SHA256", "").strip().lower()
        if len(pin) != 64 or any(ch not in "0123456789abcdef" for ch in pin):
            return False, "external reviewer registry digest pin is not configured"
        registry_path = _inside_root(root, review.get("reviewer_registry_path", "Ɣơ/operations/registry/reviewers.json"))
        registry_bytes = registry_path.read_bytes()
        if hashlib.sha256(registry_bytes).hexdigest() != pin:
            return False, "reviewer registry digest does not match the externally pinned digest"
        registry = json.loads(registry_bytes.decode("utf-8"))
        reviewers, revoked = registry.get("reviewers"), registry.get("revoked", [])
        if not isinstance(reviewers, dict) or not isinstance(revoked, list):
            return False, "reviewer registry structure is invalid"
        approval_path = _inside_root(root, review.get("approval_path", ""))
        approval = json.loads(approval_path.read_text(encoding="utf-8"))
        payload = approval["payload"]
        reviewer_id = payload["reviewer_id"]
        reviewer = reviewers.get(reviewer_id)
        if not reviewer or reviewer.get("enabled") is not True or reviewer_id in revoked:
            return False, "reviewer is not enrolled, enabled, or is revoked"
        expected_scope, expected_commit, expected_ref = review.get("scope"), review.get("commit_sha"), review.get("review_ref")
        if payload.get("proposal_sha256") != expected_artifact_sha256:
            return False, "signed proposal digest does not match the reviewed artifact"
        if payload.get("scope") != expected_scope or not isinstance(expected_scope, str) or not expected_scope:
            return False, "signed approval scope mismatch"
        if payload.get("commit_sha") != expected_commit or not isinstance(expected_commit, str) or len(expected_commit) != 40:
            return False, "signed approval commit SHA mismatch"
        if payload.get("review_ref") != expected_ref or not isinstance(expected_ref, str) or not expected_ref:
            return False, "signed review reference mismatch"
        now = int(time.time()) if now_epoch is None else now_epoch
        issued, expires = payload.get("issued_at"), payload.get("expires_at")
        if (not isinstance(issued, int) or isinstance(issued, bool) or
            not isinstance(expires, int) or isinstance(expires, bool) or
            issued > now or expires <= now or expires <= issued or expires - issued > 86400):
            return False, "approval is stale, not yet valid, or has invalid time bounds"
        public_key = load_pem_public_key(reviewer["public_key_pem"].encode("utf-8"))
        if not isinstance(public_key, Ed25519PublicKey):
            return False, "enrolled reviewer key is not Ed25519"
        signature = base64.b64decode(approval["signature_base64"], validate=True)
        public_key.verify(signature, canonical_payload(payload))
        return True, "exact artifact, commit, scope, review reference and independent Ed25519 signature verified"
    except (OSError, ValueError, TypeError, KeyError, UnicodeDecodeError,
            json.JSONDecodeError, InvalidSignature):
        return False, "approval evidence is malformed, inaccessible, or cryptographically invalid"
