"""AVS evidence integrity and provenance validation."""
from dataclasses import dataclass
import hashlib
from typing import Callable

from .contracts import EvidenceRecord


@dataclass(frozen=True)
class AvsResult:
    valid: bool
    status: str
    digest: str


class AvsValidator:
    """Validate evidence bytes and source binding; external attestation is injected."""

    def __init__(self, attestation_verifier: Callable[[EvidenceRecord], bool]):
        if not callable(attestation_verifier):
            raise TypeError("independent AVS attestation verifier required")
        self._verify = attestation_verifier

    def validate(self, record: EvidenceRecord, *, expected_revision: str,
                 now: int, max_age_seconds: int = 86400) -> AvsResult:
        digest = hashlib.sha256(record.payload).hexdigest()
        if not record.evidence_id or not record.source or not record.provenance_ref:
            return AvsResult(False, "provenance_incomplete", digest)
        if record.source_revision != expected_revision:
            return AvsResult(False, "source_revision_mismatch", digest)
        if record.captured_at > now or now - record.captured_at > max_age_seconds:
            return AvsResult(False, "evidence_stale_or_future", digest)
        if digest != record.payload_sha256:
            return AvsResult(False, "payload_digest_mismatch", digest)
        try:
            attested = self._verify(record)
        except Exception:
            attested = False
        if not attested:
            return AvsResult(False, "independent_attestation_failed", digest)
        return AvsResult(True, "evidence_verified", digest)
