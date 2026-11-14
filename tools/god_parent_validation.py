#!/usr/bin/env python3
"""Fail-closed validation of GOD parent records and their complete ancestry.

Standard-library only. This module reads provenance and content-addressed
objects; it never repairs, rewrites, or deletes them.
"""
from __future__ import annotations

import hashlib
import json
import stat
import uuid
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

SCHEMA = "eria.god.record/1"
MAX_ANCESTRY_DEPTH = 256
MAX_ANCESTRY_RECORDS = 10_000

# Explicit policy. The initial collector emits original source records;
# other child types are reserved for later derivative-record APIs.
ALLOWED_PARENT_TYPES: dict[str, set[str]] = {
    "original": {"original"},
    "translation": {"original", "translation", "interpretation", "correction"},
    "interpretation": {"original", "translation", "interpretation", "correction",
                       "frequency_observation", "collaboration_contribution"},
    "correction": {"original", "translation", "interpretation", "correction"},
    "frequency_observation": {"original", "frequency_observation"},
    "collaboration_contribution": {"original", "translation", "interpretation",
                                   "correction", "frequency_observation",
                                   "collaboration_contribution"},
}


class ParentValidationError(ValueError):
    """A proposed lineage cannot be proven intact and unambiguous."""


def _canonical_uuid(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise ParentValidationError(f"{field} must be a UUID string")
    try:
        parsed = str(uuid.UUID(value))
    except (ValueError, AttributeError, TypeError) as exc:
        raise ParentValidationError(f"{field} is not a valid UUID") from exc
    if value != parsed:
        raise ParentValidationError(f"{field} must use canonical lowercase UUID form")
    return parsed


def _json_object(path: Path, description: str) -> dict[str, Any]:
    try:
        st = path.lstat()
    except OSError as exc:
        raise ParentValidationError(f"{description} is unavailable") from exc
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode):
        raise ParentValidationError(f"{description} must be a regular non-symlink file")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ParentValidationError(f"{description} is not readable valid JSON") from exc
    if not isinstance(value, dict):
        raise ParentValidationError(f"{description} must contain a JSON object")
    return value


def _safe_relative_object(vault: Path, value: Any, expected_digest: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ParentValidationError("object_relative_path must be a safe POSIX relative path")
    rel = PurePosixPath(value)
    if rel.is_absolute() or any(part in {"", ".", ".."} for part in rel.parts):
        raise ParentValidationError("object_relative_path contains traversal or absolute path")
    expected = PurePosixPath("ORIGINAL_DATA/objects") / expected_digest[:2] / expected_digest
    if rel != expected:
        raise ParentValidationError("object_relative_path does not match the content-addressed digest")

    current = vault
    for part in rel.parts:
        current = current / part
        try:
            st = current.lstat()
        except OSError as exc:
            raise ParentValidationError("parent object is missing or inaccessible") from exc
        if stat.S_ISLNK(st.st_mode):
            raise ParentValidationError("symlink in parent object path is not permitted")
    if not stat.S_ISREG(current.stat().st_mode):
        raise ParentValidationError("parent object is not a regular file")
    resolved = current.resolve(strict=True)
    try:
        resolved.relative_to(vault)
    except ValueError as exc:
        raise ParentValidationError("parent object escapes the GOD vault") from exc
    return resolved


def _hash_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
                size += len(chunk)
    except OSError as exc:
        raise ParentValidationError("parent object cannot be read for integrity verification") from exc
    return digest.hexdigest(), size


def _validate_record_shape(record: dict[str, Any], requested_id: str) -> None:
    allowed = {
        "schema", "record_id", "record_type", "sha256", "size_bytes", "media_type",
        "source", "captured_at", "parent_record_ids", "authority", "object_relative_path",
        "validated_parents",
    }
    if set(record) - allowed:
        raise ParentValidationError("parent record contains fields outside the approved schema")
    required = {
        "schema", "record_id", "record_type", "sha256", "size_bytes", "media_type",
        "source", "captured_at", "parent_record_ids", "authority", "object_relative_path",
    }
    missing = required - set(record)
    if missing:
        raise ParentValidationError(
            "parent record is missing required fields: " + ", ".join(sorted(missing))
        )
    if record.get("schema") != SCHEMA:
        raise ParentValidationError("parent record schema is unsupported")
    embedded_id = _canonical_uuid(record.get("record_id"), "embedded record_id")
    if embedded_id != requested_id:
        raise ParentValidationError("parent record identity mismatch")
    if record.get("record_type") != "original":
        raise ParentValidationError(
            "parent record type is not yet supported by the GOD source-record schema"
        )
    digest = record.get("sha256")
    if not isinstance(digest, str) or len(digest) != 64 or any(
        char not in "0123456789abcdef" for char in digest
    ):
        raise ParentValidationError("parent sha256 must be 64 lowercase hexadecimal characters")
    size = record.get("size_bytes")
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise ParentValidationError("parent size_bytes must be a non-negative integer")
    media = record.get("media_type")
    if not isinstance(media, str) or not media.strip():
        raise ParentValidationError("parent media_type must be non-empty text")
    source = record.get("source")
    if not isinstance(source, dict) or set(source) != {
        "label", "filename", "modified_time_ns", "mode"
    }:
        raise ParentValidationError("parent source metadata does not match the source-record schema")
    if not all(isinstance(source.get(key), str) and source[key]
               for key in ("label", "filename")):
        raise ParentValidationError("parent source label and filename must be non-empty text")
    for key in ("modified_time_ns", "mode"):
        if isinstance(source.get(key), bool) or not isinstance(source.get(key), int):
            raise ParentValidationError(f"parent source {key} must be an integer")
    if record.get("authority") != "preserved-source-not-validated-as-fact":
        raise ParentValidationError("parent authority marker is invalid")
    captured_at = record.get("captured_at")
    if not isinstance(captured_at, str):
        raise ParentValidationError("parent captured_at must be an ISO-8601 timestamp")
    try:
        datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ParentValidationError("parent captured_at is not a valid ISO-8601 timestamp") from exc
    parent_ids = record.get("parent_record_ids")
    if not isinstance(parent_ids, list):
        raise ParentValidationError("parent_record_ids must be an array")
    normalized = [_canonical_uuid(item, "parent_record_id") for item in parent_ids]
    if len(normalized) != len(set(normalized)):
        raise ParentValidationError("duplicate parent IDs are not permitted")
    if requested_id in normalized:
        raise ParentValidationError("a record cannot be its own parent")
    if not parent_ids and record.get("record_type") != "original":
        raise ParentValidationError("only a verified original may be an ancestry root")
    if "validated_parents" in record and not isinstance(record["validated_parents"], list):
        raise ParentValidationError("validated_parents must be an array")


def validate_parent_chain(
    vault: str | Path,
    parent_record_ids: Iterable[str],
    *,
    child_record_type: str = "original",
) -> list[dict[str, Any]]:
    """Validate direct parents and every ancestor; return direct-parent proofs.

    The proof list preserves caller-supplied parent order. Missing, malformed,
    ambiguous, cyclic, inaccessible, or hash-mismatched records fail closed.
    """
    vault_path = Path(vault).expanduser().resolve(strict=True)
    if not vault_path.is_dir():
        raise ParentValidationError("GOD vault must be an existing directory")
    if child_record_type not in ALLOWED_PARENT_TYPES:
        raise ParentValidationError("unknown child record type")
    if isinstance(parent_record_ids, (str, bytes)):
        raise ParentValidationError("parent_record_ids must be a collection of UUIDs, not text")
    try:
        ids = [_canonical_uuid(item, "parent_record_id") for item in parent_record_ids]
    except TypeError as exc:
        raise ParentValidationError("parent_record_ids must be iterable") from exc
    if len(ids) != len(set(ids)):
        raise ParentValidationError("duplicate parent IDs are not permitted")
    if not ids:
        if child_record_type != "original":
            raise ParentValidationError("a derived record must have at least one validated parent")
        return []

    visiting: set[str] = set()
    visited: dict[str, dict[str, Any]] = {}

    def visit(record_id: str, expected_child_type: str, depth: int) -> dict[str, Any]:
        if depth > MAX_ANCESTRY_DEPTH:
            raise ParentValidationError("ancestry exceeds the maximum validation depth")
        if record_id in visiting:
            raise ParentValidationError("ancestry cycle detected")
        if record_id in visited:
            proof = visited[record_id]
            if proof["record_type"] not in ALLOWED_PARENT_TYPES[expected_child_type]:
                raise ParentValidationError("parent/child record-type relationship is not permitted")
            return proof
        if len(visited) + len(visiting) >= MAX_ANCESTRY_RECORDS:
            raise ParentValidationError("ancestry exceeds the maximum validation record count")
        if "/" in record_id or "\\" in record_id:
            raise ParentValidationError("parent ID cannot contain a path separator")

        record_path = vault_path / "SOURCE_PROVENANCE" / "records" / f"{record_id}.json"
        for component in (
            vault_path / "SOURCE_PROVENANCE",
            vault_path / "SOURCE_PROVENANCE" / "records",
            record_path,
        ):
            try:
                if stat.S_ISLNK(component.lstat().st_mode):
                    raise ParentValidationError(
                        "symlink in parent provenance path is not permitted"
                    )
            except OSError as exc:
                raise ParentValidationError(
                    "parent provenance record is missing or inaccessible"
                ) from exc
        record = _json_object(record_path, "parent provenance record")
        _validate_record_shape(record, record_id)
        if record["record_type"] not in ALLOWED_PARENT_TYPES[expected_child_type]:
            raise ParentValidationError("parent/child record-type relationship is not permitted")

        object_path = _safe_relative_object(vault_path, record["object_relative_path"], record["sha256"])
        actual_digest, actual_size = _hash_file(object_path)
        if actual_digest != record["sha256"] or actual_size != record["size_bytes"]:
            raise ParentValidationError(
                "parent object hash or byte length does not match its provenance"
            )

        visiting.add(record_id)
        try:
            ancestor_proofs = [
                visit(parent_id, record["record_type"], depth + 1)
                for parent_id in record["parent_record_ids"]
            ]
            stored_manifest = record.get("validated_parents")
            if stored_manifest is not None:
                expected_manifest = [
                    {"record_id": item["record_id"], "sha256": item["sha256"],
                     "size_bytes": item["size_bytes"]}
                    for item in ancestor_proofs
                ]
                if stored_manifest != expected_manifest:
                    raise ParentValidationError(
                        "stored validated-parent manifest does not match live ancestors"
                    )
        finally:
            visiting.remove(record_id)

        proof = {
            "record_id": record_id,
            "record_type": record["record_type"],
            "sha256": record["sha256"],
            "size_bytes": record["size_bytes"],
        }
        visited[record_id] = proof
        return proof

    return [visit(record_id, child_record_type, 0) for record_id in ids]
