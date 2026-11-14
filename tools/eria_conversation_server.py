#!/usr/bin/env python3
"""Local-only ERIA HTML conversation server for Termux.

Serves the bundled UI, delegates questions to the existing read-only
Repository Conversation Engine, and stores chat/index metadata in SQLite
outside the Git checkout (~/.eria/data/). No arbitrary SQL, shell, or
filesystem-write endpoint is exposed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
import sqlite3
import sys
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parent
TOOLS = HERE
UI_FILE = HERE / "eria_conversation.html"
sys.path.insert(0, str(TOOLS))
from eria_repository_conversation import Conversation, Repository  # noqa: E402
from eria_pantheon.pons import Pons  # noqa: E402

DB_DEFAULT = Path.home() / ".eria" / "data" / "eria_conversation.sqlite3"
MAX_BODY = 16_384
SAFE_NAME = re.compile(r"(secret|credential|token|password|private[_-]?key|\.env)", re.I)
SKIP_PARTS = {".git", ".gradle", ".idea", "node_modules", "__pycache__", ".venv", "venv", "build", "dist"}
DB_LOCK = threading.RLock()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self, path: Path):
        self.path = path.expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user','assistant')),
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_messages_session
                    ON messages(session_id, id);
                CREATE TABLE IF NOT EXISTS repository_files (
                    path TEXT PRIMARY KEY,
                    extension TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    modified_at REAL NOT NULL,
                    indexed_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event TEXT NOT NULL,
                    status TEXT NOT NULL,
                    detail_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS pons_requests (
                    request_id TEXT PRIMARY KEY,
                    capability TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('HOLD','PROPOSAL_ONLY','REVIEW_READY')),
                    created_at TEXT NOT NULL
                );
                CREATE TRIGGER IF NOT EXISTS audit_events_no_update
                BEFORE UPDATE ON audit_events BEGIN
                    SELECT RAISE(ABORT, 'audit_events is append-only');
                END;
                CREATE TRIGGER IF NOT EXISTS audit_events_no_delete
                BEFORE DELETE ON audit_events BEGIN
                    SELECT RAISE(ABORT, 'audit_events is append-only');
                END;
            """)
        with self.connect() as db:
            columns = {row[1] for row in db.execute("PRAGMA table_info(repository_files)")}
            if "source_sha256" not in columns:
                db.execute("ALTER TABLE repository_files ADD COLUMN source_sha256 TEXT NOT NULL DEFAULT ''")

    def connect(self):
        db = sqlite3.connect(str(self.path), timeout=10)
        db.row_factory = sqlite3.Row
        return db

    def add_message(self, session_id: str, role: str, content: str):
        with DB_LOCK, self.connect() as db:
            db.execute(
                "INSERT INTO messages(session_id,role,content,created_at) VALUES(?,?,?,?)",
                (session_id, role, content, utc_now()),
            )

    def history(self, session_id: str, limit: int = 100):
        with DB_LOCK, self.connect() as db:
            rows = db.execute(
                "SELECT id,role,content,created_at FROM messages "
                "WHERE session_id=? ORDER BY id DESC LIMIT ?",
                (session_id, limit),
            ).fetchall()
        return [dict(row) for row in reversed(rows)]

    def index_repository(self, repository: Repository):
        records = []
        for rel in repository.files():
            path = Path(rel)
            if SAFE_NAME.search(path.name) or any(part in SKIP_PARTS for part in path.parts):
                continue
            full = repository.root / path
            try:
                if not full.is_file():
                    continue
                stat = full.stat()
                digest = ""
                if stat.st_size <= 5 * 1024 * 1024:
                    hasher = hashlib.sha256()
                    with full.open("rb") as source:
                        for chunk in iter(lambda: source.read(65536), b""):
                            hasher.update(chunk)
                    digest = hasher.hexdigest()
                records.append((
                    rel, path.suffix.lower(), stat.st_size, stat.st_mtime,
                    utc_now(), digest
                ))
            except OSError:
                continue
        with DB_LOCK, self.connect() as db:
            db.execute("DELETE FROM repository_files")
            db.executemany(
                "INSERT OR REPLACE INTO repository_files"
                "(path,extension,size_bytes,modified_at,indexed_at,source_sha256) VALUES(?,?,?,?,?,?)",
                records,
            )
            db.execute(
                "INSERT OR REPLACE INTO metadata(key,value) VALUES('indexed_at',?)",
                (utc_now(),),
            )
            db.execute(
                "INSERT OR REPLACE INTO metadata(key,value) VALUES('repository_root',?)",
                (str(repository.root),),
            )
        self.add_audit("repository_indexed", "REVIEW_READY", {
            "files_indexed": len(records), "repository_root": str(repository.root),
            "source_hashes": "SHA-256 for eligible files up to 5 MiB",
        })
        return len(records)

    def add_audit(self, event: str, status: str, detail: dict):
        with DB_LOCK, self.connect() as db:
            db.execute(
                "INSERT INTO audit_events(event,status,detail_json,created_at) VALUES(?,?,?,?)",
                (event, status, json.dumps(detail, ensure_ascii=False, sort_keys=True), utc_now()),
            )

    def audit_history(self, limit: int = 100):
        with DB_LOCK, self.connect() as db:
            rows = db.execute(
                "SELECT id,event,status,detail_json,created_at FROM audit_events "
                "ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            try:
                item["detail"] = json.loads(item.pop("detail_json"))
            except (TypeError, json.JSONDecodeError):
                item["detail"] = {}
            result.append(item)
        return result

    def provenance(self, query: str = "", limit: int = 100):
        with DB_LOCK, self.connect() as db:
            rows = db.execute(
                "SELECT path,extension,size_bytes,modified_at,indexed_at,source_sha256 "
                "FROM repository_files WHERE instr(lower(path),lower(?))>0 "
                "ORDER BY path LIMIT ?", (query, limit)
            ).fetchall()
        return [dict(row) for row in rows]

    def create_pons_request(self, capability: str, scope: str, reason: str):
        request_id = str(uuid.uuid4())
        created = utc_now()
        with DB_LOCK, self.connect() as db:
            db.execute(
                "INSERT INTO pons_requests(request_id,capability,scope,reason,status,created_at) "
                "VALUES(?,?,?,?,?,?)",
                (request_id, capability, scope, reason, "HOLD", created),
            )
        self.add_audit("pons_authorization_requested", "HOLD", {
            "request_id": request_id, "capability": capability, "scope": scope,
        })
        return {"request_id": request_id, "capability": capability,
                "scope": scope, "reason": reason, "status": "HOLD",
                "created_at": created, "approval_created": False}

    def pons_requests(self, limit: int = 100):
        with DB_LOCK, self.connect() as db:
            rows = db.execute(
                "SELECT request_id,capability,scope,reason,status,created_at "
                "FROM pons_requests ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(row) for row in rows]

    def index_summary(self):
        with DB_LOCK, self.connect() as db:
            count = db.execute("SELECT COUNT(*) FROM repository_files").fetchone()[0]
            groups = db.execute(
                "SELECT extension,COUNT(*) AS count FROM repository_files "
                "GROUP BY extension ORDER BY count DESC LIMIT 20"
            ).fetchall()
            meta = dict(db.execute("SELECT key,value FROM metadata").fetchall())
        return {"files": count, "types": [dict(r) for r in groups],
                "indexed_at": meta.get("indexed_at")}

    def search_files(self, query: str, limit: int = 40):
        # instr() avoids wildcard interpretation and keeps the query parameterized.
        with DB_LOCK, self.connect() as db:
            rows = db.execute(
                "SELECT path,extension,size_bytes FROM repository_files "
                "WHERE instr(lower(path), lower(?)) > 0 ORDER BY path LIMIT ?",
                (query, limit),
            ).fetchall()
        return [dict(row) for row in rows]


class Handler(BaseHTTPRequestHandler):
    server_version = "ERIA-Local/1.0"

    def log_message(self, fmt, *args):
        # Avoid logging conversation text or user-supplied query strings.
        sys.stderr.write("ERIA HTTP: " + (fmt % args).split("?")[0] + "\n")

    @property
    def app(self):
        return self.server.app

    def send_json(self, status: int, value):
        raw = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(raw)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length < 1 or length > MAX_BODY:
            raise ValueError("Request body missing or too large.")
        data = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Expected a JSON object.")
        return data

    def do_GET(self):
        route = urlparse(self.path).path
        if route == "/":
            try:
                raw = UI_FILE.read_bytes()
            except OSError:
                self.send_error(404, "UI file not found")
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(raw)
            return
        if route == "/repository":
            try:
                raw = (HERE / "eria_repository.html").read_bytes()
            except OSError:
                self.send_error(404, "Repository UI file not found")
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(raw)
            return
        if route == "/api/pons/status":
            self.send_json(200, Pons.describe())
            return
        if route == "/api/pons/requests":
            self.send_json(200, {
                "requests": self.app.store.pons_requests(),
                "approval_supported": False,
                "note": "Requests are recorded as HOLD proposals; this service cannot approve grants.",
            })
            return
        if route == "/api/audit":
            self.send_json(200, {"events": self.app.store.audit_history()})
            return
        if route == "/api/provenance":
            params = parse_qs(urlparse(self.path).query)
            term = params.get("q", [""])[0][:200]
            self.send_json(200, {
                "records": self.app.store.provenance(term),
                "source_authority": "NON_AUTHORITATIVE",
                "derived_records": "not generated by this dashboard service",
                "hash_note": "SHA-256 is populated for eligible files up to 5 MiB; empty means not computed.",
            })
            return
        if route == "/api/files/detail":
            params = parse_qs(urlparse(self.path).query)
            rel = params.get("path", [""])[0][:500]
            if not rel or SAFE_NAME.search(Path(rel).name):
                self.send_json(400, {"error": "A non-sensitive repository-relative path is required."})
                return
            try:
                content = self.app.repository.show(rel)
                record = next((x for x in self.app.store.provenance(rel) if x["path"] == rel), None)
                self.send_json(200, {
                    "path": rel, "content_preview": content[:12000],
                    "truncated": len(content) > 12000, "provenance": record,
                    "source_authority": "NON_AUTHORITATIVE",
                })
            except Exception as exc:
                self.send_json(400, {"error": "File inspection unavailable: " + type(exc).__name__})
            return
        if route == "/api/status":
            self.send_json(200, {
                "ok": True, "repository": str(self.app.repository.root),
                "database": str(self.app.store.path),
                "index": self.app.store.index_summary(),
                "engine": "ERIA Repository Conversation Engine",
                "mode": "read-only repository inspection",
            })
            return
        if route == "/api/history":
            session = self.headers.get("X-ERIA-Session", "default")[:80]
            self.send_json(200, {"messages": self.app.store.history(session)})
            return
        if route == "/api/files":
            query = urlparse(self.path).query
            from urllib.parse import parse_qs
            term = parse_qs(query).get("q", [""])[0][:200]
            self.send_json(200, {"files": self.app.store.search_files(term)})
            return
        self.send_error(404)

    def do_POST(self):
        route = urlparse(self.path).path
        try:
            data = self.read_json()
            if route == "/api/chat":
                question = data.get("message")
                session = str(data.get("session_id", "default"))[:80]
                if not isinstance(question, str) or not question.strip():
                    raise ValueError("message must be non-empty text.")
                question = question.strip()[:8000]
                self.app.store.add_message(session, "user", question)
                answer = self.app.conversation.ask(question)
                self.app.store.add_message(session, "assistant", answer)
                self.send_json(200, {"answer": answer})
                return
            if route == "/api/index":
                count = self.app.store.index_repository(self.app.repository)
                self.send_json(200, {"indexed": count,
                                     "summary": self.app.store.index_summary()})
                return
            if route == "/api/pons/requests":
                capability = data.get("capability")
                scope = data.get("scope")
                reason = data.get("reason")
                if not all(isinstance(x, str) and x.strip() for x in (capability, scope, reason)):
                    raise ValueError("capability, scope, and reason are required text fields.")
                if len(capability) > 100 or len(scope) > 500 or len(reason) > 2000:
                    raise ValueError("Authorization request field exceeds its length limit.")
                request_record = self.app.store.create_pons_request(
                    capability.strip(), scope.strip(), reason.strip()
                )
                self.send_json(201, request_record)
                return
            self.send_error(404)
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            self.send_json(400, {"error": str(exc)})
        except Exception as exc:
            # Do not expose tracebacks, environment values, or filesystem internals.
            self.send_json(500, {"error": "Internal ERIA error: " + type(exc).__name__})


class App:
    def __init__(self, root: Path, database: Path):
        self.repository = Repository(root)
        self.conversation = Conversation(self.repository)
        self.store = Store(database)
        self.store.index_repository(self.repository)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--host", default="127.0.0.1",
                        help="Loopback only; remote binding is intentionally disabled.")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--database", type=Path, default=DB_DEFAULT)
    args = parser.parse_args()
    if args.host not in {"127.0.0.1", "localhost", "::1"}:
        parser.error("ERIA server only binds to loopback.")
    app = App(Path(args.repository), args.database)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.app = app
    print("ERIA HTML Conversation")
    print("Repository:", app.repository.root)
    print("SQLite:", app.store.path)
    print(f"Open http://127.0.0.1:{args.port} in your browser")
    print("Press Ctrl+C to stop. No Git writes or remote transmission are enabled.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nERIA server stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
