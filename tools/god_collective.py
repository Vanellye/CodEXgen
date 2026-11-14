#!/usr/bin/env python3
"""GOD Collective: append-only, content-addressed ingestion for ERIA.

No network, Git, shell, or deployment operations are performed. Callers must
supply a PONS adapter-verified exact-scope CapabilityGrant.
"""
from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import stat
import uuid
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from tools.eria_pantheon.pons import CapabilityGrant, Decision, Pons
from tools.god_parent_validation import ParentValidationError, validate_parent_chain

CAPABILITY = "god.ingest"
SCHEMA = "eria.god.record/1"


class PreservationError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def _write_new(path: Path, data: bytes) -> None:
    """Create a new file only; never truncate or replace an existing path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    try:
        with os.fdopen(fd, "wb", closefd=False) as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        os.close(fd)


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _append_event(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    try:
        os.write(fd, _json_bytes(event))
        os.fsync(fd)
    finally:
        os.close(fd)


def ingest_file(
    source: str | Path,
    vault: str | Path,
    grant: CapabilityGrant,
    *,
    source_label: str | None = None,
    parent_record_id: str | None = None,
    parent_record_ids: list[str] | None = None,
    source_relative_path: str | None = None,
    source_root_label: str | None = None,
    actor: str = "eria",
) -> dict[str, Any]:
    """Preserve one regular file and create provenance/lineage references."""
    source_path = Path(source).expanduser()
    if source_relative_path is not None:
        rel_source = PurePosixPath(source_relative_path)
        if (not source_relative_path or "\\" in source_relative_path
                or rel_source.is_absolute()
                or any(part in {"", ".", ".."} for part in rel_source.parts)):
            raise PreservationError("source_relative_path must be a normalized safe POSIX path")
    if source_root_label is not None and (
        not isinstance(source_root_label, str) or not source_root_label.strip()
    ):
        raise PreservationError("source_root_label must be non-empty text")
    vault_path = Path(vault).expanduser().resolve()
    if source_path.is_symlink() or not source_path.is_file():
        raise PreservationError("Source must be a regular, non-symlink file")
    source_path = source_path.resolve(strict=True)
    if Pons.authorize(grant, CAPABILITY, str(vault_path)) is Decision.HOLD:
        raise PermissionError("PONS denied GOD ingestion; missing or mismatched grant")

    source_stat = source_path.stat()
    if not stat.S_ISREG(source_stat.st_mode):
        raise PreservationError("Only regular files can be ingested")

    digest, size = sha256_file(source_path)
    record_id = str(uuid.uuid4())
    object_path = vault_path / "ORIGINAL_DATA" / "objects" / digest[:2] / digest
    metadata_path = vault_path / "SOURCE_PROVENANCE" / "records" / f"{record_id}.json"
    collaboration_path = vault_path / "COLLABORATION" / "records" / record_id / "source-reference.json"
    ledger_path = vault_path / "LINEAGE" / "events.jsonl"

    if parent_record_id is not None and parent_record_ids is not None:
        raise PreservationError("Use parent_record_id or parent_record_ids, not both")
    requested_parent_ids = (
        list(parent_record_ids) if parent_record_ids is not None
        else ([parent_record_id] if parent_record_id is not None else [])
    )
    try:
        initial_parent_proofs = validate_parent_chain(
            vault_path, requested_parent_ids, child_record_type="original"
        )
    except ParentValidationError as exc:
        raise PreservationError(f"Parent validation failed: {exc}") from exc

    raw = source_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != digest or len(raw) != size:
        raise PreservationError("Source changed while being captured; retry ingestion")

    object_path.parent.mkdir(parents=True, exist_ok=True)
    if object_path.exists():
        existing_hash, existing_size = sha256_file(object_path)
        if existing_hash != digest or existing_size != size:
            raise PreservationError("Content-addressed object collision or corruption")
    else:
        _write_new(object_path, raw)

    # Revalidate immediately before writing provenance. If an ancestor changed
    # or became unavailable, do not accept the child record.
    try:
        current_parent_proofs = validate_parent_chain(
            vault_path, requested_parent_ids, child_record_type="original"
        )
    except ParentValidationError as exc:
        raise PreservationError(f"Commit-time parent validation failed: {exc}") from exc
    if current_parent_proofs != initial_parent_proofs:
        raise PreservationError("Parent lineage changed between initial and commit-time validation")

    captured_at = utc_now()
    metadata = {
        "schema": SCHEMA,
        "record_id": record_id,
        "record_type": "original",
        "sha256": digest,
        "size_bytes": size,
        "media_type": mimetypes.guess_type(source_path.name)[0] or "application/octet-stream",
        "source": {
            "label": source_label or source_path.name,
            "filename": source_path.name,
            "modified_time_ns": source_stat.st_mtime_ns,
            "mode": stat.S_IMODE(source_stat.st_mode),
            **({"relative_path": source_relative_path} if source_relative_path else {}),
            **({"root_label": source_root_label} if source_root_label else {}),
        },
        "captured_at": captured_at,
        "parent_record_ids": requested_parent_ids,
        "validated_parents": [
            {"record_id": item["record_id"], "sha256": item["sha256"],
             "size_bytes": item["size_bytes"]}
            for item in current_parent_proofs
        ],
        "authority": "preserved-source-not-validated-as-fact",
        "object_relative_path": str(object_path.relative_to(vault_path)),
    }
    _write_new(metadata_path, _json_bytes(metadata))

    reference = {
        "schema": "eria.god.collaboration-reference/1",
        "record_id": record_id,
        "record_type": "source-reference",
        "source_sha256": digest,
        "source_metadata": str(metadata_path.relative_to(vault_path)),
        "parent_record_ids": metadata["parent_record_ids"],
        "created_at": captured_at,
        "note": "Collaboration work must be saved as new descendants; never replace the GOD object or its metadata.",
    }
    _write_new(collaboration_path, _json_bytes(reference))

    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": "ORIGINAL_INGESTED",
        "record_id": record_id,
        "parent_record_ids": metadata["parent_record_ids"],
        "timestamp": captured_at,
        "actor": actor,
        "authorization_reference": grant.approval_reference,
        "input_sha256": digest,
        "output_sha256": digest,
        "object_relative_path": str(object_path.relative_to(vault_path)),
        "metadata_relative_path": str(metadata_path.relative_to(vault_path)),
        "collaboration_reference": str(collaboration_path.relative_to(vault_path)),
    }
    _append_event(ledger_path, event)
    return {
        "status": "preserved",
        "record_id": record_id,
        "sha256": digest,
        "size_bytes": size,
        "object_path": str(object_path),
        "metadata_path": str(metadata_path),
        "collaboration_reference": str(collaboration_path),
        "lineage_event_id": event["event_id"],
    }


def verify_record(vault: str | Path, record_id: str) -> dict[str, Any]:
    """Verify this record and its complete ancestry without trusting stored paths."""
    vault_path = Path(vault).expanduser().resolve()
    try:
        proof = validate_parent_chain(
            vault_path, [record_id], child_record_type="any"
        )[0]
    except ParentValidationError as exc:
        return {
            "record_id": record_id,
            "valid": False,
            "ancestry_valid": False,
            "error": str(exc),
        }
    return {
        "record_id": record_id,
        "valid": True,
        "ancestry_valid": True,
        "record_type": proof["record_type"],
        "parent_record_ids": proof["parent_record_ids"],
        "source_relative_path": proof["source_relative_path"],
        "source_filename": proof["source_filename"],
        "expected_sha256": proof["sha256"],
        "actual_sha256": proof["sha256"],
        "expected_size_bytes": proof["size_bytes"],
        "actual_size_bytes": proof["size_bytes"],
    }


def collect_directory(
    source_root: str | Path,
    vault: str | Path,
    grant: CapabilityGrant,
    *,
    recursive: bool = True,
    actor: str = "eria",
) -> list[dict[str, Any]]:
    """Ingest a snapshot of regular files from a user-selected directory.

    Symlinks are skipped. The vault itself is excluded if it is nested under
    the source directory. This is an explicit batch operation, not a watcher.
    """
    root = Path(source_root).expanduser()
    if root.is_symlink() or not root.is_dir():
        raise PreservationError("Source root must be a regular, non-symlink directory")
    root = root.resolve(strict=True)
    vault_path = Path(vault).expanduser().resolve()
    if Pons.authorize(grant, CAPABILITY, str(vault_path)) is Decision.HOLD:
        raise PermissionError("PONS denied GOD collection; missing or mismatched grant")

    candidates = root.rglob("*") if recursive else root.iterdir()
    files: list[Path] = []
    for candidate in sorted(candidates):
        if candidate.is_symlink() or not candidate.is_file():
            continue
        resolved = candidate.resolve(strict=True)
        try:
            resolved.relative_to(vault_path)
            continue
        except ValueError:
            pass
        files.append(resolved)

    results = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        results.append(ingest_file(
            path, vault_path, grant,
            source_relative_path=relative,
            source_root_label=root.name,
            actor=actor,
        ))
    return results
