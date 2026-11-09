"""Opt-in, read-only temporal recall from Stride JOB history.

The adapter is deliberately separate from JobStore and Holified Inception.
Callers must explicitly authorize access and select JOB identifiers. It never
opens a database itself, enumerates every JOB, mutates records, or replays
side effects.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping


class JobHistoryAccessError(PermissionError):
    """Raised when historical access was not explicitly authorized."""


@dataclass(frozen=True)
class HistoricalEvent:
    job_id: str
    sequence: int
    event_type: str
    recorded_at: str
    payload: Mapping[str, Any]
    source_ref: str


@dataclass(frozen=True)
class TemporalContradiction:
    job_id: str
    field: str
    earlier_sequence: int
    earlier_value: Any
    later_sequence: int
    later_value: Any
    status: str = "conflicting_recorded_values"
    interpretation: str = (
        "Both values are preserved. This comparison does not determine "
        "which value is correct."
    )


@dataclass(frozen=True)
class JobHistoryReport:
    events: tuple[HistoricalEvent, ...]
    contradictions: tuple[TemporalContradiction, ...]
    chronology: tuple[str, ...]
    governance: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def recall_job_history(
    store: Any,
    job_ids: Iterable[str],
    *,
    authorized: bool = False,
    reverse: bool = False,
    limit_per_job: int = 500,
) -> JobHistoryReport:
    """Read only selected JOB event ledgers after an explicit opt-in.

    The supplied store must expose get_job(id) and events(id), matching the
    existing JobStore interface. No database path or global discovery is used.
    """
    if authorized is not True:
        raise JobHistoryAccessError(
            "Historical JOB access requires authorized=True from the caller."
        )
    if not callable(getattr(store, "get_job", None)) or not callable(
        getattr(store, "events", None)
    ):
        raise TypeError("store must expose get_job and events read interfaces")
    if isinstance(limit_per_job, bool) or not isinstance(limit_per_job, int) or not 1 <= limit_per_job <= 5000:
        raise ValueError("limit_per_job must be an integer from 1 to 5000")

    selected = tuple(dict.fromkeys(job_ids))
    if not selected or len(selected) > 100:
        raise ValueError("select between 1 and 100 explicit JOB identifiers")

    collected: list[HistoricalEvent] = []
    for job_id in selected:
        if not isinstance(job_id, str) or not job_id.strip():
            raise ValueError("JOB identifiers must be non-empty strings")
        # Validate selection before reading its event ledger.
        store.get_job(job_id)
        rows = store.events(job_id)
        for row in rows[-limit_per_job:]:
            collected.append(HistoricalEvent(
                job_id=job_id,
                sequence=int(row["sequence"]),
                event_type=str(row["event_type"]),
                recorded_at=str(row["created_at"]),
                payload=dict(row["payload"]),
                source_ref=f"job:{job_id}:event:{row['sequence']}",
            ))

    # Preserve event sequence within a JOB; timestamps order across JOBs.
    collected.sort(key=lambda event: (
        event.recorded_at or "", event.job_id, event.sequence
    ))
    if reverse:
        collected.reverse()

    # Compare repeated scalar fields within one JOB only. Nested structures,
    # free text and different JOBs are not asserted to be equivalent.
    by_job_field: dict[tuple[str, str], list[HistoricalEvent]] = defaultdict(list)
    for event in collected:
        for field, value in event.payload.items():
            if value is None or isinstance(value, (dict, list)):
                continue
            by_job_field[(event.job_id, field)].append(event)

    conflicts: list[TemporalContradiction] = []
    for (job_id, field), records in sorted(by_job_field.items()):
        for earlier, later in zip(records, records[1:]):
            if earlier.payload[field] != later.payload[field]:
                conflicts.append(TemporalContradiction(
                    job_id=job_id,
                    field=field,
                    earlier_sequence=earlier.sequence,
                    earlier_value=earlier.payload[field],
                    later_sequence=later.sequence,
                    later_value=later.payload[field],
                ))

    return JobHistoryReport(
        events=tuple(collected),
        contradictions=tuple(conflicts),
        chronology=tuple(event.source_ref for event in collected),
        governance={
            "mode": "explicitly_authorized_read_only_job_history",
            "authorization_required": True,
            "selected_job_ids_only": list(selected),
            "source_mutation": False,
            "event_replay": False,
            "automatic_job_discovery": False,
            "conflicts_resolved_automatically": False,
            "interpretation": "Recorded values are compared, not adjudicated.",
        },
    )
