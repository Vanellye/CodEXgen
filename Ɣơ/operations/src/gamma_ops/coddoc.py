"""Validator and reader for versioned ERIA .coddoc narrative records."""
from __future__ import annotations
from datetime import datetime
import hashlib
import json
from pathlib import Path
from typing import Any

RUNFLOW_STATES = {
    "DRAFT", "READY", "AUTHORIZED", "RUNNING", "BLOCKED", "UNRESOLVED",
    "REVIEW", "RECOVERY-REQUIRED", "RECOVERED", "COMPLETE", "LEARNED",
}
EVIDENCE_CLASSES = {
    "SOURCE_TEXT", "CODE_REFERENCE", "WORKFLOW_RESULT", "ARTIFACT_REFERENCE",
    "HISTORICAL_REFERENCE", "USER_DEFINED_LABEL", "UNKNOWN",
}

def validate_document(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if document.get("format") != "ERIA_CODDOC":
        errors.append("format must be ERIA_CODDOC")
    if document.get("version") != 1:
        errors.append("version must be 1")
    for key in ("document_id", "title", "narrative", "source_scope"):
        if not isinstance(document.get(key), str) or not document[key].strip():
            errors.append(f"{key} must be a non-empty string")
    if document.get("runflow_state") not in RUNFLOW_STATES:
        errors.append("runflow_state is not a canonical ERIA Runflow state")
    events = document.get("events")
    if not isinstance(events, list) or not events:
        errors.append("events must be a non-empty array")
        return errors
    seen_ids: set[str] = set()
    seen_sequences: set[int] = set()
    for index, event in enumerate(events):
        prefix = f"events[{index}]"
        if not isinstance(event, dict):
            errors.append(f"{prefix} must be an object")
            continue
        event_id = event.get("event_id")
        sequence = event.get("sequence")
        if not isinstance(event_id, str) or not event_id.strip():
            errors.append(f"{prefix}.event_id must be a non-empty string")
        elif event_id in seen_ids:
            errors.append(f"{prefix}.event_id is duplicated")
        else:
            seen_ids.add(event_id)
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
            errors.append(f"{prefix}.sequence must be a positive integer")
        elif sequence in seen_sequences:
            errors.append(f"{prefix}.sequence is duplicated")
        else:
            seen_sequences.add(sequence)
        if event.get("evidence_class") not in EVIDENCE_CLASSES:
            errors.append(f"{prefix}.evidence_class is unknown")
        if event.get("occurred_at") is not None:
            timestamp = event["occurred_at"]
            if not isinstance(timestamp, str):
                errors.append(f"{prefix}.occurred_at must be an ISO-8601 string or null")
            else:
                try:
                    parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    if parsed.tzinfo is None:
                        errors.append(f"{prefix}.occurred_at must include a timezone")
                except ValueError:
                    errors.append(f"{prefix}.occurred_at is not valid ISO-8601")
        refs = event.get("source_refs")
        if not isinstance(refs, list) or not refs or any(not isinstance(ref, str) or not ref.strip() for ref in refs):
            errors.append(f"{prefix}.source_refs must contain one or more non-empty references")
        if not isinstance(event.get("observation"), str) or not event["observation"].strip():
            errors.append(f"{prefix}.observation must be a non-empty string")
        if not isinstance(event.get("interpretation"), str):
            errors.append(f"{prefix}.interpretation must be a string")
    return errors

def load_coddoc(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    raw = source.read_bytes()
    document = json.loads(raw.decode("utf-8"))
    if not isinstance(document, dict):
        raise ValueError(".coddoc root must be a JSON object")
    errors = validate_document(document)
    if errors:
        raise ValueError("; ".join(errors))
    document["_source_path"] = source.as_posix()
    document["_source_sha256"] = hashlib.sha256(raw).hexdigest()
    return document

def ordered_events(document: dict[str, Any]) -> list[dict[str, Any]]:
    """Return authored sequence order; never infer missing timestamps or reorder history."""
    return sorted(document["events"], key=lambda event: event["sequence"])
