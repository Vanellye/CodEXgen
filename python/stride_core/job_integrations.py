"""JOB integrations for Stride: Faculty Engine, Geometry Lab, snapshots and recovery.

The Main is a shared index, not an owner. JOBs and their artifacts retain
independent identifiers, attribution, provenance, and exportable history.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from stride_core.faculty_engine import run_faculty_suite
from stride_core.job_engine import JobError, JobStore

SNAPSHOT_SCHEMA = "codexgen.stride.job-snapshot.v1"
GEOMETRY_SCHEMA = "codexgen-geometry-experiment-v1"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _ensure_artifacts(store: JobStore) -> None:
    with store._connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS job_artifacts (
            id TEXT PRIMARY KEY,
            job_id TEXT NOT NULL REFERENCES jobs(id),
            kind TEXT NOT NULL,
            title TEXT NOT NULL,
            content_json TEXT NOT NULL,
            sha256 TEXT NOT NULL,
            created_at TEXT NOT NULL
        )""")
        db.execute("CREATE INDEX IF NOT EXISTS job_artifacts_job_idx ON job_artifacts(job_id)")


def attach_artifact(store: JobStore, job_id: str, kind: str,
                    title: str, content: dict[str, Any]) -> dict[str, Any]:
    """Attach a JSON artifact with canonical digest and provenance to a JOB."""
    _ensure_artifacts(store)
    store.get_job(job_id)
    if not isinstance(content, dict):
        raise JobError("artifact content must be a JSON object")
    kind = str(kind).strip()
    title = str(title).strip()
    if not kind or len(kind) > 80 or not title or len(title) > 200:
        raise JobError("artifact kind/title is invalid")
    encoded = _canonical(content)
    digest = hashlib.sha256(encoded).hexdigest()
    import uuid
    from datetime import datetime, timezone
    artifact_id = str(uuid.uuid4())
    created = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with store._connect() as db:
        db.execute("""INSERT INTO job_artifacts
            (id,job_id,kind,title,content_json,sha256,created_at)
            VALUES(?,?,?,?,?,?,?)""",
            (artifact_id, job_id, kind, title, encoded.decode("utf-8"), digest, created))
        store._event(db, job_id, "artifact_attached", {
            "artifact_id": artifact_id, "kind": kind, "title": title, "sha256": digest
        })
    return {"id": artifact_id, "job_id": job_id, "kind": kind,
            "title": title, "sha256": digest, "created_at": created}


def connect_faculty_run(store: JobStore, job_id: str,
                        observations: dict[str, float], concepts: list[str],
                        prediction: float, measured: float,
                        channels: list[dict[str, Any]]) -> dict[str, Any]:
    """Run the existing Faculty Engine and attach its reviewable report to a JOB."""
    report = run_faculty_suite(observations, concepts, prediction, measured, channels)
    artifact = attach_artifact(store, job_id, "faculty_engine_report",
                               "Stride Faculty Engine report", report)
    return {"artifact": artifact, "report": report}


def connect_geometry_experiment(store: JobStore, job_id: str,
                                experiment: dict[str, Any]) -> dict[str, Any]:
    """Validate and attach a Geometry Lab JSON experiment to a JOB."""
    if not isinstance(experiment, dict) or experiment.get("schema") != GEOMETRY_SCHEMA:
        raise JobError("unsupported Geometry Laboratory experiment schema")
    linked_job = experiment.get("linkedJobId")
    if linked_job and linked_job != job_id:
        raise JobError("experiment is linked to a different JOB ID")
    if experiment.get("workspace") not in {"curvature", "fractal", "coordinates", "projection"}:
        raise JobError("unsupported Geometry Laboratory workspace")
    if not isinstance(experiment.get("parameters"), dict):
        raise JobError("experiment parameters are required")
    if not isinstance(experiment.get("diagram", ""), str):
        raise JobError("experiment diagram must be SVG text")
    if len(_canonical(experiment)) > 2_000_000:
        raise JobError("experiment exceeds the 2 MB attachment limit")
    return attach_artifact(store, job_id, "geometry_experiment",
                           str(experiment.get("title") or "Geometry experiment")[:200],
                           experiment)


def list_artifacts(store: JobStore, job_id: str) -> list[dict[str, Any]]:
    _ensure_artifacts(store)
    store.get_job(job_id)
    with store._connect() as db:
        rows = db.execute("""SELECT id,job_id,kind,title,content_json,sha256,created_at
            FROM job_artifacts WHERE job_id=? ORDER BY created_at,id""", (job_id,)).fetchall()
    result = []
    for row in rows:
        content = json.loads(row["content_json"])
        actual = hashlib.sha256(_canonical(content)).hexdigest()
        if actual != row["sha256"]:
            raise JobError("stored artifact digest mismatch")
        result.append({"id": row["id"], "job_id": row["job_id"], "kind": row["kind"],
                       "title": row["title"], "content": content, "sha256": actual,
                       "created_at": row["created_at"]})
    return result


def export_job_snapshot(store: JobStore, job_id: str) -> str:
    """Create a deterministic, integrity-checked JSON recovery package."""
    job = store.get_job(job_id)
    events = store.events(job_id)
    metrics = [vars(x) for x in store.list_metrics(job_id)]
    artifacts = list_artifacts(store, job_id)
    payload = {"schema": SNAPSHOT_SCHEMA, "format_version": 1,
               "job": job, "events": events, "metrics": metrics, "artifacts": artifacts}
    digest = hashlib.sha256(_canonical(payload)).hexdigest()
    return json.dumps({"payload": payload, "sha256": digest},
                      ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)


def import_job_snapshot(store: JobStore, snapshot: str | dict[str, Any]) -> dict[str, Any]:
    """Verify a snapshot then restore it without overwriting any existing JOB."""
    try:
        envelope = json.loads(snapshot) if isinstance(snapshot, str) else snapshot
        payload = envelope["payload"]
        supplied = envelope["sha256"]
    except (TypeError, KeyError, json.JSONDecodeError) as exc:
        raise JobError("invalid JOB snapshot envelope") from exc
    actual = hashlib.sha256(_canonical(payload)).hexdigest()
    if not isinstance(supplied, str) or supplied != actual:
        raise JobError("snapshot integrity check failed")
    if payload.get("schema") != SNAPSHOT_SCHEMA or payload.get("format_version") != 1:
        raise JobError("unsupported JOB snapshot version")
    job = payload.get("job")
    if not isinstance(job, dict) or not job.get("id"):
        raise JobError("snapshot has no valid JOB record")
    events = payload.get("events", [])
    metrics = payload.get("metrics", [])
    artifacts = payload.get("artifacts", [])
    if not all(isinstance(x, list) for x in (events, metrics, artifacts)):
        raise JobError("snapshot collections must be arrays")
    if len(events) > 100000 or len(metrics) > 100000 or len(artifacts) > 10000:
        raise JobError("snapshot exceeds recovery limits")
    if job.get("state") not in {"open", "active", "paused", "blocked", "adapted", "completed", "archived"}:
        raise JobError("snapshot contains an invalid JOB state")
    if job.get("stage") not in {"notice", "orient", "choose", "make", "examine", "adapt", "carry_forward"}:
        raise JobError("snapshot contains an invalid JOB stage")
    _ensure_artifacts(store)
    with store._connect() as db:
        if db.execute("SELECT 1 FROM jobs WHERE id=?", (job["id"],)).fetchone():
            raise JobError("JOB already exists; import never overwrites existing work")
        parent = job.get("parent_id")
        if parent and not db.execute("SELECT 1 FROM jobs WHERE id=?", (parent,)).fetchone():
            # Preserve the branch identity while making the missing parent explicit.
            parent = None
        db.execute("""INSERT INTO jobs
            (id,title,purpose,origin,parent_id,stage,state,path_json,constraints_json,created_at,updated_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (job["id"], job["title"], job["purpose"], job["origin"], parent,
             job["stage"], job["state"], _canonical(job.get("path", [])).decode(),
             _canonical(job.get("constraints", [])).decode(),
             job["created_at"], job["updated_at"]))
        for event in events:
            db.execute("""INSERT INTO job_events
                (job_id,event_type,payload_json,created_at) VALUES(?,?,?,?)""",
                (job["id"], event["event_type"], _canonical(event.get("payload", {})).decode(),
                 event["created_at"]))
        for metric in metrics:
            db.execute("""INSERT INTO job_metrics
                (job_id,name,value,unit,method,window,source,limitations,created_at)
                VALUES(?,?,?,?,?,?,?,?,?)""",
                (job["id"], metric["name"], metric["value"], metric["unit"],
                 metric["method"], metric["window"], metric["source"],
                 metric["limitations"], metric.get("created_at", job["updated_at"])))
        for artifact in artifacts:
            content = artifact["content"]
            digest = hashlib.sha256(_canonical(content)).hexdigest()
            if digest != artifact["sha256"]:
                raise JobError("snapshot artifact digest mismatch")
            db.execute("""INSERT INTO job_artifacts
                (id,job_id,kind,title,content_json,sha256,created_at)
                VALUES(?,?,?,?,?,?,?)""",
                (artifact["id"], job["id"], artifact["kind"], artifact["title"],
                 _canonical(content).decode(), digest, artifact["created_at"]))
    return store.get_job(job["id"])


ANDROID_TRANSFER_SCHEMA = "codexgen.android.jobs.v1"


def _android_millis(value: Any) -> int:
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return int(parsed.timestamp() * 1000)
        except ValueError:
            return 0
    return 0


def export_android_job_transfer(store: JobStore) -> str:
    """Export JOB/event records in the schema used by the native Android dashboard."""
    with store._connect() as db:
        jobs = [dict(row) for row in db.execute(
            "SELECT id,title,purpose,state,stage,parent_id,created_at,updated_at FROM jobs ORDER BY created_at,id"
        ).fetchall()]
        for job in jobs:
            job["created_at"] = _android_millis(job["created_at"])
            job["updated_at"] = _android_millis(job["updated_at"])
        events = []
        for row in db.execute(
            "SELECT job_id,event_type,payload_json,created_at FROM job_events ORDER BY sequence"
        ).fetchall():
            events.append({"job_id": row["job_id"], "event_type": row["event_type"],
                           "detail": row["payload_json"], "created_at": _android_millis(row["created_at"])})
    return json.dumps({"schema": ANDROID_TRANSFER_SCHEMA, "jobs": jobs, "events": events},
                      ensure_ascii=False, sort_keys=True, indent=2)


def import_android_job_transfer(store: JobStore, raw: str | dict[str, Any]) -> int:
    """Import Android dashboard records without overwriting existing JOB identities."""
    try:
        payload = json.loads(raw) if isinstance(raw, str) else raw
    except (TypeError, json.JSONDecodeError) as exc:
        raise JobError("invalid Android JOB transfer JSON") from exc
    if not isinstance(payload, dict) or payload.get("schema") != ANDROID_TRANSFER_SCHEMA:
        raise JobError("unsupported Android JOB transfer schema")
    jobs, events = payload.get("jobs"), payload.get("events", [])
    if not isinstance(jobs, list) or not isinstance(events, list):
        raise JobError("Android JOB transfer collections must be arrays")
    if len(jobs) > 100000 or len(events) > 500000:
        raise JobError("Android JOB transfer exceeds recovery limits")
    _ensure_artifacts(store)
    with store._connect() as db:
        ids = set()
        for job in jobs:
            if not isinstance(job, dict) or not isinstance(job.get("id"), str):
                raise JobError("Android transfer contains an invalid JOB")
            if job["id"] in ids or db.execute("SELECT 1 FROM jobs WHERE id=?", (job["id"],)).fetchone():
                raise JobError("duplicate JOB identity; import never overwrites existing work")
            ids.add(job["id"])
            if job.get("state") not in {"open", "active", "paused", "blocked", "adapted", "completed", "archived"}:
                raise JobError("Android transfer contains an invalid state")
            if job.get("stage") not in {"notice", "orient", "choose", "make", "examine", "adapt", "carry_forward"}:
                raise JobError("Android transfer contains an invalid stage")
        # Insert all records without parent links first, then restore valid relationships.
        for job in jobs:
            db.execute("""INSERT INTO jobs
                (id,title,purpose,origin,parent_id,stage,state,path_json,constraints_json,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                (job["id"], job["title"], job["purpose"], "android-dashboard", None,
                 job["stage"], job["state"], "[]", "[]",
                 str(job.get("created_at", "")), str(job.get("updated_at", ""))))
        for job in jobs:
            parent = job.get("parent_id")
            if parent in ids:
                db.execute("UPDATE jobs SET parent_id=? WHERE id=?", (parent, job["id"]))
        for event in events:
            if not isinstance(event, dict) or event.get("job_id") not in ids:
                continue
            db.execute("""INSERT INTO job_events
                (job_id,event_type,payload_json,created_at) VALUES(?,?,?,?)""",
                (event["job_id"], str(event.get("event_type", "imported")),
                 _canonical({"detail": event.get("detail", "")}).decode(),
                 str(event.get("created_at", ""))))
    return len(jobs)
