#!/usr/bin/env python3
"""Append-only creation of typed GOD descendants.

Derived bytes are stored separately from originals. This module never edits an
ancestor record or object and requires a trusted PONS grant for god.derive.
"""
from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import stat
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.eria_pantheon.pons import CapabilityGrant, Decision, Pons
from tools.god_parent_validation import DERIVED_TYPES, ParentValidationError, validate_parent_chain

CAPABILITY = "god.derive"
SCHEMA = "eria.god.record/1"


class DerivationError(RuntimeError):
    """A derivative could not be safely created or linked."""


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _ensure_directory_chain(vault: Path, directory: Path) -> None:
    try:
        relative = directory.relative_to(vault)
    except ValueError as exc:
        raise DerivationError("GOD write path escapes the vault") from exc
    current = vault
    for part in relative.parts:
        current = current / part
        current.mkdir(mode=0o700, exist_ok=True)
        info = current.lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise DerivationError("symlink or non-directory in GOD write path")


def _write_new(path: Path, data: bytes) -> None:
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


def create_derived_record(
    content: bytes | str,
    vault: str | Path,
    grant: CapabilityGrant,
    *,
    record_type: str,
    parent_record_ids: list[str],
    operation: str,
    source_context: dict[str, str],
    method: str = "operator-supplied",
    actor: str = "eria",
) -> dict[str, Any]:
    """Create a translation, interpretation, or correction as a new GOD child.

    source_context must identify the source-relative path, filename, and SHA-256
    of one of the direct parents. No parent bytes or metadata are overwritten.
    """
    if record_type not in DERIVED_TYPES:
        raise DerivationError("record_type must be translation, interpretation, or correction")
    if not isinstance(operation, str) or not operation.strip():
        raise DerivationError("operation must be non-empty text")
    if not isinstance(method, str) or not method.strip():
        raise DerivationError("method must be non-empty text")
    if not isinstance(actor, str) or not actor.strip():
        raise DerivationError("actor must be non-empty text")
    if not isinstance(source_context, dict) or set(source_context) != {
        "relative_path", "filename", "source_sha256"
    }:
        raise DerivationError("source_context requires relative_path, filename, and source_sha256")
    if not all(isinstance(source_context.get(k), str) and source_context[k].strip()
               for k in ("relative_path", "filename", "source_sha256")):
        raise DerivationError("source_context values must be non-empty text")
    if len(source_context["source_sha256"]) != 64 or any(
        c not in "0123456789abcdef" for c in source_context["source_sha256"]
    ):
        raise DerivationError("source_context source_sha256 must be lowercase SHA-256")
    if isinstance(content, str):
        raw = content.encode("utf-8")
    elif isinstance(content, bytes):
        raw = content
    else:
        raise DerivationError("content must be bytes or UTF-8 text")

    vault_path = Path(vault).expanduser().resolve()
    if Pons.authorize(grant, CAPABILITY, str(vault_path)) is Decision.HOLD:
        raise PermissionError("PONS denied GOD derivation; missing or mismatched grant")

    try:
        initial_proofs = validate_parent_chain(
            vault_path, parent_record_ids, child_record_type=record_type
        )
    except ParentValidationError as exc:
        raise DerivationError(f"Parent validation failed: {exc}") from exc
    if not any(
        item["sha256"] == source_context["source_sha256"]
        and item["source_relative_path"] == source_context["relative_path"]
        and item["source_filename"] == source_context["filename"]
        for item in initial_proofs
    ):
        raise DerivationError("source_context must exactly match one direct parent's hash and relative identity")

    digest = hashlib.sha256(raw).hexdigest()
    record_id = str(uuid.uuid4())
    object_path = vault_path / "DERIVED_DATA" / "objects" / digest[:2] / digest
    metadata_path = vault_path / "SOURCE_PROVENANCE" / "records" / f"{record_id}.json"
    ledger_path = vault_path / "LINEAGE" / "events.jsonl"

    _ensure_directory_chain(vault_path, object_path.parent)
    if object_path.exists() or object_path.is_symlink():
        info = object_path.lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
            raise DerivationError("existing derived object must be a regular non-symlink file")
        existing = hashlib.sha256(object_path.read_bytes()).hexdigest()
        if existing != digest:
            raise DerivationError("derived content-address collision or corruption")
    else:
        _write_new(object_path, raw)

    # Revalidate immediately before writing the child provenance record.
    try:
        current_proofs = validate_parent_chain(
            vault_path, parent_record_ids, child_record_type=record_type
        )
    except ParentValidationError as exc:
        raise DerivationError(f"Commit-time parent validation failed: {exc}") from exc
    if current_proofs != initial_proofs:
        raise DerivationError("Parent lineage changed before child-record creation")
    if not any(
        item["sha256"] == source_context["source_sha256"]
        and item["source_relative_path"] == source_context["relative_path"]
        and item["source_filename"] == source_context["filename"]
        for item in current_proofs
    ):
        raise DerivationError("Source context no longer matches a direct parent")

    captured_at = datetime.now(timezone.utc).isoformat()
    relative_object = object_path.relative_to(vault_path).as_posix()
    metadata = {
        "schema": SCHEMA,
        "record_id": record_id,
        "record_type": record_type,
        "sha256": digest,
        "size_bytes": len(raw),
        "media_type": mimetypes.guess_type(source_context["filename"])[0] or "application/octet-stream",
        "source": {
            "label": operation,
            "filename": source_context["filename"],
            "modified_time_ns": 0,
            "mode": 0,
            "relative_path": source_context["relative_path"],
        },
        "captured_at": captured_at,
        "parent_record_ids": list(parent_record_ids),
        "validated_parents": [
            {"record_id": item["record_id"], "sha256": item["sha256"],
             "size_bytes": item["size_bytes"]}
            for item in current_proofs
        ],
        "authority": "derived-not-validated-as-fact",
        "object_relative_path": relative_object,
        "derivation": {
            "operation": operation,
            "method": method,
            "source_context": dict(source_context),
            "created_by": actor,
        },
    }
    _ensure_directory_chain(vault_path, metadata_path.parent)
    _write_new(metadata_path, _json_bytes(metadata))

    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": f"{record_type.upper()}_CREATED",
        "record_id": record_id,
        "record_type": record_type,
        "parent_record_ids": list(parent_record_ids),
        "timestamp": captured_at,
        "actor": actor,
        "authorization_reference": grant.approval_reference,
        "input_parent_proofs": current_proofs,
        "input_source_sha256": source_context["source_sha256"],
        "output_sha256": digest,
        "object_relative_path": relative_object,
        "metadata_relative_path": metadata_path.relative_to(vault_path).as_posix(),
    }
    _ensure_directory_chain(vault_path, ledger_path.parent)
    _append_event(ledger_path, event)
    return {
        "status": "derived",
        "record_id": record_id,
        "record_type": record_type,
        "sha256": digest,
        "size_bytes": len(raw),
        "parent_record_ids": list(parent_record_ids),
        "metadata_path": str(metadata_path),
        "object_path": str(object_path),
        "lineage_event_id": event["event_id"],
    }
