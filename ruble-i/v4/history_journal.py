"""Append-only JSONL event journal; production needs external checkpointing."""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
from datetime import datetime, timezone


class HistoryIntegrityError(Exception):
    pass


def _canonical(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def append_event(path: str, event: dict) -> dict:
    """Append one event with previous hash; never edits earlier records."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    previous = None
    if target.exists():
        records = [line for line in target.read_text(encoding="utf-8").splitlines() if line]
        if records:
            previous = json.loads(records[-1])["event_hash"]
    record = dict(event)
    record.setdefault("occurred_at", datetime.now(timezone.utc).isoformat())
    record["previous_event_hash"] = previous
    record.pop("event_hash", None)
    record["event_hash"] = sha256(_canonical(record)).hexdigest()
    # O_APPEND ensures writes append rather than truncate. External locking is
    # still required for concurrent multi-process writers.
    fd = os.open(str(target), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        os.write(fd, _canonical(record) + b"\n")
        os.fsync(fd)
    finally:
        os.close(fd)
    return record


def verify_journal(path: str) -> bool:
    previous = None
    try:
        with open(path, "r", encoding="utf-8") as stream:
            for line in stream:
                if not line.strip():
                    continue
                record = json.loads(line)
                actual = record.pop("event_hash")
                if record.get("previous_event_hash") != previous:
                    return False
                expected = sha256(_canonical(record)).hexdigest()
                if actual != expected:
                    return False
                previous = actual
        return True
    except Exception:
        return False
