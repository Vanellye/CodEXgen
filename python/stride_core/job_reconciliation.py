"""Append-only corrections and derived JOB reconciliation views.

This ledger is independent of JobStore. It stores references to original JOB
events and never edits or deletes them. A correction is only a proposal until
a separately appended review accepts or declines it.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any


class ReconciliationError(ValueError):
    """Invalid correction, review, or reconciliation request."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _required(name: str, value: Any, limit: int = 4000) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ReconciliationError(f"{name} must be non-empty text up to {limit} characters")
    return value.strip()


def _json(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ReconciliationError("value must be finite JSON-serializable data") from exc


@dataclass(frozen=True)
class CorrectionRecord:
    correction_id: str
    job_id: str
    source_ref: str
    field: str
    proposed_value: Any
    evidence: str
    rationale: str
    author: str
    recorded_at: str


@dataclass(frozen=True)
class CorrectionReview:
    review_id: str
    correction_id: str
    decision: str
    evidence: str
    rationale: str
    reviewer: str
    recorded_at: str


@dataclass(frozen=True)
class ReconciliationView:
    job_id: str
    source_event: dict[str, Any]
    corrections: tuple[CorrectionRecord, ...]
    reviews: tuple[CorrectionReview, ...]
    derived_payload: dict[str, Any]
    interpretation_status: dict[str, str]
    source_preserved: bool
    note: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CorrectionLedger:
    """Separate SQLite append-only ledger; no update/delete interface is exposed."""

    def __init__(self, database: str | Path = ":memory:") -> None:
        self.database = str(database)
        if self.database != ":memory:":
            Path(self.database).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS corrections (
                    correction_id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    source_ref TEXT NOT NULL,
                    field TEXT NOT NULL,
                    proposed_value_json TEXT NOT NULL,
                    evidence TEXT NOT NULL,
                    rationale TEXT NOT NULL,
                    author TEXT NOT NULL,
                    recorded_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS corrections_source_idx
                    ON corrections(job_id, source_ref, recorded_at);
                CREATE TABLE IF NOT EXISTS correction_reviews (
                    review_id TEXT PRIMARY KEY,
                    correction_id TEXT NOT NULL REFERENCES corrections(correction_id),
                    decision TEXT NOT NULL CHECK(decision IN ('accepted','declined')),
                    evidence TEXT NOT NULL,
                    rationale TEXT NOT NULL,
                    reviewer TEXT NOT NULL,
                    recorded_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS reviews_correction_idx
                    ON correction_reviews(correction_id, recorded_at);
            """)

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.database, timeout=10.0)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        return db

    def append_correction(
        self, *, job_id: str, source_ref: str, field: str,
        proposed_value: Any, evidence: str, rationale: str, author: str,
        authorized: bool = False,
    ) -> CorrectionRecord:
        if authorized is not True:
            raise PermissionError("Appending a correction requires explicit authorization")
        job_id = _required("job_id", job_id, 128)
        source_ref = _required("source_ref", source_ref, 300)
        field = _required("field", field, 120)
        evidence = _required("evidence", evidence)
        rationale = _required("rationale", rationale)
        author = _required("author", author, 200)
        value_json = _json(proposed_value)
        record = CorrectionRecord(
            str(uuid.uuid4()), job_id, source_ref, field,
            json.loads(value_json), evidence, rationale, author, _now()
        )
        with self._connect() as db:
            db.execute("""INSERT INTO corrections VALUES(?,?,?,?,?,?,?,?,?)""", (
                record.correction_id, record.job_id, record.source_ref,
                record.field, value_json, record.evidence, record.rationale,
                record.author, record.recorded_at
            ))
        return record

    def append_review(
        self, correction_id: str, *, decision: str, evidence: str,
        rationale: str, reviewer: str, authorized: bool = False,
    ) -> CorrectionReview:
        if authorized is not True:
            raise PermissionError("Reviewing a correction requires explicit authorization")
        if decision not in {"accepted", "declined"}:
            raise ReconciliationError("decision must be accepted or declined")
        evidence = _required("evidence", evidence)
        rationale = _required("rationale", rationale)
        reviewer = _required("reviewer", reviewer, 200)
        with self._connect() as db:
            if not db.execute(
                "SELECT 1 FROM corrections WHERE correction_id=?", (correction_id,)
            ).fetchone():
                raise ReconciliationError("correction not found")
            latest = db.execute("""SELECT decision FROM correction_reviews
                WHERE correction_id=? ORDER BY recorded_at DESC, rowid DESC LIMIT 1""",
                (correction_id,)).fetchone()
            if latest and latest["decision"] == decision:
                raise ReconciliationError("duplicate consecutive review decision")
            review = CorrectionReview(
                str(uuid.uuid4()), correction_id, decision, evidence,
                rationale, reviewer, _now()
            )
            db.execute("INSERT INTO correction_reviews VALUES(?,?,?,?,?,?,?)", (
                review.review_id, review.correction_id, review.decision,
                review.evidence, review.rationale, review.reviewer, review.recorded_at
            ))
        return review

    def reconcile(self, store: Any, job_id: str, source_ref: str) -> ReconciliationView:
        """Build an overlay view; the supplied JOB store is read only."""
        job_id = _required("job_id", job_id, 128)
        source_ref = _required("source_ref", source_ref, 300)
        if not callable(getattr(store, "get_job", None)) or not callable(
            getattr(store, "events", None)
        ):
            raise TypeError("store must expose get_job and events")
        store.get_job(job_id)
        match = None
        for row in store.events(job_id):
            if f"job:{job_id}:event:{row['sequence']}" == source_ref:
                match = row
                break
        if match is None:
            raise ReconciliationError("referenced original JOB event not found")

        with self._connect() as db:
            rows = db.execute("""SELECT * FROM corrections
                WHERE job_id=? AND source_ref=? ORDER BY recorded_at,rowid""",
                (job_id, source_ref)).fetchall()
            corrections = [CorrectionRecord(
                row["correction_id"], row["job_id"], row["source_ref"],
                row["field"], json.loads(row["proposed_value_json"]),
                row["evidence"], row["rationale"], row["author"], row["recorded_at"]
            ) for row in rows]
            review_rows = db.execute("""SELECT r.* FROM correction_reviews r
                JOIN corrections c ON c.correction_id=r.correction_id
                WHERE c.job_id=? AND c.source_ref=? ORDER BY r.recorded_at,r.rowid""",
                (job_id, source_ref)).fetchall()
            reviews = [CorrectionReview(**dict(row)) for row in review_rows]

        latest_review: dict[str, CorrectionReview] = {}
        for review in reviews:
            latest_review[review.correction_id] = review

        original = dict(match["payload"])
        derived = dict(original)
        status: dict[str, str] = {}
        # Only the latest accepted correction per field is applied to the
        # derived overlay. Declined/pending proposals remain visible.
        accepted_by_field: dict[str, CorrectionRecord] = {}
        for correction in corrections:
            review = latest_review.get(correction.correction_id)
            state = review.decision if review else "proposed"
            status[correction.correction_id] = state
            if state == "accepted":
                accepted_by_field[correction.field] = correction
        for field, correction in accepted_by_field.items():
            derived[field] = correction.proposed_value

        return ReconciliationView(
            job_id=job_id,
            source_event={
                "source_ref": source_ref,
                "sequence": match["sequence"],
                "event_type": match["event_type"],
                "recorded_at": match["created_at"],
                "payload": original,
            },
            corrections=tuple(corrections),
            reviews=tuple(reviews),
            derived_payload=derived,
            interpretation_status=status,
            source_preserved=True,
            note=(
                "Original JOB event is unchanged. Derived payload is a view only; "
                "proposals do not apply until reviewed as accepted. The latest "
                "accepted correction per field supplies the displayed overlay."
            ),
        )
