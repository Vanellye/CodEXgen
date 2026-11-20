"""PONS authorization gate. Production trust verification is injected and mandatory."""
from dataclasses import dataclass
from typing import Callable, Optional

from .contracts import ReadGrant


@dataclass(frozen=True)
class PonsDecision:
    allowed: bool
    reason: str


class PonsAuthorizer:
    """Fail-closed, per-query read authorization; this class never mints grants."""

    def __init__(self, trusted_verifier: Callable[[ReadGrant], bool]):
        if not callable(trusted_verifier):
            raise TypeError("independent trusted PONS verifier required")
        self._verify = trusted_verifier

    def authorize(self, grant: Optional[ReadGrant], *, scope: str,
                  source_revision: str, now: int) -> PonsDecision:
        if grant is None:
            return PonsDecision(False, "grant_missing")
        if grant.revoked:
            return PonsDecision(False, "grant_revoked")
        if not grant.reviewer_id or not grant.approval_ref or not grant.nonce:
            return PonsDecision(False, "grant_identity_incomplete")
        if grant.scope != scope:
            return PonsDecision(False, "scope_mismatch")
        if grant.source_revision != source_revision:
            return PonsDecision(False, "source_revision_mismatch")
        if grant.issued_at > now or grant.expires_at <= now:
            return PonsDecision(False, "grant_not_current")
        try:
            verified = self._verify(grant)
        except Exception:
            verified = False
        if not verified:
            return PonsDecision(False, "independent_signature_or_revocation_check_failed")
        return PonsDecision(True, "authorized_read_only_query")
