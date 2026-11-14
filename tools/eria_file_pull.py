#!/usr/bin/env python3
"""Read-only local + GitHub file ingestion for ERIA's SQLite database."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import subprocess
import threading
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MAX_FILE_BYTES = 2 * 1024 * 1024
SKIP_DIRS = {
    ".git", ".gradle", ".idea", ".venv", "venv", "__pycache__",
    "node_modules", "build", "dist", ".cache", ".pytest_cache",
}
SECRET_NAME = re.compile(
    r"(^\.env($|\.)|secret|credential|token|password|private[_-]?key|"
    r"\.keystore$|\.jks$|\.p12$|\.pem$|id_rsa|id_ed25519)", re.I
)
TEXT_EXTENSIONS = {
    ".kt", ".kts", ".java", ".cpp", ".cc", ".c", ".h", ".hpp",
    ".py", ".sh", ".bash", ".html", ".htm", ".css", ".js", ".mjs",
    ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml", ".toml", ".ini",
    ".properties", ".md", ".txt", ".xml", ".gradle", ".sql", ".csv",
    ".cmake", ".mk",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git_read(root: Path, *args: str) -> str:
    """Run a read-only Git query. No ref or working-tree mutation is possible here."""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True, capture_output=True, text=True, timeout=10,
        )
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def classify_path(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext in {".kt", ".kts", ".java", ".cpp", ".cc", ".c", ".h", ".hpp"}:
        return "source_code"
    if ext in {".py", ".sh", ".bash"}:
        return "scripts"
    if ext in {".html", ".htm", ".css", ".js", ".mjs", ".ts", ".tsx", ".jsx"}:
        return "web"
    if ext in {".json", ".yaml", ".yml", ".toml", ".ini", ".properties", ".xml"}:
        return "configuration"
    if ext in {".md", ".txt"}:
        return "documentation"
    if ext in {".sql", ".csv"}:
        return "data"
    return "other_text"


def decode_eligible_text(path: str, raw: bytes):
    if len(raw) > MAX_FILE_BYTES or b"\0" in raw:
        return None
    if SECRET_NAME.search(Path(path).name):
        return None
    if Path(path).suffix.lower() not in TEXT_EXTENSIONS and Path(path).name not in {
        "Dockerfile", "Makefile", ".gitignore"
    }:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


class FilePullService:
    """Snapshots local working-tree text and a GitHub branch into append-preserving tables."""

    def __init__(self, repository_root: Path, database_path: Path):
        self.root = Path(repository_root).expanduser().resolve()
        self.database_path = Path(database_path).expanduser().resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._init_database()
        self.remote_url = git_read(self.root, "remote", "get-url", "origin")
        self.local_branch = git_read(self.root, "branch", "--show-current") or "unknown"
        self.remote_branch = os.environ.get("ERIA_REMOTE_BRANCH", self.local_branch)
        match = re.search(r"github\.com[:/]([^/]+)/([^/.]+)(?:\.git)?$", self.remote_url)
        self.owner, self.repository = (match.group(1), match.group(2)) if match else (None, None)

    def _connect(self):
        db = sqlite3.connect(str(self.database_path), timeout=20)
        db.row_factory = sqlite3.Row
        return db

    def _init_database(self):
        with self._connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS pull_blobs(
              sha256 TEXT PRIMARY KEY, content TEXT NOT NULL,
              byte_length INTEGER NOT NULL, created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS pull_files(
              source TEXT NOT NULL, path TEXT NOT NULL, category TEXT NOT NULL,
              sha256 TEXT NOT NULL, source_ref TEXT NOT NULL, source_commit TEXT NOT NULL,
              status TEXT NOT NULL, byte_length INTEGER NOT NULL,
              first_seen TEXT NOT NULL, last_seen TEXT NOT NULL,
              PRIMARY KEY(source,path)
            );
            CREATE TABLE IF NOT EXISTS pull_file_versions(
              id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT NOT NULL,
              path TEXT NOT NULL, sha256 TEXT NOT NULL, source_ref TEXT NOT NULL,
              source_commit TEXT NOT NULL, category TEXT NOT NULL,
              byte_length INTEGER NOT NULL, imported_at TEXT NOT NULL,
              UNIQUE(source,path,sha256,source_ref,source_commit)
            );
            CREATE INDEX IF NOT EXISTS idx_pull_versions_source_path
              ON pull_file_versions(source,path,id);
            CREATE TABLE IF NOT EXISTS pull_jobs(
              id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT NOT NULL,
              status TEXT NOT NULL, scanned INTEGER NOT NULL, imported INTEGER NOT NULL,
              unchanged INTEGER NOT NULL, skipped INTEGER NOT NULL, missing INTEGER NOT NULL,
              source_ref TEXT NOT NULL, source_commit TEXT NOT NULL,
              started_at TEXT NOT NULL, finished_at TEXT NOT NULL, detail TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS pull_audit(
              id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL,
              detail_json TEXT NOT NULL, created_at TEXT NOT NULL
            );
            CREATE TRIGGER IF NOT EXISTS pull_audit_no_update
              BEFORE UPDATE ON pull_audit BEGIN
                SELECT RAISE(ABORT,'pull_audit is append-only');
              END;
            CREATE TRIGGER IF NOT EXISTS pull_audit_no_delete
              BEFORE DELETE ON pull_audit BEGIN
                SELECT RAISE(ABORT,'pull_audit is append-only');
              END;
            """)

    def _audit(self, event: str, detail: dict):
        with self._lock, self._connect() as db:
            db.execute(
                "INSERT INTO pull_audit(event,detail_json,created_at) VALUES(?,?,?)",
                (event, json.dumps(detail, ensure_ascii=False, sort_keys=True), utc_now()),
            )

    def _record(self, source: str, path: str, content: str, source_ref: str, commit: str):
        raw = content.encode("utf-8")
        digest = hashlib.sha256(raw).hexdigest()
        category = classify_path(path)
        stamp = utc_now()
        with self._lock, self._connect() as db:
            db.execute(
                "INSERT OR IGNORE INTO pull_blobs(sha256,content,byte_length,created_at) VALUES(?,?,?,?)",
                (digest, content, len(raw), stamp),
            )
            old = db.execute(
                "SELECT sha256,first_seen FROM pull_files WHERE source=? AND path=?",
                (source, path),
            ).fetchone()
            changed = old is None or old["sha256"] != digest
            db.execute("""
              INSERT INTO pull_files(source,path,category,sha256,source_ref,source_commit,
                status,byte_length,first_seen,last_seen)
              VALUES(?,?,?,?,?,?,'present',?,?,?)
              ON CONFLICT(source,path) DO UPDATE SET
                category=excluded.category, sha256=excluded.sha256,
                source_ref=excluded.source_ref, source_commit=excluded.source_commit,
                status='present', byte_length=excluded.byte_length, last_seen=excluded.last_seen
            """, (
                source, path, category, digest, source_ref, commit, len(raw),
                old["first_seen"] if old else stamp, stamp,
            ))
            if changed:
                db.execute("""
                  INSERT OR IGNORE INTO pull_file_versions
                    (source,path,sha256,source_ref,source_commit,category,byte_length,imported_at)
                  VALUES(?,?,?,?,?,?,?,?)
                """, (source, path, digest, source_ref, commit, category, len(raw), stamp))
        return changed

    def _mark_missing(self, source: str, seen: set[str]):
        with self._lock, self._connect() as db:
            rows = db.execute(
                "SELECT path FROM pull_files WHERE source=? AND status='present'", (source,)
            ).fetchall()
            missing = [row["path"] for row in rows if row["path"] not in seen]
            for path in missing:
                db.execute(
                    "UPDATE pull_files SET status='missing',last_seen=? WHERE source=? AND path=?",
                    (utc_now(), source, path),
                )
        return len(missing)

    def _finish_job(self, source, started, source_ref, commit, counts, missing, status="completed", detail=""):
        finished = utc_now()
        with self._lock, self._connect() as db:
            db.execute("""
              INSERT INTO pull_jobs(source,status,scanned,imported,unchanged,skipped,missing,
                source_ref,source_commit,started_at,finished_at,detail)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                source, status, counts["scanned"], counts["imported"], counts["unchanged"],
                counts["skipped"], missing, source_ref, commit, started, finished, detail[:500],
            ))
        self._audit("file_pull_" + status, {
            "source": source, **counts, "missing": missing,
            "source_ref": source_ref, "source_commit": commit,
        })

    def pull_local(self):
        started = utc_now()
        commit = git_read(self.root, "rev-parse", "HEAD")
        branch = git_read(self.root, "branch", "--show-current") or "unknown"
        observed = set()
        counts = {"scanned": 0, "imported": 0, "unchanged": 0, "skipped": 0}
        for base, directories, files in os.walk(self.root, followlinks=False):
            directories[:] = [name for name in directories if name not in SKIP_DIRS]
            for filename in files:
                path = Path(base) / filename
                relative = path.relative_to(self.root).as_posix()
                observed.add(relative)
                if SECRET_NAME.search(filename) or path.is_symlink():
                    counts["skipped"] += 1
                    continue
                counts["scanned"] += 1
                try:
                    if path.stat().st_size > MAX_FILE_BYTES:
                        counts["skipped"] += 1
                        continue
                    content = decode_eligible_text(relative, path.read_bytes())
                    if content is None:
                        counts["skipped"] += 1
                        continue
                    key = "imported" if self._record("local", relative, content, branch, commit) else "unchanged"
                    counts[key] += 1
                except OSError:
                    counts["skipped"] += 1
        missing = self._mark_missing("local", observed)
        self._finish_job("local", started, branch, commit, counts, missing)
        return {"source": "local", **counts, "missing": missing, "branch": branch, "commit": commit}

    def _github_json(self, url: str):
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "ERIA-FilePull/1.0"}
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if token:
            headers["Authorization"] = "Bearer " + token
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    def _github_raw(self, path: str, commit: str):
        # Pin raw retrieval to the exact commit whose tree was enumerated.
        relative = urllib.parse.quote(path, safe="/")
        url = "https://raw.githubusercontent.com/{}/{}/{}/{}".format(
            self.owner, self.repository, commit, relative
        )
        headers = {"User-Agent": "ERIA-FilePull/1.0"}
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if token:
            headers["Authorization"] = "Bearer " + token
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read(MAX_FILE_BYTES + 1)

    def pull_github(self):
        if not self.owner:
            raise RuntimeError("origin is not a recognized GitHub repository URL")
        started = utc_now()
        branch_ref = urllib.parse.quote(self.remote_branch, safe="")
        branch_data = self._github_json(
            "https://api.github.com/repos/{}/{}/branches/{}".format(
                self.owner, self.repository, branch_ref
            )
        )
        commit = branch_data["commit"]["sha"]
        tree = self._github_json(
            "https://api.github.com/repos/{}/{}/git/trees/{}?recursive=1".format(
                self.owner, self.repository, commit
            )
        )
        if tree.get("truncated"):
            raise RuntimeError("GitHub tree is truncated; refusing to mark unseen paths missing")
        observed = set()
        counts = {"scanned": 0, "imported": 0, "unchanged": 0, "skipped": 0}
        for item in tree.get("tree", []):
            if item.get("type") != "blob":
                continue
            path = item.get("path", "")
            if path:
                observed.add(path)
            if (
                not path or any(part in SKIP_DIRS for part in Path(path).parts)
                or SECRET_NAME.search(Path(path).name)
                or (Path(path).suffix.lower() not in TEXT_EXTENSIONS
                    and Path(path).name not in {"Dockerfile", "Makefile", ".gitignore"})
            ):
                counts["skipped"] += 1
                continue
            counts["scanned"] += 1
            if int(item.get("size", 0)) > MAX_FILE_BYTES:
                counts["skipped"] += 1
                continue
            try:
                content = decode_eligible_text(path, self._github_raw(path, commit))
                if content is None:
                    counts["skipped"] += 1
                    continue
                key = "imported" if self._record(
                    "github", path, content, self.remote_branch, commit
                ) else "unchanged"
                counts[key] += 1
            except Exception:
                counts["skipped"] += 1
        missing = self._mark_missing("github", observed)
        self._finish_job("github", started, self.remote_branch, commit, counts, missing)
        return {
            "source": "github", **counts, "missing": missing,
            "branch": self.remote_branch, "commit": commit,
        }

    def sync_all(self):
        results = {"local": self.pull_local()}
        try:
            results["github"] = self.pull_github()
        except Exception as exc:
            results["github"] = {
                "source": "github", "status": "error",
                "error": type(exc).__name__ + ": " + str(exc)[:250],
            }
            self._audit("github_pull_failed", {"error_type": type(exc).__name__})
        return {"ok": results["github"].get("status") != "error", "results": results, "status": self.status()}

    def status(self):
        with self._connect() as db:
            counts = [dict(row) for row in db.execute(
                "SELECT source,status,COUNT(*) AS count FROM pull_files GROUP BY source,status"
            )]
            versions = db.execute("SELECT COUNT(*) FROM pull_file_versions").fetchone()[0]
            jobs = [dict(row) for row in db.execute(
                "SELECT source,status,scanned,imported,unchanged,skipped,missing,source_ref,"
                "source_commit,finished_at FROM pull_jobs ORDER BY id DESC LIMIT 10"
            )]
        return {
            "repository": str(self.root), "remote": self.remote_url,
            "local_branch": self.local_branch, "remote_branch": self.remote_branch,
            "file_counts": counts, "version_records": versions, "recent_jobs": jobs,
            "schedule_minutes": int(os.environ.get("ERIA_PULL_INTERVAL_MINUTES", "60")),
        }


def start_scheduler(service: FilePullService):
    """Run startup sync and periodic sync without delaying HTTP server startup."""
    interval = int(os.environ.get("ERIA_PULL_INTERVAL_MINUTES", "60"))
    stop = threading.Event()

    def worker():
        try:
            service.sync_all()
        except Exception as exc:
            service._audit("startup_pull_failed", {"error_type": type(exc).__name__})
        while interval > 0 and not stop.wait(interval * 60):
            try:
                service.sync_all()
            except Exception as exc:
                service._audit("scheduled_pull_failed", {"error_type": type(exc).__name__})

    thread = threading.Thread(target=worker, name="eria-file-pull", daemon=True)
    thread.start()
    return stop
