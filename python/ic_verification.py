"""Evidence-led verification records for instrument connections and ICs.

This module records planned/observed verification evidence. It does not
communicate with instruments, energize hardware, program devices, or authorize
physical operation. A PASS is scoped to the cited test only.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Domain = Literal["instrument_connection", "integrated_circuit"]
Outcome = Literal["not_run", "pass", "fail", "inconclusive"]

INSTRUMENT_CHECKS = (
    "identity_and_tagging",
    "wiring_and_pinout",
    "protective_earth_and_isolation",
    "loop_continuity",
    "signal_range_and_scaling",
    "communications_and_protocol",
    "calibration_traceability",
    "alarm_and_fault_behavior",
    "fail_safe_state",
)
INTEGRATED_CIRCUIT_CHECKS = (
    "part_identity_and_revision",
    "package_pinout",
    "power_rails_and_sequence",
    "supply_current",
    "clock_and_reset",
    "logic_function",
    "timing_and_constraints",
    "interface_compatibility",
    "thermal_and_operating_limits",
)


@dataclass(frozen=True)
class ICVerification:
    verification_id: str
    domain: Domain
    subject_id: str
    check_id: str
    method_ref: str
    evidence_refs: tuple[str, ...] = ()
    outcome: Outcome = "not_run"
    reviewer_ref: str | None = None

    def to_record(self) -> dict[str, object]:
        validate_verification(self)
        return {
            "verification_id": self.verification_id,
            "domain": self.domain,
            "subject_id": self.subject_id,
            "check_id": self.check_id,
            "method_ref": self.method_ref,
            "evidence_refs": list(self.evidence_refs),
            "outcome": self.outcome,
            "reviewer_ref": self.reviewer_ref,
            "scope_note": "PASS applies only to this check and cited evidence",
            "hardware_operated_by_this_record": False,
            "physical_actuation_authorized": False,
            "potability_claim_authorized": False,
            "release_authorized": False,
        }


def validate_verification(item: ICVerification) -> None:
    identifiers = (
        item.verification_id, item.subject_id, item.check_id, item.method_ref
    )
    if any(not isinstance(value, str) or not value.strip() for value in identifiers):
        raise ValueError("verification, subject, check, and method identifiers are required")
    if item.domain not in ("instrument_connection", "integrated_circuit"):
        raise ValueError("domain must be instrument_connection or integrated_circuit")
    checks = INSTRUMENT_CHECKS if item.domain == "instrument_connection" else INTEGRATED_CIRCUIT_CHECKS
    if item.check_id not in checks:
        raise ValueError(f"check_id is not defined for {item.domain}")
    if item.outcome not in ("not_run", "pass", "fail", "inconclusive"):
        raise ValueError("unsupported verification outcome")
    if len(set(item.evidence_refs)) != len(item.evidence_refs):
        raise ValueError("evidence_refs must be unique")
    if any(not ref.strip() for ref in item.evidence_refs):
        raise ValueError("evidence_refs cannot contain empty values")
    if item.outcome == "pass" and (not item.evidence_refs or not item.reviewer_ref):
        raise ValueError("PASS requires evidence references and an independent reviewer")
    if item.reviewer_ref is not None and not item.reviewer_ref.strip():
        raise ValueError("reviewer_ref cannot be empty")


def required_checks(domain: Domain) -> tuple[str, ...]:
    if domain == "instrument_connection":
        return INSTRUMENT_CHECKS
    if domain == "integrated_circuit":
        return INTEGRATED_CIRCUIT_CHECKS
    raise ValueError("unsupported verification domain")


def summarize_verification(
    domain: Domain, records: tuple[ICVerification, ...]
) -> dict[str, object]:
    """Summarize evidence coverage without granting operational/release authority."""
    expected = required_checks(domain)
    selected = [record for record in records if record.domain == domain]
    seen: set[str] = set()
    for record in selected:
        validate_verification(record)
        if record.check_id in seen:
            raise ValueError("duplicate check records are not allowed in one summary")
        seen.add(record.check_id)
    outcomes = {record.check_id: record.outcome for record in selected}
    complete = all(outcomes.get(check) == "pass" for check in expected)
    return {
        "domain": domain,
        "required_checks": list(expected),
        "recorded_checks": len(selected),
        "missing_checks": [check for check in expected if check not in outcomes],
        "nonpassing_checks": [check for check in expected if outcomes.get(check) != "pass"],
        "evidence_complete": complete,
        "release_authorized": False,
        "physical_actuation_authorized": False,
        "potability_claim_authorized": False,
    }
