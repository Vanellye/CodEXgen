"""Branch-specific provenance boundary for narrative research artifacts.

This module labels fictional material without asserting empirical validity.
It does not evaluate, authorize, or promote scientific claims.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass

BRANCH_DOMAIN = "body"
CLASSIFICATION = "fiction"
EVIDENCE_STATUS = "not_empirical_evidence"
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")


class FictionArtifactError(ValueError):
    """Invalid narrative artifact metadata."""


@dataclass(frozen=True)
class FictionArtifact:
    artifact_id: str
    domain: str
    source_path: str
    content_sha256: str
    classification: str = CLASSIFICATION
    evidence_status: str = EVIDENCE_STATUS

    def to_record(self) -> dict[str, str]:
        validate_artifact(self)
        return asdict(self)


def create_artifact(artifact_id: str, source_path: str, content: str) -> FictionArtifact:
    """Create a content-addressed fiction record for this branch's domain."""
    if not isinstance(content, str):
        raise FictionArtifactError("content must be text")
    if not isinstance(source_path, str) or not source_path.strip():
        raise FictionArtifactError("source_path must be non-empty")
    record = FictionArtifact(
        artifact_id=artifact_id,
        domain=BRANCH_DOMAIN,
        source_path=source_path,
        content_sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
    )
    validate_artifact(record)
    return record


def validate_artifact(record: FictionArtifact) -> None:
    if not _IDENTIFIER.fullmatch(record.artifact_id):
        raise FictionArtifactError("artifact_id must be a stable identifier")
    if record.domain != BRANCH_DOMAIN:
        raise FictionArtifactError("artifact domain does not match this branch identity")
    if not record.source_path or "\x00" in record.source_path:
        raise FictionArtifactError("source_path must be a non-empty path")
    if not re.fullmatch(r"[0-9a-f]{64}", record.content_sha256):
        raise FictionArtifactError("content_sha256 must be lowercase SHA-256")
    if record.classification != CLASSIFICATION:
        raise FictionArtifactError("fiction artifacts cannot self-promote to another classification")
    if record.evidence_status != EVIDENCE_STATUS:
        raise FictionArtifactError("fiction artifacts are not empirical evidence")
