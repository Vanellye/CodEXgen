"""Ed25519 verification for exact-scope independent reviewer approvals."""
from __future__ import annotations
import base64, json, time
from dataclasses import dataclass
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization import load_pem_public_key

@dataclass(frozen=True)
class ReviewerResult:
    valid: bool
    reason: str

def canonical_payload(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def verify_reviewer_approval(approval: dict, *, enrolled_reviewers: dict,
                             expected_proposal_sha256: str, expected_scope: str,
                             revoked_reviewers: set[str] | None = None,
                             now_epoch: int | None = None) -> ReviewerResult:
    """Verify enrolled identity, Ed25519 signature, proposal/scope, freshness and revocation.

    enrolled_reviewers maps reviewer_id to {"public_key_pem": "...", "enabled": True}.
    Registry enrollment itself must be controlled out-of-band by an independent authority.
    """
    try:
        payload = approval["payload"]
        reviewer_id = payload["reviewer_id"]
        entry = enrolled_reviewers.get(reviewer_id)
        if not entry or entry.get("enabled") is not True:
            return ReviewerResult(False, "reviewer is not independently enrolled and enabled")
        if reviewer_id in (revoked_reviewers or set()):
            return ReviewerResult(False, "reviewer is revoked")
        if payload.get("proposal_sha256") != expected_proposal_sha256:
            return ReviewerResult(False, "proposal digest mismatch")
        if payload.get("scope") != expected_scope:
            return ReviewerResult(False, "approval scope mismatch")
        now = int(time.time()) if now_epoch is None else now_epoch
        issued, expires = payload.get("issued_at"), payload.get("expires_at")
        if not isinstance(issued, int) or not isinstance(expires, int) or issued > now or expires <= now or expires <= issued:
            return ReviewerResult(False, "approval is stale, not yet valid, or has invalid time bounds")
        public_key = load_pem_public_key(entry["public_key_pem"].encode("utf-8"))
        signature = base64.b64decode(approval["signature_base64"], validate=True)
        public_key.verify(signature, canonical_payload(payload))
        return ReviewerResult(True, "independent reviewer signature and exact scope verified")
    except (KeyError, TypeError, ValueError, InvalidSignature):
        return ReviewerResult(False, "malformed approval or cryptographic verification failed")
