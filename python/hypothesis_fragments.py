"""Mini-bigger placeholder records linked to parent hypotheticals.

These are structural placeholders only: they do not assert evidence, execute code,
or authorize runtime changes.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from hypothesis_contract import HypothesisRecord, validate_hypothesis

_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")


@dataclass(frozen=True)
class MiniBiggerRecord:
    """A small placeholder representing one part of a larger hypothetical."""

    record_id: str
    parent_record_id: str
    label: str
    description: str
    source_ref: str
    created_at: str

    def to_envelope(self) -> dict[str, object]:
        validate_mini_bigger(self)
        base = HypothesisRecord(
            record_id=self.record_id,
            topic="mini-bigger-placeholder",
            claim=self.description,
            assumptions=("placeholder structure only",),
            unknowns=("parent hypothesis remains unvalidated",),
            source_ref=self.source_ref,
            created_at=self.created_at,
        ).to_envelope()
        base["source"] = "hypothesis_catalog.mini_bigger"
        base["payload"].update({
            "record_kind": "mini_bigger",
            "label": self.label,
            "parent_record_id": self.parent_record_id,
            "relationship": "placeholder_child_of",
            "is_placeholder": True,
            "runtime_injection_allowed": False,
        })
        return base


def validate_mini_bigger(record: MiniBiggerRecord) -> None:
    if not _IDENTIFIER.fullmatch(record.record_id):
        raise ValueError("record_id must be a stable identifier")
    if not _IDENTIFIER.fullmatch(record.parent_record_id):
        raise ValueError("parent_record_id must be a stable identifier")
    if record.record_id == record.parent_record_id:
        raise ValueError("a mini-bigger cannot be its own parent")
    for field, value in (
        ("label", record.label),
        ("description", record.description),
        ("source_ref", record.source_ref),
    ):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be non-empty text")
    # Reuse the parent hypothesis contract for timestamp and non-evidence rules.
    validate_hypothesis(HypothesisRecord(
        record_id=record.record_id,
        topic="mini-bigger-placeholder",
        claim=record.description,
        assumptions=("placeholder structure only",),
        unknowns=("parent hypothesis remains unvalidated",),
        source_ref=record.source_ref,
        created_at=record.created_at,
    ))
