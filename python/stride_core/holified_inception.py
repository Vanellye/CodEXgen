"""Holified Inception: an independent, evidence-aware context reader.

This module composes supplied context with existing Stride perception and
creativity helpers. It does not replace those helpers, access external systems,
persist data, or perform consequential actions.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Any, Iterable, Mapping, Optional

from .faculty_engine import assess_perception, generate_ideas


EVIDENCE_LABELS = {
    "observed", "verified", "inferred", "hypothesis",
    "simulated", "fictional", "unknown", "disputed", "recorded",
}


class HolifiedInputError(ValueError):
    """Raised when contextual input is malformed or exceeds safe bounds."""


@dataclass(frozen=True)
class ContextItem:
    """A source-bearing piece of context; content is never silently upgraded."""
    item_id: str
    content: str
    evidence: str = "observed"
    source: str = "user_input"
    relates_to: tuple[str, ...] = ()


@dataclass(frozen=True)
class ContextLink:
    source_id: str
    target_id: str
    relationship: str
    evidence: str


@dataclass(frozen=True)
class HolifiedReport:
    present: str
    origins: tuple[dict[str, str], ...]
    connections: tuple[ContextLink, ...]
    tensions: tuple[str, ...]
    possibilities: tuple[str, ...]
    discernment: tuple[dict[str, str], ...]
    return_summary: str
    next_steps: tuple[str, ...]
    perception: Optional[dict[str, Any]]
    creativity_seed: Optional[str]
    governance: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _required_text(name: str, value: Any, limit: int) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise HolifiedInputError(
            f"{name} must be a non-empty string no longer than {limit} characters"
        )
    return value.strip()


def _normalize_items(items: Iterable[ContextItem | Mapping[str, Any]]) -> tuple[ContextItem, ...]:
    normalized = []
    seen = set()
    for raw in items:
        if isinstance(raw, ContextItem):
            item = raw
        elif isinstance(raw, Mapping):
            item = ContextItem(
                item_id=raw.get("item_id", ""),
                content=raw.get("content", ""),
                evidence=raw.get("evidence", "observed"),
                source=raw.get("source", "unspecified"),
                relates_to=tuple(raw.get("relates_to", ())),
            )
        else:
            raise HolifiedInputError("context items must be ContextItem or mappings")

        item_id = _required_text("item_id", item.item_id, 120)
        content = _required_text("content", item.content, 4000)
        source = _required_text("source", item.source, 500)
        if item_id in seen:
            raise HolifiedInputError(f"duplicate context item_id: {item_id}")
        if item.evidence not in EVIDENCE_LABELS:
            raise HolifiedInputError(f"unsupported evidence label: {item.evidence}")
        if not isinstance(item.relates_to, tuple) or any(
            not isinstance(x, str) or not x.strip() for x in item.relates_to
        ):
            raise HolifiedInputError("relates_to must be a tuple of non-empty identifiers")
        seen.add(item_id)
        normalized.append(ContextItem(
            item_id, content, item.evidence, source, item.relates_to
        ))
        if len(normalized) > 128:
            raise HolifiedInputError("at most 128 context items are supported")
    return tuple(normalized)


def read_beyond_present(
    present: str,
    context: Iterable[ContextItem | Mapping[str, Any]] = (),
    observations: Optional[dict[str, float]] = None,
    creative_concepts: Iterable[str] = (),
) -> HolifiedReport:
    """Build an evidence-labeled context view without changing source records.

    Connections are emitted only when explicitly referenced by a context item.
    Creative combinations are suggestions and always remain hypothetical.
    """
    present_text = _required_text("present", present, 8000)
    items = _normalize_items(context)
    by_id = {item.item_id: item for item in items}

    origins = tuple({
        "item_id": item.item_id,
        "source": item.source,
        "evidence": item.evidence,
        "content": item.content,
    } for item in items)

    links = []
    tensions = []
    for item in items:
        for target_id in item.relates_to:
            if target_id not in by_id:
                tensions.append(
                    f"{item.item_id} references unavailable context {target_id}; relationship remains unknown."
                )
                continue
            target = by_id[target_id]
            relationship_evidence = (
                "observed" if item.evidence in {"observed", "verified"}
                and target.evidence in {"observed", "verified"} else "inferred"
            )
            links.append(ContextLink(
                item.item_id, target_id, "explicit_context_reference",
                relationship_evidence,
            ))
        if item.evidence in {"unknown", "disputed"}:
            tensions.append(
                f"{item.item_id} is labeled {item.evidence}; do not treat it as settled."
            )

    perception = None
    if observations is not None:
        if not isinstance(observations, dict) or not observations:
            raise HolifiedInputError("observations must be a non-empty mapping when supplied")
        perception = asdict(assess_perception(observations))

    concepts = tuple(creative_concepts)
    possibilities = ()
    creativity_seed = None
    if concepts:
        ideas = generate_ideas(concepts)
        possibilities = tuple(
            f"[hypothesis] {idea}" for idea in ideas.combinations
        )
        creativity_seed = ideas.seed_digest

    discernment = tuple({
        "item_id": item.item_id,
        "status": item.evidence,
        "source": item.source,
        "interpretation": (
            "Evidence-labeled context; retain its original status."
            if item.evidence in {"observed", "verified"}
            else "Do not present this item as independently established."
        ),
    } for item in items)

    if not items:
        tensions.append("No additional context was supplied; analysis is limited to the present input.")
    if not possibilities:
        possibilities = ("No speculative possibilities generated.",)

    summary = (
        f"Read the present input with {len(items)} supplied context item(s), "
        f"{len(links)} explicit connection(s), and {len(tensions)} unresolved "
        "context warning(s). Original context was not modified."
    )
    next_steps = (
        "Review source references and unresolved context warnings.",
        "Supply missing context only when it is available and authorized.",
        "Keep generated possibilities separate from observed or verified records.",
    )

    return HolifiedReport(
        present=present_text,
        origins=origins,
        connections=tuple(links),
        tensions=tuple(tensions),
        possibilities=possibilities,
        discernment=discernment,
        return_summary=summary,
        next_steps=next_steps,
        perception=perception,
        creativity_seed=creativity_seed,
        governance={
            "mode": "read_only_context_analysis",
            "source_mutation": False,
            "external_actions": False,
            "fiction_promoted_to_fact": False,
            "human_review_recommended": True,
            "limitations": "Only supplied context and local Stride faculty helpers are used.",
        },
    )



@dataclass(frozen=True)
class HolifiedTemporalReport:
    """A supplied-context reading plus separately retained JOB history."""
    reading: HolifiedReport
    history: Any
    historical_context: tuple[ContextItem, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "reading": self.reading.to_dict(),
            "history": self.history.to_dict(),
            "historical_context": [asdict(item) for item in self.historical_context],
        }


def read_with_job_history(
    present: str,
    store: Any,
    job_ids: Iterable[str],
    *,
    authorized: bool = False,
    context: Iterable[ContextItem | Mapping[str, Any]] = (),
    observations: Optional[dict[str, float]] = None,
    creative_concepts: Iterable[str] = (),
    reverse: bool = False,
    limit_per_job: int = 500,
) -> HolifiedTemporalReport:
    """Optionally add explicitly authorized, read-only JOB event history.

    JOB history is fetched only when this function is called with
    authorized=True and explicit JOB identifiers. The original reader remains
    independently usable with supplied context alone.
    """
    from .job_history import recall_job_history

    history = recall_job_history(
        store,
        job_ids,
        authorized=authorized,
        reverse=reverse,
        limit_per_job=limit_per_job,
    )
    historical = tuple(
        ContextItem(
            item_id=f"job-history:{event.job_id}:{event.sequence}",
            content=json.dumps({
                "event_type": event.event_type,
                "recorded_at": event.recorded_at,
                "payload": dict(event.payload),
                "source_ref": event.source_ref,
            }, ensure_ascii=False, sort_keys=True),
            evidence="recorded",
            source=event.source_ref,
        )
        for event in history.events
    )
    supplied = tuple(context)
    reading = read_beyond_present(
        present,
        (*supplied, *historical),
        observations=observations,
        creative_concepts=creative_concepts,
    )
    return HolifiedTemporalReport(
        reading=reading,
        history=history,
        historical_context=historical,
    )
