"""Water equipment inventory contracts; metadata only, with no device I/O.

A declared or reported connection never grants control authority and never
establishes that water is potable. This module intentionally has no transport,
driver, command, pump, valve, or treatment-control implementation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

EquipmentKind = Literal["pump", "valve", "sensor", "treatment"]
ConnectionState = Literal["not_connected", "reported_connected", "unknown"]

EQUIPMENT_KINDS: tuple[str, ...] = ("pump", "valve", "sensor", "treatment")


@dataclass(frozen=True)
class WaterEquipment:
    equipment_id: str
    kind: EquipmentKind
    source_ref: str
    connection_state: ConnectionState = "unknown"
    model: str | None = None
    calibration_ref: str | None = None

    def to_record(self) -> dict[str, object]:
        validate_equipment(self)
        return {
            "equipment_id": self.equipment_id,
            "kind": self.kind,
            "source_ref": self.source_ref,
            "connection_state": self.connection_state,
            "model": self.model,
            "calibration_ref": self.calibration_ref,
            "observation_only": True,
            "control_enabled": False,
            "potability_claim_allowed": False,
            "external_io_performed": False,
        }


def validate_equipment(item: WaterEquipment) -> None:
    if not item.equipment_id.strip() or not item.source_ref.strip():
        raise ValueError("equipment_id and source_ref are required")
    if item.kind not in EQUIPMENT_KINDS:
        raise ValueError(f"kind must be one of: {', '.join(EQUIPMENT_KINDS)}")
    if item.connection_state not in ("not_connected", "reported_connected", "unknown"):
        raise ValueError("unsupported connection_state")
    if item.calibration_ref is not None and not item.calibration_ref.strip():
        raise ValueError("calibration_ref cannot be empty")


def build_equipment_inventory(
    equipment: tuple[WaterEquipment, ...],
) -> list[dict[str, object]]:
    """Build an inventory; reported connections remain non-controlling metadata."""
    seen: set[str] = set()
    records = []
    for item in equipment:
        validate_equipment(item)
        if item.equipment_id in seen:
            raise ValueError("equipment_id values must be unique")
        seen.add(item.equipment_id)
        records.append(item.to_record())
    return records
