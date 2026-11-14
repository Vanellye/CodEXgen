"""Cryptographically verified, exact-scope PONS capability grants.

This module verifies signed authorization envelopes. It does not create grants,
authenticate humans, execute patches, or provide an OS sandbox. The signing key
must be provisioned out-of-band and kept out of the repository.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import time
from typing import Any

_HEX = re.compile(r"^[0-9a-f]{64}$")
_REQUIRED = {"grant_id", "capability", "scope", "issued_at", "expires_at", "nonce", "signature"}


class ApprovalError(PermissionError):
    """A remote PONS grant is absent, invalid, expired, or out of scope."""


def _canonical(payload: dict[str, Any]) -> bytes:
    unsigned = {k: v for k, v in payload.items() if k != "signature"}
    return json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def verify_signed_grant(grant: Any, key: str | bytes, *,
                        capability: str, scope: str,
                        patch_sha256: str | None = None,
                        now: int | None = None,
                        max_lifetime_seconds: int = 900) -> dict[str, Any]:
    """Verify HMAC-SHA256 grant, exact capability/scope, expiry and optional patch hash."""
    if isinstance(key, str):
        key = key.encode("utf-8")
    if not isinstance(key, bytes) or len(key) < 32:
        raise ApprovalError("PONS signing key must contain at least 32 bytes.")
    if not isinstance(grant, dict) or not _REQUIRED.issubset(grant):
        raise ApprovalError("Complete signed PONS grant required.")
    if grant.get("capability") != capability or grant.get("scope") != scope:
        raise ApprovalError("PONS grant capability or exact scope mismatch.")
    if not all(isinstance(grant.get(k), str) and grant[k].strip()
               for k in ("grant_id", "nonce", "signature")):
        raise ApprovalError("Grant identity, nonce and signature must be non-empty strings.")
    issued, expires = grant.get("issued_at"), grant.get("expires_at")
    if type(issued) is not int or type(expires) is not int:
        raise ApprovalError("Grant timestamps must be integer Unix seconds.")
    current = int(time.time()) if now is None else int(now)
    if issued > current + 30 or expires <= current or expires <= issued:
        raise ApprovalError("PONS grant is not currently valid.")
    if expires - issued > max_lifetime_seconds:
        raise ApprovalError("PONS grant lifetime exceeds policy.")
    if patch_sha256 is not None:
        if not isinstance(patch_sha256, str) or not _HEX.fullmatch(patch_sha256):
            raise ApprovalError("An exact SHA-256 patch hash is required.")
        if grant.get("patch_sha256") != patch_sha256:
            raise ApprovalError("Approved patch hash does not match the proposed patch.")
    elif "patch_sha256" in grant and grant["patch_sha256"] is not None:
        raise ApprovalError("Unexpected patch hash for this capability.")
    signature = grant["signature"]
    if not _HEX.fullmatch(signature):
        raise ApprovalError("Malformed PONS signature.")
    expected = hmac.new(key, _canonical(grant), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise ApprovalError("PONS signature verification failed.")
    return {k: v for k, v in grant.items() if k != "signature"}


def sign_grant(payload: dict[str, Any], key: str | bytes) -> dict[str, Any]:
    """Signing helper for trusted workflow tooling; never expose the key to browsers."""
    if isinstance(key, str):
        key = key.encode("utf-8")
    if not isinstance(key, bytes) or len(key) < 32:
        raise ApprovalError("PONS signing key must contain at least 32 bytes.")
    if "signature" in payload:
        raise ApprovalError("Sign an unsigned grant payload.")
    result = dict(payload)
    result["signature"] = hmac.new(key, _canonical(result), hashlib.sha256).hexdigest()
    return result
