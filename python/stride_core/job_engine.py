"""Local-first JOB engine for Stride.

A JOB is a Journey of Becoming, not an occupational assignment. This module
provides SQLite persistence, explicit lifecycle transitions, branch lineage,
append-only event records, and purpose-scoped numerical observations.

It does not execute external actions, infer consent, score human worth, or
automatically publish or delete user data.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import math
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Optional


class JobError(ValueError):
    """Invalid JOB input or lifecycle operation."""


STATES = {"open", "active", "paused", "blocked", "adapted", "completed", "archived"}
STAGES = {"notice", "orient", "choose", "make", "examine", "adapt", "carry_forward"}
TRANSITIONS = {
    "open": {"active", "paused", "blocked", "adapted", "completed", "archived"},
    "active": {"paused", "blocked", "adapted", "completed"},
    "paused": {"active", "blocked", "adapted", "completed", "archived"},
    "blocked": {"active", "paused", "adapted", "archived"},
    "adapted": {"active", "paused", "blocked", "completed"},
    "completed": {"active", "archived"},
    "archived": set(),
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _text(name: str, value: Any, limit: int = 2000) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise JobError(f"{name} must be a non-empty string up to {limit} characters")
    return value.strip()


def _json(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise JobError("value must be JSON-serializable and contain no NaN or infinity") from exc


@dataclass(frozen=True)
class JobMetric:
    name: str
    value: float
    unit: str
    method: str
    window: str
    source: str
    limitations: str


class JobStore:
    """SQLite-backed local JOB store. Each mutation is committed atomically."""

    def __init__(self, database: str | Path = "stride_jobs.sqlite3") -> None:
        self.database = str(database)
        if self.database != ":memory:":
            Path(self.database).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database, timeout=10.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    origin TEXT NOT NULL,
                    parent_id TEXT REFERENCES jobs(id),
                    stage TEXT NOT NULL,
                    state TEXT NOT NULL,
                    path_json TEXT NOT NULL,
                    constraints_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS jobs_parent_idx ON jobs(parent_id);
                CREATE TABLE IF NOT EXISTS job_events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL REFERENCES jobs(id),
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS job_events_job_idx
                    ON job_events(job_id, sequence);
                CREATE TABLE IF NOT EXISTS job_metrics (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL REFERENCES jobs(id),
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    method TEXT NOT NULL,
                    window TEXT NOT NULL,
                    source TEXT NOT NULL,
                    limitations TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS job_metrics_job_idx
                    ON job_metrics(job_id, sequence);
            """)

    def _event(self, db: sqlite3.Connection, job_id: str, kind: str,
               payload: dict[str, Any]) -> None:
        db.execute(
            "INSERT INTO job_events(job_id,event_type,payload_json,created_at) VALUES(?,?,?,?)",
            (job_id, kind, _json(payload), _now()),
        )

    def create_job(self, title: str, purpose: str, origin: str,
                   path: Optional[list[str]] = None,
                   constraints: Optional[list[str]] = None,
                   parent_id: Optional[str] = None,
                   job_id: Optional[str] = None) -> dict[str, Any]:
        title = _text("title", title, 200)
        purpose = _text("purpose", purpose)
        origin = _text("origin", origin, 200)
        path = [] if path is None else path
        constraints = [] if constraints is None else constraints
        if not isinstance(path, list) or any(not isinstance(x, str) or not x.strip() for x in path):
            raise JobError("path must be a list of non-empty strings")
        if not isinstance(constraints, list) or any(not isinstance(x, str) or not x.strip() for x in constraints):
            raise JobError("constraints must be a list of non-empty strings")
        identifier = job_id or str(uuid.uuid4())
        _text("job_id", identifier, 128)
        now = _now()
        with self._connect() as db:
            if parent_id is not None and not db.execute(
                    "SELECT 1 FROM jobs WHERE id=?", (parent_id,)).fetchone():
                raise JobError("parent JOB does not exist")
            db.execute("""INSERT INTO jobs
                (id,title,purpose,origin,parent_id,stage,state,path_json,constraints_json,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                (identifier, title, purpose, origin, parent_id, "notice", "open",
                 _json(path), _json(constraints), now, now))
            self._event(db, identifier, "created", {
                "title": title, "purpose": purpose, "origin": origin, "parent_id": parent_id
            })
        return self.get_job(identifier)

    def get_job(self, job_id: str) -> dict[str, Any]:
        with self._connect() as db:
            row = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if row is None:
            raise JobError("JOB not found")
        result = dict(row)
        result["path"] = json.loads(result.pop("path_json"))
        result["constraints"] = json.loads(result.pop("constraints_json"))
        return result

    def list_children(self, parent_id: str) -> list[dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute("SELECT id FROM jobs WHERE parent_id=? ORDER BY created_at,id",
                              (parent_id,)).fetchall()
        return [self.get_job(row["id"]) for row in rows]

    def transition(self, job_id: str, new_state: str, stage: Optional[str] = None,
                   reason: str = "", reopen: bool = False) -> dict[str, Any]:
        if new_state not in STATES:
            raise JobError("unsupported JOB state")
        if stage is not None and stage not in STAGES:
            raise JobError("unsupported lifecycle stage")
        reason = reason.strip() if isinstance(reason, str) else ""
        with self._connect() as db:
            row = db.execute("SELECT state,stage FROM jobs WHERE id=?", (job_id,)).fetchone()
            if row is None:
                raise JobError("JOB not found")
            current = row["state"]
            if current == "completed" and new_state == "active" and not reopen:
                raise JobError("reopening a completed JOB requires reopen=True")
            if new_state not in TRANSITIONS[current]:
                raise JobError(f"transition {current} -> {new_state} is not allowed")
            now = _now()
            next_stage = stage or row["stage"]
            db.execute("UPDATE jobs SET state=?,stage=?,updated_at=? WHERE id=?",
                       (new_state, next_stage, now, job_id))
            self._event(db, job_id, "transitioned", {
                "from": current, "to": new_state, "stage": next_stage,
                "reason": reason, "reopened": bool(reopen and current == "completed")
            })
        return self.get_job(job_id)

    def add_branch(self, parent_id: str, title: str, purpose: str,
                   origin: Optional[str] = None, path: Optional[list[str]] = None,
                   constraints: Optional[list[str]] = None) -> dict[str, Any]:
        parent = self.get_job(parent_id)
        return self.create_job(title, purpose, origin or f"branch:{parent_id}",
                               path, constraints, parent_id=parent_id)

    def record_metric(self, job_id: str, metric: JobMetric) -> JobMetric:
        if not isinstance(metric, JobMetric):
            raise JobError("metric must be a JobMetric")
        name = _text("metric.name", metric.name, 100)
        unit = _text("metric.unit", metric.unit, 40)
        method = _text("metric.method", metric.method, 500)
        window = _text("metric.window", metric.window, 120)
        source = _text("metric.source", metric.source, 300)
        limitations = _text("metric.limitations", metric.limitations, 1000)
        if isinstance(metric.value, bool) or not isinstance(metric.value, (int, float)) or not math.isfinite(metric.value):
            raise JobError("metric.value must be a finite number")
        with self._connect() as db:
            if not db.execute("SELECT 1 FROM jobs WHERE id=?", (job_id,)).fetchone():
                raise JobError("JOB not found")
            created = _now()
            db.execute("""INSERT INTO job_metrics
                (job_id,name,value,unit,method,window,source,limitations,created_at)
                VALUES(?,?,?,?,?,?,?,?,?)""",
                (job_id, name, float(metric.value), unit, method, window, source, limitations, created))
            self._event(db, job_id, "metric_recorded", {
                "name": name, "value": float(metric.value), "unit": unit,
                "method": method, "window": window, "source": source,
                "limitations": limitations
            })
        return JobMetric(name, float(metric.value), unit, method, window, source, limitations)

    def list_metrics(self, job_id: str) -> list[JobMetric]:
        self.get_job(job_id)
        with self._connect() as db:
            rows = db.execute("""SELECT name,value,unit,method,window,source,limitations
                FROM job_metrics WHERE job_id=? ORDER BY sequence""", (job_id,)).fetchall()
        return [JobMetric(**dict(row)) for row in rows]

    def events(self, job_id: str) -> list[dict[str, Any]]:
        self.get_job(job_id)
        with self._connect() as db:
            rows = db.execute("""SELECT sequence,event_type,payload_json,created_at
                FROM job_events WHERE job_id=? ORDER BY sequence""", (job_id,)).fetchall()
        return [{**dict(row), "payload": json.loads(row["payload_json"])}
                for row in rows]
