"""Read-only adapter for the local ERIA platform SQLite database."""
from __future__ import annotations
import os, sqlite3
from pathlib import Path

DEFAULT_DB = Path.home() / ".eria" / "data" / "eria_platform.sqlite3"

class PlatformDatabase:
    def __init__(self, path=None):
        self.path = Path(path or os.environ.get("ERIA_PLATFORM_DB", DEFAULT_DB)).expanduser()

    def _connect(self):
        if not self.path.is_file():
            raise FileNotFoundError(f"ERIA platform database not found: {self.path}")
        uri = self.path.resolve().as_uri() + "?mode=ro"
        db = sqlite3.connect(uri, uri=True, timeout=5)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA query_only=ON")
        return db

    def status(self):
        with self._connect() as db:
            integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
            tables = {r[0] for r in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )}
            result = {"database": str(self.path), "integrity": integrity, "tables": {}}
            for table in ("source_files", "derived_artifacts", "translation_jobs",
                          "decoder_jobs", "repository_scans", "audit_events"):
                if table in tables:
                    # Table names are selected only from this fixed allowlist.
                    count = db.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
                    result["tables"][table] = count
            return result

    def source_urls(self, limit=30):
        with self._connect() as db:
            tables = {r[0] for r in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )}
            if "derived_artifacts" not in tables:
                return []
            cols = {r[1] for r in db.execute("PRAGMA table_info(derived_artifacts)")}
            required = {"artifact_id", "artifact_type", "output_path", "transformation"}
            if not required.issubset(cols):
                raise RuntimeError("derived_artifacts schema is not recognized")
            rows = db.execute("""
                SELECT artifact_id, source_id, output_path, transformation, created_at
                FROM derived_artifacts
                WHERE artifact_type='source_url'
                ORDER BY artifact_id DESC LIMIT ?
            """, (max(1, min(int(limit), 100)),)).fetchall()
            return [dict(r) for r in rows]

    def artifact_summary(self, limit=20):
        with self._connect() as db:
            tables = {r[0] for r in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )}
            if "derived_artifacts" not in tables:
                return {"count": 0, "recent": []}
            count = db.execute("SELECT COUNT(*) FROM derived_artifacts").fetchone()[0]
            rows = db.execute("""
                SELECT artifact_id, source_id, artifact_type, output_path,
                       output_sha256, transformation, created_at
                FROM derived_artifacts ORDER BY artifact_id DESC LIMIT ?
            """, (max(1, min(int(limit), 100)),)).fetchall()
            return {"count": count, "recent": [dict(r) for r in rows]}
