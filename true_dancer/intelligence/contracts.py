"""Immutable contracts shared by PONS, AVS, and intelligence adapters."""
from dataclasses import dataclass
from typing import Mapping, Any


@dataclass(frozen=True)
class ReadGrant:
    reviewer_id: str
    approval_ref: str
    scope: str
    issued_at: int
    expires_at: int
    source_revision: str
    nonce: str
    revoked: bool = False
    signature: str = ""


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    source: str
    source_revision: str
    captured_at: int
    payload_sha256: str
    provenance_ref: str
    payload: bytes


@dataclass(frozen=True)
class IntelligenceSnapshot:
    query_id: str
    source_revision: str
    captured_at: int
    rows: tuple[Mapping[str, Any], ...]
    evidence: EvidenceRecord
