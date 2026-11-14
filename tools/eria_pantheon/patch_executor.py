"""PONS-gated exact-content patch executor.

No shell, subprocess, Git operation, or code execution is performed. A grant
authorizes one exact repository-relative file and the SHA-256 of the complete
replacement bytes. Writes are staged beside the target and atomically replaced.
"""
from __future__ import annotations
import hashlib, json, os, re, tempfile, threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .approval import ApprovalError, verify_signed_grant

class PatchHold(PermissionError):
    """Patch is unsafe, unauthorized, or cannot be audited."""

_ALLOWED_ROOTS = {"tools", "tests", "docs", "interfaces"}
_PROTECTED_NAMES = {".git", "storage", "__pycache__"}
_HEX = re.compile(r"^[0-9a-f]{64}$")
_AUDIT_LOCK = threading.RLock()

def _safe_target(root: Path, relative_path: str) -> Path:
    if not isinstance(relative_path, str) or not relative_path or "\\" in relative_path:
        raise PatchHold("A normalized repository-relative path is required.")
    rel = Path(relative_path)
    if rel.is_absolute() or any(part in ("", ".", "..") for part in rel.parts):
        raise PatchHold("Path traversal or absolute paths are not permitted.")
    if len(rel.parts) < 2 or rel.parts[0] not in _ALLOWED_ROOTS:
        raise PatchHold("Patch path is outside the approved source roots.")
    if any(part in _PROTECTED_NAMES for part in rel.parts):
        raise PatchHold("Protected repository or runtime storage paths cannot be patched.")
    cursor = root
    for part in rel.parts[:-1]:
        cursor = cursor / part
        if cursor.is_symlink():
            raise PatchHold("Symlinked parent directories are not patchable.")
    target = root / rel
    if target.is_symlink() or not target.is_file():
        raise PatchHold("Patch target must be an existing regular file, not a symlink.")
    resolved = target.resolve(strict=True)
    if root not in resolved.parents:
        raise PatchHold("Patch target escapes repository root.")
    return resolved

def execute_exact_patch(repository: str | Path, *, relative_path: str,
                        replacement: str | bytes, grant: Any, signing_key: str | bytes,
                        now: int | None = None) -> dict[str, Any]:
    """Verify one signed exact-path/hash grant, atomically replace, and audit."""
    root = Path(repository).resolve(strict=True)
    raw = replacement.encode("utf-8") if isinstance(replacement, str) else replacement
    if not isinstance(raw, bytes) or not raw or len(raw) > 1_000_000:
        raise PatchHold("Replacement must be 1 byte to 1 MB.")
    digest = hashlib.sha256(raw).hexdigest()
    if not _HEX.fullmatch(digest):
        raise PatchHold("Invalid replacement digest.")
    try:
        verified = verify_signed_grant(grant, signing_key,
            capability="eria.source.write", scope=relative_path,
            patch_sha256=digest, now=now)
    except ApprovalError as exc:
        raise PatchHold(str(exc)) from exc
    target = _safe_target(root, relative_path)
    audit_dir = root / "storage" / "approvals"
    if audit_dir.is_symlink():
        raise PatchHold("Audit directory cannot be a symlink.")
    audit_dir.mkdir(parents=True, exist_ok=True)
    if root not in audit_dir.resolve(strict=True).parents:
        raise PatchHold("Audit directory escapes repository.")
    audit = audit_dir / "patch-executions.jsonl"
    before_hash = hashlib.sha256(target.read_bytes()).hexdigest()
    record = {
        "schema": "eria.pons.patch-audit/1.0",
        "grant_id": verified["grant_id"], "nonce": verified["nonce"],
        "capability": verified["capability"], "scope": verified["scope"],
        "patch_sha256": digest, "previous_sha256": before_hash,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "result": "PENDING", "authority": "NON_AUTHORITATIVE",
    }
    with _AUDIT_LOCK:
        if audit.exists():
            for line in audit.read_text(encoding="utf-8").splitlines():
                try:
                    old = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise PatchHold("Patch audit ledger malformed; execution held.") from exc
                if old.get("grant_id") == verified["grant_id"] or old.get("nonce") == verified["nonce"]:
                    raise PatchHold("PONS grant or nonce has already been consumed.")
        fd, temp_name = tempfile.mkstemp(prefix=".eria-patch-", dir=str(target.parent))
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(raw); stream.flush(); os.fsync(stream.fileno())
            os.chmod(temp_name, target.stat().st_mode & 0o777)
            # Recheck identity immediately before replacement.
            if target.is_symlink() or hashlib.sha256(target.read_bytes()).hexdigest() != before_hash:
                raise PatchHold("Target changed during patch preparation.")
            os.replace(temp_name, target)
            record["result"] = "APPLIED"
            record["result_sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
        except Exception:
            try: os.unlink(temp_name)
            except OSError: pass
            record["result"] = "FAILED"
            raise
        finally:
            try:
                fd = os.open(audit, os.O_WRONLY | os.O_CREAT | os.O_APPEND |
                             getattr(os, "O_NOFOLLOW", 0), 0o600)
                with os.fdopen(fd, "a", encoding="utf-8") as stream:
                    stream.write(json.dumps(record, sort_keys=True) + "\\n")
                    stream.flush(); os.fsync(stream.fileno())
            except OSError as exc:
                # Fail loudly: the file may already be changed, but audit failure
                # must never be represented as a successful operation.
                raise PatchHold("Patch outcome could not be durably audited.") from exc
    return {"status": "APPLIED", "path": relative_path, "patch_sha256": digest,
            "previous_sha256": before_hash, "grant_id": verified["grant_id"],
            "audit": "storage/approvals/patch-executions.jsonl",
            "shell_executed": False, "git_mutated": False}
