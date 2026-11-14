#!/usr/bin/env python3
"""Import the committed main-branch snapshot into ERIA without replacing records.

This reads Git objects only (no checkout, branch switch, merge, or working-tree
writes). It creates two additive ERIA tables and stores source bytes plus Git
and SHA-256 provenance. Existing ERIA tables and rows are never updated/deleted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SKIP_COMPONENTS = {".git", ".eria", ".venv", "venv", "__pycache__", "node_modules"}
SECRET_NAMES = {".env", ".env.local", ".env.production"}
MAX_FILE_BYTES = 25 * 1024 * 1024
MAX_TOTAL_BYTES = 250 * 1024 * 1024


def git(root: Path, *args: str) -> bytes:
    p = subprocess.run(["git", "-C", str(root), *args],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        raise RuntimeError(p.stderr.decode("utf-8", "replace").strip())
    return p.stdout


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=".", help="Existing CodEXgen Git checkout")
    ap.add_argument("--ref", default="main", help="Git ref to import (default: main)")
    ap.add_argument("--database", required=True, help="ERIA SQLite database path")
    ap.add_argument("--max-file-bytes", type=int, default=MAX_FILE_BYTES)
    ap.add_argument("--max-total-bytes", type=int, default=MAX_TOTAL_BYTES)
    args = ap.parse_args()

    root = Path(args.repo).expanduser().resolve()
    db_path = Path(args.database).expanduser().resolve()
    if not (root / ".git").exists():
        raise RuntimeError(f"Not a Git checkout: {root}")
    if not db_path.is_file():
        raise RuntimeError(f"ERIA database does not exist: {db_path}")

    commit = git(root, "rev-parse", "--verify", f"{args.ref}^{{commit}}").decode().strip()
    entries = git(root, "ls-tree", "-rz", "--full-tree", commit).split(b"\0")
    parsed = []
    for entry in entries:
        if not entry:
            continue
        meta, path_bytes = entry.split(b"\t", 1)
        mode, obj_type, blob_sha = meta.decode("ascii").split()
        path = path_bytes.decode("utf-8", "surrogateescape")
        parts = Path(path).parts
        lower_name = Path(path).name.lower()
        if obj_type != "blob" or mode == "120000":
            continue
        if any(part in SKIP_COMPONENTS for part in parts):
            continue
        if lower_name in SECRET_NAMES or lower_name.startswith(("id_rsa", "id_ed25519")):
            continue
        parsed.append((path, mode, blob_sha))

    con = sqlite3.connect(db_path, timeout=30)
    imported = 0
    skipped_large = 0
    total = 0
    try:
        con.execute("PRAGMA busy_timeout=30000")
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("BEGIN IMMEDIATE")
        con.execute("""
            CREATE TABLE IF NOT EXISTS eria_main_import_batches (
                commit_sha TEXT PRIMARY KEY,
                ref_name TEXT NOT NULL,
                source_repository TEXT NOT NULL,
                imported_files INTEGER NOT NULL,
                skipped_large_files INTEGER NOT NULL,
                imported_bytes INTEGER NOT NULL,
                imported_at TEXT NOT NULL
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS eria_main_import_files (
                commit_sha TEXT NOT NULL,
                source_path TEXT NOT NULL,
                git_blob_sha TEXT NOT NULL,
                content_sha256 TEXT NOT NULL,
                mode TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                content BLOB NOT NULL,
                imported_at TEXT NOT NULL,
                PRIMARY KEY (commit_sha, source_path, git_blob_sha)
            )
        """)
        existing = con.execute(
            "SELECT 1 FROM eria_main_import_batches WHERE commit_sha=?", (commit,)
        ).fetchone()
        if existing:
            con.rollback()
            print(json.dumps({
                "status": "already_imported", "commit": commit,
                "database": str(db_path), "existing_records_preserved": True
            }, indent=2))
            return 0

        now = datetime.now(timezone.utc).isoformat()
        for path, mode, blob_sha in parsed:
            raw = git(root, "cat-file", "blob", blob_sha)
            if len(raw) > args.max_file_bytes or total + len(raw) > args.max_total_bytes:
                skipped_large += 1
                continue
            digest = hashlib.sha256(raw).hexdigest()
            con.execute("""
                INSERT OR IGNORE INTO eria_main_import_files
                (commit_sha, source_path, git_blob_sha, content_sha256,
                 mode, size_bytes, content, imported_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (commit, path, blob_sha, digest, mode, len(raw), raw, now))
            imported += 1
            total += len(raw)

        con.execute("""
            INSERT INTO eria_main_import_batches
            (commit_sha, ref_name, source_repository, imported_files,
             skipped_large_files, imported_bytes, imported_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (commit, args.ref, str(root), imported, skipped_large, total, now))
        con.commit()
        check = con.execute("PRAGMA integrity_check").fetchone()[0]
        if check != "ok":
            raise RuntimeError(f"SQLite integrity check failed after import: {check}")
        print(json.dumps({
            "status": "imported", "ref": args.ref, "commit": commit,
            "database": str(db_path), "candidate_files": len(parsed),
            "imported_files": imported, "skipped_large_files": skipped_large,
            "imported_bytes": total, "integrity": check,
            "existing_records_overwritten": 0, "existing_records_deleted": 0,
            "git_history_modified": False, "working_tree_modified": False
        }, indent=2))
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
