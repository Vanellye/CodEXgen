"""Local, permission-checked push/pull router for CodEXgen.

This is an in-process SQLite transport. It does not open sockets or route
between realms. Channel membership and permissions are explicit; consequential
events require recipient acceptance before they can be acknowledged as accepted.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class RouterError(ValueError):
    """Base class for rejected router operations."""


class PermissionDenied(RouterError):
    pass


class ConsentRequired(RouterError):
    pass


@dataclass(frozen=True)
class ChannelEvent:
    event_id: str
    channel_id: str
    sender: str
    event_type: str
    payload: dict[str, Any]
    created_at: str
    requires_acceptance: bool
    idempotency_key: str


class LocalChannelRouter:
    """Durable local channel router with append-only event and decision history."""

    def __init__(self, database_path: str | Path = "codexgen_channels.sqlite3"):
        self.database_path = str(database_path)
        self._initialize()

    def _connect(self):
        db = sqlite3.connect(self.database_path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA journal_mode=WAL")
        return db

    def _initialize(self):
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS channels(
                    channel_id TEXT PRIMARY KEY, owner TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS memberships(
                    channel_id TEXT NOT NULL REFERENCES channels(channel_id),
                    endpoint TEXT NOT NULL,
                    can_publish INTEGER NOT NULL CHECK(can_publish IN (0,1)),
                    can_read INTEGER NOT NULL CHECK(can_read IN (0,1)),
                    active INTEGER NOT NULL CHECK(active IN (0,1)),
                    PRIMARY KEY(channel_id, endpoint)
                );
                CREATE TABLE IF NOT EXISTS events(
                    event_id TEXT PRIMARY KEY,
                    channel_id TEXT NOT NULL REFERENCES channels(channel_id),
                    sender TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    requires_acceptance INTEGER NOT NULL,
                    idempotency_key TEXT NOT NULL,
                    UNIQUE(channel_id, sender, idempotency_key)
                );
                CREATE TABLE IF NOT EXISTS deliveries(
                    event_id TEXT NOT NULL REFERENCES events(event_id),
                    recipient TEXT NOT NULL,
                    state TEXT NOT NULL CHECK(state IN
                      ('pending','delivered','accepted','declined','revoked')),
                    PRIMARY KEY(event_id, recipient)
                );
                CREATE TABLE IF NOT EXISTS decisions(
                    decision_id TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL REFERENCES events(event_id),
                    recipient TEXT NOT NULL,
                    decision TEXT NOT NULL CHECK(decision IN ('accept','decline')),
                    decided_at TEXT NOT NULL
                );
                CREATE TRIGGER IF NOT EXISTS events_no_update
                BEFORE UPDATE ON events BEGIN
                    SELECT RAISE(ABORT, 'events are append-only');
                END;
                CREATE TRIGGER IF NOT EXISTS events_no_delete
                BEFORE DELETE ON events BEGIN
                    SELECT RAISE(ABORT, 'events are append-only');
                END;
                CREATE TRIGGER IF NOT EXISTS decisions_no_update
                BEFORE UPDATE ON decisions BEGIN
                    SELECT RAISE(ABORT, 'decisions are append-only');
                END;
                CREATE TRIGGER IF NOT EXISTS decisions_no_delete
                BEFORE DELETE ON decisions BEGIN
                    SELECT RAISE(ABORT, 'decisions are append-only');
                END;
            """)

    @staticmethod
    def _now():
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()

    def create_channel(self, channel_id: str, owner: str):
        if not channel_id.strip() or not owner.strip():
            raise RouterError("channel_id and owner are required")
        with self._connect() as db:
            db.execute("INSERT INTO channels VALUES (?,?)", (channel_id, owner))
            db.execute(
                "INSERT INTO memberships VALUES (?,?,1,1,1)",
                (channel_id, owner),
            )

    def grant(self, channel_id: str, owner: str, endpoint: str,
              *, can_publish: bool = False, can_read: bool = True):
        with self._connect() as db:
            channel = db.execute(
                "SELECT owner FROM channels WHERE channel_id=?", (channel_id,)
            ).fetchone()
            if channel is None:
                raise RouterError("unknown channel")
            if channel["owner"] != owner:
                raise PermissionDenied("only the channel owner may grant access")
            db.execute(
                """INSERT INTO memberships VALUES (?,?,?,?,1)
                   ON CONFLICT(channel_id,endpoint) DO UPDATE SET
                     can_publish=excluded.can_publish,
                     can_read=excluded.can_read, active=1""",
                (channel_id, endpoint, int(can_publish), int(can_read)),
            )

    def revoke(self, channel_id: str, owner: str, endpoint: str):
        with self._connect() as db:
            channel = db.execute(
                "SELECT owner FROM channels WHERE channel_id=?", (channel_id,)
            ).fetchone()
            if channel is None:
                raise RouterError("unknown channel")
            if channel["owner"] != owner:
                raise PermissionDenied("only the channel owner may revoke access")
            db.execute(
                "UPDATE memberships SET active=0 WHERE channel_id=? AND endpoint=?",
                (channel_id, endpoint),
            )
            db.execute(
                """UPDATE deliveries SET state='revoked'
                   WHERE recipient=? AND event_id IN
                   (SELECT event_id FROM events WHERE channel_id=?)
                   AND state='pending'""",
                (endpoint, channel_id),
            )

    def push(self, channel_id: str, sender: str, event_type: str,
             payload: dict[str, Any], *, idempotency_key: str,
             recipients: list[str] | None = None,
             requires_acceptance: bool = False) -> str:
        if not event_type.strip() or not idempotency_key.strip():
            raise RouterError("event_type and idempotency_key are required")
        if not isinstance(payload, dict):
            raise RouterError("payload must be a JSON object")
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        with self._connect() as db:
            membership = db.execute(
                """SELECT can_publish,active FROM memberships
                   WHERE channel_id=? AND endpoint=?""",
                (channel_id, sender),
            ).fetchone()
            if membership is None or not membership["active"] or not membership["can_publish"]:
                raise PermissionDenied("sender cannot publish to this channel")
            existing = db.execute(
                """SELECT event_id,payload,event_type,requires_acceptance FROM events
                   WHERE channel_id=? AND sender=? AND idempotency_key=?""",
                (channel_id, sender, idempotency_key),
            ).fetchone()
            if existing:
                if (existing["payload"], existing["event_type"], bool(existing["requires_acceptance"])) != (encoded, event_type, requires_acceptance):
                    raise RouterError("idempotency key reused with different event content")
                return existing["event_id"]
            event_id = str(uuid.uuid4())
            db.execute(
                "INSERT INTO events VALUES (?,?,?,?,?,?,?,?,?)",
                (event_id, channel_id, sender, event_type, encoded,
                 self._now(), int(requires_acceptance), idempotency_key),
            )
            if recipients is None:
                rows = db.execute(
                    """SELECT endpoint FROM memberships WHERE channel_id=?
                       AND active=1 AND can_read=1 AND endpoint<>?""",
                    (channel_id, sender),
                ).fetchall()
                targets = [row["endpoint"] for row in rows]
            else:
                targets = list(dict.fromkeys(recipients))
            for recipient in targets:
                target = db.execute(
                    """SELECT active,can_read FROM memberships
                       WHERE channel_id=? AND endpoint=?""",
                    (channel_id, recipient),
                ).fetchone()
                if target is None or not target["active"] or not target["can_read"]:
                    raise PermissionDenied(f"recipient cannot read channel: {recipient}")
                db.execute(
                    "INSERT INTO deliveries VALUES (?,?, 'pending')",
                    (event_id, recipient),
                )
            return event_id

    def pull(self, channel_id: str, recipient: str, *, after: str | None = None,
             limit: int = 100) -> tuple[ChannelEvent, ...]:
        if limit < 1 or limit > 500:
            raise RouterError("limit must be between 1 and 500")
        with self._connect() as db:
            member = db.execute(
                """SELECT active,can_read FROM memberships
                   WHERE channel_id=? AND endpoint=?""",
                (channel_id, recipient),
            ).fetchone()
            if member is None or not member["active"] or not member["can_read"]:
                raise PermissionDenied("endpoint cannot pull from this channel")
            params: list[Any] = [channel_id, recipient]
            cursor_clause = ""
            if after is not None:
                cursor_clause = " AND e.created_at > (SELECT created_at FROM events WHERE event_id=?)"
                params.append(after)
            params.append(limit)
            rows = db.execute(
                """SELECT e.* FROM events e JOIN deliveries d ON d.event_id=e.event_id
                   WHERE e.channel_id=? AND d.recipient=? AND d.state IN ('pending','delivered')
                   """ + cursor_clause + " ORDER BY e.created_at,e.event_id LIMIT ?",
                params,
            ).fetchall()
            result = []
            for row in rows:
                db.execute(
                    """UPDATE deliveries SET state='delivered'
                       WHERE event_id=? AND recipient=? AND state='pending'""",
                    (row["event_id"], recipient),
                )
                result.append(ChannelEvent(
                    row["event_id"], row["channel_id"], row["sender"],
                    row["event_type"], json.loads(row["payload"]), row["created_at"],
                    bool(row["requires_acceptance"]), row["idempotency_key"],
                ))
            return tuple(result)

    def decide(self, event_id: str, recipient: str, *, accept: bool):
        decision = "accept" if accept else "decline"
        with self._connect() as db:
            delivery = db.execute(
                """SELECT d.state,e.requires_acceptance FROM deliveries d
                   JOIN events e ON e.event_id=d.event_id
                   WHERE d.event_id=? AND d.recipient=?""",
                (event_id, recipient),
            ).fetchone()
            if delivery is None:
                raise PermissionDenied("no delivery exists for this recipient")
            if delivery["state"] in ("revoked", "declined", "accepted"):
                raise RouterError(f"delivery already resolved: {delivery['state']}")
            if not delivery["requires_acceptance"] and accept:
                raise RouterError("this event does not request consequential-action consent")
            db.execute(
                "INSERT INTO decisions VALUES (?,?,?,?,?)",
                (str(uuid.uuid4()), event_id, recipient, decision, self._now()),
            )
            db.execute(
                "UPDATE deliveries SET state=? WHERE event_id=? AND recipient=?",
                ("accepted" if accept else "declined", event_id, recipient),
            )

    def delivery_state(self, event_id: str, recipient: str) -> str:
        with self._connect() as db:
            row = db.execute(
                "SELECT state FROM deliveries WHERE event_id=? AND recipient=?",
                (event_id, recipient),
            ).fetchone()
            if row is None:
                raise RouterError("unknown delivery")
            return row["state"]

    def history(self, channel_id: str) -> tuple[dict[str, Any], ...]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT event_id,sender,event_type,created_at,idempotency_key FROM events WHERE channel_id=? ORDER BY created_at,event_id",
                (channel_id,),
            ).fetchall()
            return tuple(dict(row) for row in rows)
