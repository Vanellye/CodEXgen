"""Deterministic scheduled allowance proposal preparation.

No timers, unattended jobs, persistent grants, or money movement occur here.
A scheduler may call prepare_due_occurrence; independent approval stays separate.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from allowance import AllowancePolicy, BalanceEvidence, BeneficiaryRequest, prepare_hybrid_allocation


class ScheduleHold(Exception):
    pass


@dataclass(frozen=True)
class ScheduledAllowance:
    schedule_id: str
    interval_seconds: int
    starts_at: str
    ends_at: str
    policy: AllowancePolicy


def prepare_due_occurrence(schedule: ScheduledAllowance, occurrence_number: int,
                           balances: list[BalanceEvidence],
                           beneficiaries: list[BeneficiaryRequest],
                           already_allocated_minor: int = 0,
                           beneficiary_period_usage: dict[str, int] | None = None,
                           now: datetime | None = None) -> dict:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if not schedule.schedule_id or schedule.interval_seconds <= 0 or occurrence_number < 0:
        raise ScheduleHold("schedule identity, positive interval, and valid occurrence required")
    try:
        starts = datetime.fromisoformat(schedule.starts_at.replace("Z", "+00:00"))
        ends = datetime.fromisoformat(schedule.ends_at.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise ScheduleHold("invalid schedule timestamps") from exc
    if starts.tzinfo is None or ends.tzinfo is None or ends <= starts:
        raise ScheduleHold("schedule boundaries must be timezone-aware and ordered")
    due_at = starts.astimezone(timezone.utc).timestamp() + occurrence_number * schedule.interval_seconds
    if now.timestamp() < due_at:
        raise ScheduleHold("scheduled occurrence is not due")
    if now > ends.astimezone(timezone.utc):
        raise ScheduleHold("schedule has expired")
    proposal = prepare_hybrid_allocation(
        schedule.policy, balances, beneficiaries,
        already_allocated_minor=already_allocated_minor,
        beneficiary_period_usage=beneficiary_period_usage, now=now)
    proposal["schedule"] = {
        "schedule_id": schedule.schedule_id,
        "occurrence_number": occurrence_number,
        "interval_seconds": schedule.interval_seconds,
        "due_at": datetime.fromtimestamp(due_at, timezone.utc).isoformat(),
    }
    proposal["status"] = "SCHEDULED_PROPOSAL_AWAITING_INDEPENDENT_APPROVAL"
    proposal.pop("proposal_sha256", None)
    canonical = json.dumps(proposal, sort_keys=True, separators=(",", ":"))
    proposal["proposal_sha256"] = sha256(canonical.encode("utf-8")).hexdigest()
    return proposal
