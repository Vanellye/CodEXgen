"""ERIA isolated test/build runner.

Requires Linux bubblewrap. Commands run in a fresh git-archive workspace with
network namespaces disabled, read-only system mounts, no host home/secrets,
and a writable temporary project copy. An HMAC-scoped approval is required.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import secrets
import shutil
import subprocess
import tarfile
import tempfile
import time
from pathlib import Path, PurePosixPath

COMMANDS = {
    "python-tests": ["python", "-m", "pytest", "-q"],
    "android-debug-build": ["./gradlew", "assembleDebug"],
    "make-check-review": ["make", "check"],
}
MAX_SECONDS = 900
MAX_OUTPUT = 2_000_000


def _paths():
    home = Path.home() / ".eria"
    return home / "runner.key", home / "runner-approvals"


def _key(create=False):
    key_path, _ = _paths()
    key_path.parent.mkdir(parents=True, exist_ok=True)
    if not key_path.exists():
        if not create:
            raise RuntimeError("Runner approval key is missing; issue an approval interactively first.")
        fd = os.open(key_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(secrets.token_bytes(32))
    if key_path.stat().st_mode & 0o077:
        raise RuntimeError("Runner key permissions must be 0600.")
    return key_path.read_bytes()


def _revision(root):
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True, timeout=8,
    ).stdout.strip()


def issue_approval(repository, command_id, lifetime_minutes=15):
    root = Path(repository).resolve(strict=True)
    if command_id not in COMMANDS:
        raise ValueError("Unknown fixed command identifier.")
    if not shutil.which("bwrap"):
        raise RuntimeError("bubblewrap is unavailable; isolated execution remains HOLD.")
    if not 1 <= lifetime_minutes <= 30:
        raise ValueError("Approval lifetime must be 1–30 minutes.")
    commit = _revision(root)
    phrase = f"APPROVE {command_id} {commit[:12]}"
    print("Exact one-command approval:")
    print(phrase)
    if input("Type the exact phrase to authorize this isolated run: ").strip() != phrase:
        raise RuntimeError("Approval phrase mismatch; no grant created.")
    key = _key(create=True)
    payload = {
        "id": secrets.token_hex(16), "repository": str(root),
        "commit": commit, "command_id": command_id,
        "argv": COMMANDS[command_id], "expires_at": int(time.time()) + lifetime_minutes * 60,
        "nonce": secrets.token_hex(16),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["signature"] = hmac.new(key, canonical, hashlib.sha256).hexdigest()
    _, approvals = _paths()
    approvals.mkdir(parents=True, exist_ok=True)
    destination = approvals / (payload["id"] + ".json")
    fd = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(payload, stream, sort_keys=True)
    return {"approval_id": payload["id"], "commit": commit,
            "command_id": command_id, "expires_at": payload["expires_at"],
            "scope": "one command, one commit, one use"}


def _consume_approval(approval_id, root, command_id):
    if not approval_id or any(c not in "0123456789abcdef" for c in approval_id):
        raise RuntimeError("A valid approval identifier is required.")
    _, approvals = _paths()
    grant_path = approvals / (approval_id + ".json")
    raw = grant_path.read_bytes()
    grant_path.unlink()  # one-use even if later validation fails
    grant = json.loads(raw)
    signature = grant.pop("signature", "")
    canonical = json.dumps(grant, sort_keys=True, separators=(",", ":")).encode()
    expected = hmac.new(_key(), canonical, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise RuntimeError("Approval signature invalid.")
    if grant["repository"] != str(root) or grant["commit"] != _revision(root):
        raise RuntimeError("Approval repository or commit no longer matches.")
    if grant["command_id"] != command_id or grant["argv"] != COMMANDS[command_id]:
        raise RuntimeError("Approval command scope mismatch.")
    if int(time.time()) > int(grant["expires_at"]):
        raise RuntimeError("Approval expired.")
    return grant


def _extract_archive(root, commit, destination):
    archive = subprocess.run(
        ["git", "-C", str(root), "archive", "--format=tar", commit],
        check=True, capture_output=True, timeout=60,
    )
    import io
    with tarfile.open(fileobj=io.BytesIO(archive.stdout), mode="r:") as bundle:
        for member in bundle.getmembers():
            name = PurePosixPath(member.name)
            if name.is_absolute() or ".." in name.parts or not (member.isfile() or member.isdir()):
                raise RuntimeError("Unsafe archive member rejected.")
        bundle.extractall(destination)


def run_approved(repository, command_id, approval_id, timeout=MAX_SECONDS):
    root = Path(repository).resolve(strict=True)
    if command_id not in COMMANDS:
        raise ValueError("Command is not in the fixed allowlist.")
    if not shutil.which("bwrap"):
        raise RuntimeError("bubblewrap unavailable: execution_state=HOLD.")
    if not 1 <= timeout <= MAX_SECONDS:
        raise ValueError("Timeout outside allowed range.")
    grant = _consume_approval(approval_id, root, command_id)
    commit = grant["commit"]
    started = time.time()
    with tempfile.TemporaryDirectory(prefix="eria-run-") as temporary:
        workspace = Path(temporary) / "workspace"
        workspace.mkdir(mode=0o700)
        _extract_archive(root, commit, workspace)
        bwrap = [
            shutil.which("bwrap"), "--unshare-all", "--die-with-parent",
            "--new-session", "--ro-bind", "/usr", "/usr",
        ]
        for system_path in ("/bin", "/lib", "/lib64"):
            if Path(system_path).exists():
                bwrap += ["--ro-bind", system_path, system_path]
        bwrap += [
            "--proc", "/proc", "--dev", "/dev",
            "--tmpfs", "/tmp", "--dir", "/workspace",
            "--bind", str(workspace), "/workspace",
            "--chdir", "/workspace",
            "--setenv", "HOME", "/tmp",
            "--setenv", "PATH", "/usr/bin:/bin",
            "--setenv", "PYTHONDONTWRITEBYTECODE", "1",
            "--", *COMMANDS[command_id],
        ]
        try:
            proc = subprocess.run(
                bwrap, capture_output=True, text=True, timeout=timeout,
                env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"},
            )
            status = "PASSED" if proc.returncode == 0 else "FAILED"
            exit_code = proc.returncode
            stdout, stderr = proc.stdout, proc.stderr
        except subprocess.TimeoutExpired as exc:
            status, exit_code = "TIMEOUT", None
            stdout = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            stderr = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
    stdout = stdout[-MAX_OUTPUT:]
    stderr = stderr[-MAX_OUTPUT:]
    elapsed = round(time.time() - started, 3)
    result = {
        "runner": "ERIA bubblewrap isolated runner", "status": status,
        "execution_state": "COMPLETED", "command_id": command_id,
        "argv": COMMANDS[command_id], "repository": str(root), "commit": commit,
        "approval_id": approval_id, "exit_code": exit_code,
        "duration_seconds": elapsed, "stdout": stdout, "stderr": stderr,
        "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
        "stderr_sha256": hashlib.sha256(stderr.encode()).hexdigest(),
        "network_namespace": "unshared", "workspace": "temporary_git_archive",
        "host_checkout_writable": False, "host_home_mounted": False,
        "source_mutations": False, "git_mutations": False,
        "authority": "EXECUTION_EVIDENCE_NOT_SOURCE_TRUTH",
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    approve = sub.add_parser("approve")
    approve.add_argument("repository")
    approve.add_argument("command_id", choices=sorted(COMMANDS))
    approve.add_argument("--minutes", type=int, default=15)
    run = sub.add_parser("run")
    run.add_argument("repository")
    run.add_argument("command_id", choices=sorted(COMMANDS))
    run.add_argument("--approval-id", required=True)
    run.add_argument("--timeout", type=int, default=MAX_SECONDS)
    args = parser.parse_args()
    if args.action == "approve":
        result = issue_approval(args.repository, args.command_id, args.minutes)
    else:
        result = run_approved(args.repository, args.command_id, args.approval_id, args.timeout)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
