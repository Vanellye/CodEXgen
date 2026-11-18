#!/usr/bin/env python3
"""ERIA Generation Genesis: auditable, idempotent continuous generation worker."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from code_generator import DEFAULT_SPEC, CodeGeneratorEngine, ModuleSpecification  # noqa: E402

STOP = False


def request_stop(_signum: int, _frame: object) -> None:
    global STOP
    STOP = True


def sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_revision() -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return os.environ.get("GITHUB_SHA")


def append_record(audit_path: Path, record: dict[str, object]) -> None:
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()
    fd = os.open(audit_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        os.write(fd, payload)
        os.fsync(fd)
    finally:
        os.close(fd)


def run_cycle(output_dir: Path, audit_path: Path) -> int:
    source = ROOT / "python" / "code_generator.py"
    target = output_dir / f'{DEFAULT_SPEC["module_name"].lower()}_module.py'
    source_hash = sha256(source)
    before_hash = sha256(target)
    started = time.monotonic()
    started_at = datetime.now(timezone.utc).isoformat()
    status = "passed"
    error = None
    try:
        spec = ModuleSpecification(**DEFAULT_SPEC)
        generated_path = Path(CodeGeneratorEngine(str(output_dir)).build_module(spec))
        after_hash = sha256(generated_path)
        outcome = "generated" if before_hash != after_hash else "unchanged"
    except Exception as exc:  # audit failures without hiding the original error
        status, outcome, error = "failed", "error", f"{type(exc).__name__}: {exc}"
        after_hash = sha256(target)
    record = {
        "schema": "ERIA-GENESIS-RUN/1",
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "duration_ms": round((time.monotonic() - started) * 1000, 3),
        "status": status,
        "outcome": outcome,
        "repository_revision": git_revision(),
        "generator": "python/code_generator.py",
        "source_sha256": source_hash,
        "output_path": str(target.relative_to(ROOT)) if target.is_relative_to(ROOT) else str(target),
        "output_sha256": after_hash,
        "human_approval_required_for": ["repository_write", "merge", "release", "deployment", "deletion"],
        "error": error,
    }
    append_record(audit_path, record)
    print(json.dumps(record, sort_keys=True))
    return 1 if status == "failed" else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run auditable Generation Genesis cycles.")
    parser.add_argument("--once", action="store_true", help="Run one bounded generation cycle.")
    parser.add_argument("--interval", type=int, default=900, help="Seconds between cycles (minimum 60).")
    parser.add_argument("--out", type=Path, default=ROOT / "generated_modules")
    parser.add_argument("--audit", type=Path, default=ROOT / ".eria" / "genesis-runs.jsonl")
    parser.add_argument("--lock", type=Path, default=ROOT / ".eria" / "genesis.lock")
    args = parser.parse_args()
    if args.interval < 60:
        parser.error("--interval must be at least 60 seconds")

    args.lock.parent.mkdir(parents=True, exist_ok=True)
    with args.lock.open("a+") as lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("Genesis worker already holds the execution lock.", file=sys.stderr)
            return 2

        if args.once:
            return run_cycle(args.out.resolve(), args.audit.resolve())

        signal.signal(signal.SIGTERM, request_stop)
        signal.signal(signal.SIGINT, request_stop)
        exit_code = 0
        print(f"Generation Genesis active; interval={args.interval}s. Stop with Ctrl+C.")
        while not STOP:
            exit_code = run_cycle(args.out.resolve(), args.audit.resolve())
            if STOP:
                break
            deadline = time.monotonic() + args.interval
            while not STOP and time.monotonic() < deadline:
                time.sleep(min(1.0, max(0.0, deadline - time.monotonic())))
        print("Generation Genesis stopped cleanly.")
        return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
