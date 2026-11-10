"""Explicitly labeled hypothetical records; not empirical evidence."""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import datetime

_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")
EVIDENCE_STATUS = "not_empirical_evidence"


class HypothesisError(ValueError):
    """A hypothetical record is malformed or misclassified."""


@dataclass(frozen=True)
class HypothesisRecord:
    record_id: str
    topic: str
    claim: str
    assumptions: tuple[str, ...]
    unknowns: tuple[str, ...]
    source_ref: str
    created_at: str
    validation_status: str = "unvalidated"

    def to_envelope(self) -> dict[str, object]:
        validate_hypothesis(self)
        return {
            "record_id": self.record_id,
            "schema_version": 1,
            "source": "hypothesis_catalog",
            "observed_at": self.created_at,
            "payload": {
                "topic": self.topic,
                "claim": self.claim,
                "assumptions": list(self.assumptions),
                "unknowns": list(self.unknowns),
                "validation_status": self.validation_status,
                "evidence_status": EVIDENCE_STATUS,
            },
            "units": {},
            "quality": "UNKNOWN",
            "provenance": {"source_ref": self.source_ref, "signature_status": "not_present"},
            "transformations": [],
            "authorization": {"status": "not_authorized", "scope": [], "approval_ref": None},
            "validation": {"status": self.validation_status},
            "retention": {"policy": "preserve_original"},
        }


def validate_hypothesis(record: HypothesisRecord) -> None:
    if not _IDENTIFIER.fullmatch(record.record_id):
        raise HypothesisError("record_id must be a stable identifier")
    for field, value in (("topic", record.topic), ("claim", record.claim), ("source_ref", record.source_ref)):
        if not isinstance(value, str) or not value.strip():
            raise HypothesisError(f"{field} must be non-empty text")
    try:
        parsed = datetime.fromisoformat(record.created_at.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise HypothesisError("created_at must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise HypothesisError("created_at must include a timezone")
    if record.validation_status not in {"unvalidated", "requires_review"}:
        raise HypothesisError("hypotheses cannot self-promote to validated evidence")
    if not all(isinstance(item, str) and item.strip() for item in record.assumptions):
        raise HypothesisError("assumptions must contain non-empty text")
    if not all(isinstance(item, str) and item.strip() for item in record.unknowns):
        raise HypothesisError("unknowns must contain non-empty text")
