"""ERIA content-addressed Data Vault for immutable Git-commit acquisition.

The vault lives outside the checkout. It reads Git objects from one exact commit,
stores eligible original bytes by SHA-256, and appends provenance records to a
hash-chained JSONL manifest. It never edits the source repository or Git history.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

DEFAULT_VAULT = Path.home() / ".eria" / "vault"
MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_FILES = 50_000
SKIP_PARTS = {".git", ".gradle", ".idea", ".venv", "venv", "__pycache__",
              "node_modules", "vendor", "build", "dist", ".eria"}
SENSITIVE = re.compile(
    r"(^|/)(\.env(?:\.|$)|secrets?|credentials?|id_rsa|id_ed25519|"
    r"[^/]*\.pem|[^/]*\.p12|[^/]*\.jks|[^/]*keystore[^/]*)(/|$)", re.I
)
TOKEN = re.compile(r"[\w'-]{2,}", re.UNICODE)
TEXT_SUFFIXES = {
    ".py", ".sh", ".bash", ".kt", ".kts", ".java", ".c", ".h", ".hpp",
    ".cpp", ".rs", ".go", ".js", ".jsx", ".ts", ".tsx", ".html", ".css",
    ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    ".gradle", ".sql", ".xml", ".properties", ".ptn", ".csv",
}


class VaultError(RuntimeError):
    """Vault acquisition or integrity failure."""


def _git(repo: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True, capture_output=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise VaultError("Git object read failed: " + " ".join(args[:2])) from exc
    return result.stdout


def _canonical(value: dict[str, Any]) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def _safe_path(path: str) -> bool:
    parts = Path(path).parts
    return bool(path) and not path.startswith("/") and "\\" not in path and (
        all(part not in {"", ".", ".."} for part in parts)
        and not any(part in SKIP_PARTS for part in parts)
        and not SENSITIVE.search(path)
    )


def _wordplay(data: bytes, path: str) -> dict[str, Any] | None:
    if Path(path).suffix.lower() not in TEXT_SUFFIXES or b"\0" in data[:8192]:
        return None
    try:
        text = data.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError:
        return None
    words = [w.casefold() for w in TOKEN.findall(text)]
    if not words:
        return {"word_count": 0, "top_terms": [], "alliteration": [], "ending_groups": []}
    counts = Counter(words)
    starts: dict[str, set[str]] = defaultdict(set)
    endings: dict[str, set[str]] = defaultdict(set)
    for word in set(words):
        normalized = re.sub(r"[^a-z]", "", word)
        if len(normalized) >= 3:
            starts[normalized[0]].add(normalized)
            endings[normalized[-3:]].add(normalized)
    alliteration = [
        {"sound": key, "words": sorted(value)[:20]}
        for key, value in sorted(starts.items())
        if len(value) >= 3
    ][:40]
    ending_groups = [
        {"ending": key, "words": sorted(value)[:20]}
        for key, value in sorted(endings.items())
        if len(value) >= 3
    ][:40]
    return {
        "word_count": len(words),
        "top_terms": [{"term": word, "count": count}
                      for word, count in counts.most_common(100)],
        "alliteration": alliteration,
        "ending_groups": ending_groups,
    }


def _atomic_object(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if hashlib.sha256(path.read_bytes()).digest() != hashlib.sha256(data).digest():
            raise VaultError("Content-address collision or damaged object: " + str(path))
        return
    fd, temporary = tempfile.mkstemp(prefix=".vault-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            if hashlib.sha256(path.read_bytes()).digest() != hashlib.sha256(data).digest():
                raise VaultError("Concurrent object collision: " + str(path))
        finally:
            os.unlink(temporary)
    except Exception:
        if os.path.exists(temporary):
            os.unlink(temporary)
        raise


def _manifest_head(manifest: Path) -> str:
    if not manifest.exists():
        return "0" * 64
    previous = "0" * 64
    with manifest.open("rb") as stream:
        for raw in stream:
            if not raw.strip():
                continue
            try:
                row = json.loads(raw)
                supplied = row.pop("record_hash")
                if row.get("previous_record_hash") != previous:
                    raise VaultError("Manifest chain link mismatch.")
                expected = hashlib.sha256(_canonical(row)).hexdigest()
                if supplied != expected:
                    raise VaultError("Manifest record hash mismatch.")
                previous = supplied
            except (ValueError, KeyError, TypeError) as exc:
                raise VaultError("Manifest is malformed or tampered.") from exc
    return previous


def verify_vault(vault: str | Path) -> dict[str, Any]:
    root = Path(vault).expanduser().resolve()
    manifest = root / "manifest.jsonl"
    previous = _manifest_head(manifest)
    checked = 0
    if manifest.exists():
        with manifest.open("r", encoding="utf-8") as stream:
            for line in stream:
                if not line.strip():
                    continue
                row = json.loads(line)
                object_path = root / "objects" / row["sha256"][:2] / row["sha256"][2:]
                if not object_path.is_file():
                    raise VaultError("Missing object for " + row["sha256"])
                digest = hashlib.sha256(object_path.read_bytes()).hexdigest()
                if digest != row["sha256"]:
                    raise VaultError("Object hash mismatch for " + row["sha256"])
                checked += 1
    return {"status": "VERIFIED", "records": checked,
            "manifest_head": previous, "source_mutations": False,
            "git_mutations": False}


def acquire_commit(repository: str | Path, commit: str, vault: str | Path = DEFAULT_VAULT) -> dict[str, Any]:
    repo = Path(repository).expanduser().resolve(strict=True)
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise VaultError("A full 40-character commit SHA is required.")
    resolved = _git(repo, "rev-parse", commit).decode("ascii").strip()
    if resolved != commit:
        raise VaultError("Commit anchor did not resolve exactly.")
    tree = _git(repo, "ls-tree", "-rz", "-r", "--full-tree", commit)
    entries = tree.split(b"\0")
    vault_root = Path(vault).expanduser().resolve()
    objects = vault_root / "objects"
    manifest = vault_root / "manifest.jsonl"
    indexes = vault_root / "wordplay"
    objects.mkdir(parents=True, exist_ok=True)
    indexes.mkdir(parents=True, exist_ok=True)
    captured = 0
    skipped_sensitive = 0
    skipped_large = 0
    skipped_special = 0
    with (vault_root / ".manifest.lock").open("a+b") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        previous = _manifest_head(manifest)
        existing = set()
        if manifest.exists():
            with manifest.open("r", encoding="utf-8") as stream:
                for line in stream:
                    if line.strip():
                        row = json.loads(line)
                        if row.get("commit_sha") == commit:
                            existing.add(row.get("path"))
        new_records = []
        for entry in entries:
            if not entry:
                continue
            try:
                metadata, raw_path = entry.split(b"\t", 1)
                mode, kind, blob = metadata.decode("ascii").split(" ", 2)
                path = raw_path.decode("utf-8", errors="strict")
            except (ValueError, UnicodeDecodeError):
                skipped_special += 1
                continue
            if kind != "blob" or mode not in {"100644", "100755"}:
                skipped_special += 1
                continue
            if not _safe_path(path):
                skipped_sensitive += 1
                continue
            if path in existing:
                continue
            data = _git(repo, "cat-file", "blob", blob)
            if len(data) > MAX_FILE_BYTES:
                skipped_large += 1
                continue
            digest = hashlib.sha256(data).hexdigest()
            _atomic_object(objects / digest[:2] / digest[2:], data)
            wordplay = _wordplay(data, path)
            record = {
                "schema": "eria-vault-record-v1",
                "commit_sha": commit,
                "git_blob_sha": blob,
                "path": path,
                "mode": mode,
                "size_bytes": len(data),
                "sha256": digest,
                "wordplay": wordplay,
                "previous_record_hash": previous,
            }
            record_hash = hashlib.sha256(_canonical(record)).hexdigest()
            stored = dict(record)
            stored["record_hash"] = record_hash
            new_records.append(stored)
            previous = record_hash
            captured += 1
            if captured >= MAX_FILES:
                break
        if new_records:
            with manifest.open("ab") as stream:
                for record in new_records:
                    stream.write(_canonical(record) + b"\n")
                stream.flush()
                os.fsync(stream.fileno())
            index_path = indexes / (commit + ".json")
            index_payload = {
                "schema": "eria-vault-wordplay-v1", "commit_sha": commit,
                "records": [{"path": r["path"], "sha256": r["sha256"],
                             "wordplay": r["wordplay"]}
                            for r in new_records if r["wordplay"] is not None],
            }
            _atomic_object(index_path, json.dumps(
                index_payload, ensure_ascii=False, sort_keys=True, indent=2
            ).encode("utf-8"))
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    return {
        "status": "CAPTURED" if captured else "ALREADY_PRESENT",
        "anchor_commit": commit, "new_records": captured,
        "skipped_sensitive_or_excluded": skipped_sensitive,
        "skipped_large": skipped_large, "skipped_non_regular": skipped_special,
        "vault": str(vault_root), "manifest_head": previous,
        "source_mutations": False, "git_mutations": False,
        "automatic_repeat": "Run capture again for a new exact commit; existing commit/path records are not overwritten.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ERIA content-addressed Data Vault")
    sub = parser.add_subparsers(dest="command", required=True)
    capture = sub.add_parser("capture", help="Acquire an exact Git commit into the sidecar vault")
    capture.add_argument("repository")
    capture.add_argument("--anchor", required=True)
    capture.add_argument("--vault", default=str(DEFAULT_VAULT))
    watch = sub.add_parser("watch", help="Poll Git HEAD and acquire each newly observed commit")
    watch.add_argument("repository")
    watch.add_argument("--interval", type=int, default=300, help="Polling seconds (minimum 30)")
    watch.add_argument("--vault", default=str(DEFAULT_VAULT))
    verify = sub.add_parser("verify", help="Verify manifest chain and stored objects")
    verify.add_argument("--vault", default=str(DEFAULT_VAULT))
    args = parser.parse_args(argv)
    try:
        if args.command == "capture":
            result = acquire_commit(args.repository, args.anchor, args.vault)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.command == "verify":
            print(json.dumps(verify_vault(args.vault), ensure_ascii=False, indent=2))
            return 0
        if args.interval < 30:
            raise VaultError("Watch interval must be at least 30 seconds.")
        repository = Path(args.repository).expanduser().resolve(strict=True)
        last_seen = None
        print(json.dumps({"status": "WATCHING", "repository": str(repository),
                          "interval_seconds": args.interval, "vault": args.vault}), flush=True)
        while True:
            commit = _git(repository, "rev-parse", "HEAD").decode("ascii").strip()
            if commit != last_seen:
                result = acquire_commit(repository, commit, args.vault)
                print(json.dumps(result, ensure_ascii=False), flush=True)
                last_seen = commit
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print(json.dumps({"status": "STOPPED", "reason": "operator interrupt"}))
        return 0
    except (VaultError, OSError) as exc:
        print(json.dumps({"status": "HOLD", "reason": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
