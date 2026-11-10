"""CodEXgen cognitive layer: append-only, provenance-aware temporal memory.

This first implementation records claims and their lineage without deciding
which conflicting claim is true. Reconciliation surfaces overlaps for review;
it never rewrites or deletes historical entries.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


class LedgerError(ValueError):
    """Raised when an entry would violate ledger integrity."""


@dataclass(frozen=True)
class MemoryEntry:
    entry_id: str
    subject: str
    statement: str
    source_ref: str
    recorded_at: str
    effective_from: str | None = None
    effective_until: str | None = None
    derived_from: tuple[str, ...] = ()

    def to_envelope(self) -> dict[str, object]:
        """Expose this immutable claim as a TRUE NORTH data record.

        UNKNOWN quality means the ledger preserves the claim without
        adjudicating its truth. The envelope grants no operational authority.
        """
        return {
            "record_id": self.entry_id,
            "schema_version": 1,
            "source": "cognitive_layer",
            "observed_at": self.recorded_at,
            "payload": {
                "subject": self.subject,
                "statement": self.statement,
                "effective_from": self.effective_from,
                "effective_until": self.effective_until,
                "derived_from": list(self.derived_from),
            },
            "units": {},
            "quality": "UNKNOWN",
            "provenance": {
                "source_ref": self.source_ref,
                "signature_status": "not_present",
            },
            "transformations": [],
            "authorization": {
                "status": "not_authorized",
                "scope": [],
                "approval_ref": None,
            },
            "validation": {
                "status": "unreviewed",
                "reconciliation": "pending",
            },
            "retention": {
                "policy": "append_only",
                "historical_record_mutation": "prohibited",
            },
        }


@dataclass(frozen=True)
class ReconciliationReport:
    subject: str
    entries: tuple[MemoryEntry, ...]
    conflicting_pairs: tuple[tuple[str, str], ...]

    @property
    def status(self) -> str:
        return "REVIEW_REQUIRED" if self.conflicting_pairs else "NO_OVERLAP_CONFLICTS"


def _parse_timestamp(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise LedgerError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise LedgerError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _normalize_statement(value: str) -> str:
    return " ".join(value.casefold().split())


def _periods_may_overlap(left: MemoryEntry, right: MemoryEntry) -> bool:
    # Unknown bounds are treated conservatively: uncertainty must not hide a
    # possible conflict. Explicit non-overlapping intervals remain distinct.
    left_start = _parse_timestamp(left.effective_from, "effective_from") if left.effective_from else None
    left_end = _parse_timestamp(left.effective_until, "effective_until") if left.effective_until else None
    right_start = _parse_timestamp(right.effective_from, "effective_from") if right.effective_from else None
    right_end = _parse_timestamp(right.effective_until, "effective_until") if right.effective_until else None

    if left_end is not None and right_start is not None and left_end < right_start:
        return False
    if right_end is not None and left_start is not None and right_end < left_start:
        return False
    return True


class TemporalCognitiveLayer:
    """Append-only evidence ledger with explicit lineage and review-first conflict detection."""

    def __init__(self, database_path: str | Path = "codexgen_cognitive_memory.sqlite3"):
        self.database_path = str(database_path)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS memory_entries (
                    entry_id TEXT PRIMARY KEY,
                    subject TEXT NOT NULL,
                    statement TEXT NOT NULL,
                    source_ref TEXT NOT NULL,
                    recorded_at TEXT NOT NULL,
                    effective_from TEXT,
                    effective_until TEXT
                );
                CREATE TABLE IF NOT EXISTS memory_lineage (
                    entry_id TEXT NOT NULL REFERENCES memory_entries(entry_id),
                    parent_id TEXT NOT NULL REFERENCES memory_entries(entry_id),
                    PRIMARY KEY (entry_id, parent_id),
                    CHECK (entry_id <> parent_id)
                );
                CREATE TRIGGER IF NOT EXISTS memory_entries_no_update
                BEFORE UPDATE ON memory_entries
                BEGIN
                    SELECT RAISE(ABORT, 'memory entries are immutable');
                END;
                CREATE TRIGGER IF NOT EXISTS memory_entries_no_delete
                BEFORE DELETE ON memory_entries
                BEGIN
                    SELECT RAISE(ABORT, 'memory entries are immutable');
                END;
                CREATE TRIGGER IF NOT EXISTS memory_lineage_no_update
                BEFORE UPDATE ON memory_lineage
                BEGIN
                    SELECT RAISE(ABORT, 'memory lineage is immutable');
                END;
                CREATE TRIGGER IF NOT EXISTS memory_lineage_no_delete
                BEFORE DELETE ON memory_lineage
                BEGIN
                    SELECT RAISE(ABORT, 'memory lineage is immutable');
                END;
                """
            )

    def append(self, entry: MemoryEntry) -> None:
        """Append one evidence record; never update an existing record."""
        required = {
            "entry_id": entry.entry_id,
            "subject": entry.subject,
            "statement": entry.statement,
            "source_ref": entry.source_ref,
            "recorded_at": entry.recorded_at,
        }
        for field, value in required.items():
            if not isinstance(value, str) or not value.strip():
                raise LedgerError(f"{field} must be a non-empty string")

        _parse_timestamp(entry.recorded_at, "recorded_at")
        start = _parse_timestamp(entry.effective_from, "effective_from") if entry.effective_from else None
        end = _parse_timestamp(entry.effective_until, "effective_until") if entry.effective_until else None
        if start is not None and end is not None and end < start:
            raise LedgerError("effective_until cannot precede effective_from")
        if len(set(entry.derived_from)) != len(entry.derived_from):
            raise LedgerError("derived_from cannot contain duplicate identifiers")
        if entry.entry_id in entry.derived_from:
            raise LedgerError("an entry cannot derive from itself")

        with self._connect() as connection:
            for parent_id in entry.derived_from:
                parent = connection.execute(
                    "SELECT 1 FROM memory_entries WHERE entry_id = ?", (parent_id,)
                ).fetchone()
                if parent is None:
                    raise LedgerError(f"unknown lineage parent: {parent_id}")
            try:
                connection.execute(
                    """
                    INSERT INTO memory_entries
                        (entry_id, subject, statement, source_ref, recorded_at,
                         effective_from, effective_until)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        entry.entry_id, entry.subject.strip(), entry.statement.strip(),
                        entry.source_ref.strip(), entry.recorded_at,
                        entry.effective_from, entry.effective_until,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                raise LedgerError(f"entry cannot be appended: {exc}") from exc
            connection.executemany(
                "INSERT INTO memory_lineage (entry_id, parent_id) VALUES (?, ?)",
                [(entry.entry_id, parent_id) for parent_id in entry.derived_from],
            )

    def entries(self, subject: str | None = None) -> tuple[MemoryEntry, ...]:
        query = (
            "SELECT entry_id, subject, statement, source_ref, recorded_at, "
            "effective_from, effective_until FROM memory_entries"
        )
        params: tuple[str, ...] = ()
        if subject is not None:
            query += " WHERE subject = ?"
            params = (subject,)
        query += " ORDER BY recorded_at, entry_id"
        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
            result = []
            for row in rows:
                parents = connection.execute(
                    "SELECT parent_id FROM memory_lineage WHERE entry_id = ? ORDER BY parent_id",
                    (row[0],),
                ).fetchall()
                result.append(MemoryEntry(*row, derived_from=tuple(parent[0] for parent in parents)))
        return tuple(result)

    def reconcile(self, subject: str) -> ReconciliationReport:
        """Surface potentially conflicting claims; do not select a winner."""
        records = self.entries(subject)
        conflicts: list[tuple[str, str]] = []
        for index, left in enumerate(records):
            for right in records[index + 1:]:
                if _normalize_statement(left.statement) == _normalize_statement(right.statement):
                    continue
                if _periods_may_overlap(left, right):
                    conflicts.append((left.entry_id, right.entry_id))
        return ReconciliationReport(
            subject=subject,
            entries=records,
            conflicting_pairs=tuple(conflicts),
        )

    def lineage(self, entry_id: str) -> tuple[str, ...]:
        """Return direct parent identifiers for a record."""
        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM memory_entries WHERE entry_id = ?", (entry_id,)
            ).fetchone()
            if row is None:
                raise LedgerError(f"unknown entry: {entry_id}")
            parents = connection.execute(
                "SELECT parent_id FROM memory_lineage WHERE entry_id = ? ORDER BY parent_id",
                (entry_id,),
            ).fetchall()
        return tuple(parent[0] for parent in parents)
