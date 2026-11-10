"""Explicit, idempotent bridge from Rise lifecycle revisions to Wisdom records.

The bridge is passive: callers submit already-committed lifecycle events. It never
starts recovery, changes process state, transmits signals, or alters network settings.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib, json, sqlite3, time
from pathlib import Path
from typing import Callable

@dataclass(frozen=True)
class WisdomRevision:
    event_id: str
    process_id: str
    revision: int
    state: str
    event: str
    evidence_summary: str
    created_unix: float

class RiseWisdomBridge:
    def __init__(self, db_path: str | Path,
                 wisdom_sink: Callable[[WisdomRevision], None] | None = None,
                 telemetry_sink: Callable[[WisdomRevision], None] | None = None):
        self.db_path = str(db_path)
        self.wisdom_sink = wisdom_sink
        self.telemetry_sink = telemetry_sink
        with sqlite3.connect(self.db_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS lifecycle_revisions (
                event_id TEXT PRIMARY KEY, process_id TEXT NOT NULL, revision INTEGER NOT NULL,
                state TEXT NOT NULL, event TEXT NOT NULL, evidence_summary TEXT NOT NULL,
                created_unix REAL NOT NULL)""")

    def record_revision(self, process_id: str, revision: int, state: str, event: str,
                        evidence_summary: str = "") -> WisdomRevision:
        if not process_id or len(process_id) > 200 or not state or not event:
            raise ValueError("process_id, state and event are required")
        if not isinstance(revision, int) or revision < 0:
            raise ValueError("revision must be a non-negative integer")
        safe_evidence = str(evidence_summary)[:500]
        identity = f"{process_id}:{revision}:{state}:{event}"
        event_id = hashlib.sha256(identity.encode()).hexdigest()
        record = WisdomRevision(event_id, process_id, revision, state, event,
                                 safe_evidence, time.time())
        with sqlite3.connect(self.db_path) as db:
            cursor = db.execute("INSERT OR IGNORE INTO lifecycle_revisions VALUES (?,?,?,?,?,?,?)",
                (record.event_id, record.process_id, record.revision, record.state,
                 record.event, record.evidence_summary, record.created_unix))
            inserted = cursor.rowcount == 1
        if inserted:
            if self.wisdom_sink:
                self.wisdom_sink(record)
            if self.telemetry_sink:
                self.telemetry_sink(record)
        return record

    def count(self) -> int:
        with sqlite3.connect(self.db_path) as db:
            return int(db.execute("SELECT COUNT(*) FROM lifecycle_revisions").fetchone()[0])

    def export(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as db:
            rows = db.execute("SELECT event_id,process_id,revision,state,event,evidence_summary,created_unix FROM lifecycle_revisions ORDER BY created_unix").fetchall()
        keys = ("event_id","process_id","revision","state","event","evidence_summary","created_unix")
        return [dict(zip(keys, row)) for row in rows]
