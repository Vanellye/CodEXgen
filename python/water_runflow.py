"""Water-management runflow as a data-only hypothetical simulation.

No sensors, pumps, valves, treatment equipment, or external services are controlled.
Quality observations are recorded, never interpreted as proof of potability.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from codexgen_contracts.envelope import validate_record

STAGES = ("collection", "treatment", "storage", "distribution", "reuse")


@dataclass(frozen=True)
class WaterFlowStep:
    record_id: str
    stage: str
    parent_record_id: str | None
    source_ref: str
    observed_at: str
    volume_value: float | None = None
    volume_unit: str | None = None
    quality_observation: str = "unknown"

    def to_envelope(self) -> dict[str, object]:
        validate_water_step(self)
        return validate_record({
            "record_id": self.record_id,
            "schema_version": 1,
            "source": "water_runflow.simulation",
            "observed_at": self.observed_at,
            "payload": {
                "domain": "water",
                "stage": self.stage,
                "parent_record_id": self.parent_record_id,
                "quality_observation": self.quality_observation,
                "simulation_only": True,
                "physical_actuation_allowed": False,
                "potability_determined": False,
            },
            "units": ({"volume": self.volume_unit} if self.volume_unit else {}),
            "quality": "UNKNOWN",
            "provenance": {
                "source_ref": self.source_ref,
                "signature_status": "not_present",
            },
            "transformations": [],
            "authorization": {
                "status": "not_authorized",
                "scope": [],
                "approval_ref": None,
            },
            "validation": {"status": "unvalidated"},
            "retention": {"policy": "preserve_original"},
        })


def validate_water_step(step: WaterFlowStep) -> None:
    if step.stage not in STAGES:
        raise ValueError(f"stage must be one of: {', '.join(STAGES)}")
    if not step.record_id or not step.source_ref:
        raise ValueError("record_id and source_ref are required")
    if step.parent_record_id == step.record_id:
        raise ValueError("a water-flow step cannot parent itself")
    try:
        parsed = datetime.fromisoformat(step.observed_at.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise ValueError("observed_at must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("observed_at must include a timezone")
    if (step.volume_value is None) != (step.volume_unit is None):
        raise ValueError("volume_value and volume_unit must be supplied together")
    if step.volume_value is not None and step.volume_value < 0:
        raise ValueError("volume_value cannot be negative")
    if step.volume_unit is not None and not step.volume_unit.strip():
        raise ValueError("volume_unit cannot be empty")
    if not step.quality_observation.strip():
        raise ValueError("quality_observation cannot be empty")


def build_water_runflow(steps: tuple[WaterFlowStep, ...]) -> list[dict[str, object]]:
    """Validate a linear stage sequence; missing stages are allowed but order is fixed."""
    previous_index = -1
    previous_id: str | None = None
    envelopes = []
    for step in steps:
        validate_water_step(step)
        index = STAGES.index(step.stage)
        if index <= previous_index:
            raise ValueError("water stages must be unique and follow the defined order")
        if previous_id is not None and step.parent_record_id != previous_id:
            raise ValueError("each step must reference the immediately preceding step")
        if previous_id is None and step.parent_record_id is not None:
            raise ValueError("first step must not reference a prior step")
        envelopes.append(step.to_envelope())
        previous_index = index
        previous_id = step.record_id
    return envelopes
