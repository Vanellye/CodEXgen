"""Versioned, provenance-aware data envelope for CodEXgen.

This module validates and serializes records without silently repairing inputs.
It does not authorize actions or claim cryptographic signer trust.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime
from typing import Any, Mapping

SCHEMA_VERSION = 1
QUALITY_STATES = {
    "VALID", "STALE", "OUT_OF_RANGE", "UNCALIBRATED",
    "SENSOR_FAULT", "UNKNOWN",
}
IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class EnvelopeError(ValueError):
    """An envelope is malformed or cannot be represented canonically."""


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _check_json_value(value: Any, path: str = "payload") -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise EnvelopeError(f"{path} contains a non-finite number")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _check_json_value(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise EnvelopeError(f"{path} object keys must be strings")
            _check_json_value(item, f"{path}.{key}")
        return
    raise EnvelopeError(f"{path} contains unsupported type {type(value).__name__}")


def _require_identifier(value: Any, field: str) -> None:
    if not isinstance(value, str) or not IDENTIFIER_RE.fullmatch(value):
        raise EnvelopeError(f"{field} must be a stable identifier")


def _require_timestamp(value: Any, field: str) -> None:
    if not isinstance(value, str):
        raise EnvelopeError(f"{field} must be an RFC 3339 timestamp string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EnvelopeError(f"{field} must be a valid RFC 3339 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise EnvelopeError(f"{field} must include a timezone offset")


def _validate_provenance(value: Any) -> None:
    if not isinstance(value, dict):
        raise EnvelopeError("provenance must be an object")
    allowed = {"source_ref", "source_commit", "source_digest", "signer", "signature_status"}
    unknown = set(value) - allowed
    if unknown:
        raise EnvelopeError("provenance contains unknown fields: " + ", ".join(sorted(unknown)))
    if "source_digest" in value and (
        not isinstance(value["source_digest"], str)
        or not SHA256_RE.fullmatch(value["source_digest"])
    ):
        raise EnvelopeError("provenance.source_digest must be a lowercase SHA-256 digest")
    if "signature_status" in value and value["signature_status"] not in {
        "not_present", "valid", "invalid", "unverified"
    }:
        raise EnvelopeError("provenance.signature_status is not recognized")


def _validate_transformations(value: Any) -> None:
    if not isinstance(value, list):
        raise EnvelopeError("transformations must be a list")
    for index, item in enumerate(value):
        prefix = f"transformations[{index}]"
        if not isinstance(item, dict):
            raise EnvelopeError(f"{prefix} must be an object")
        if set(item) - {"operation", "version", "parameters_digest", "output_digest"}:
            raise EnvelopeError(f"{prefix} contains unknown fields")
        for required in ("operation", "version"):
            _require_identifier(item.get(required), f"{prefix}.{required}")
        for digest_field in ("parameters_digest", "output_digest"):
            digest = item.get(digest_field)
            if digest is not None and (
                not isinstance(digest, str) or not SHA256_RE.fullmatch(digest)
            ):
                raise EnvelopeError(f"{prefix}.{digest_field} must be a lowercase SHA-256 digest")


def validate_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a record and return a detached plain-dict copy; never repair it."""
    if not isinstance(record, Mapping):
        raise EnvelopeError("record must be an object")
    required = {
        "record_id", "schema_version", "source", "observed_at", "payload",
        "units", "quality", "provenance", "transformations", "authorization",
        "validation", "retention",
    }
    optional = {"monotonic_time"}
    missing = required - set(record)
    unknown = set(record) - required - optional
    if missing:
        raise EnvelopeError("missing required fields: " + ", ".join(sorted(missing)))
    if unknown:
        raise EnvelopeError("unknown fields: " + ", ".join(sorted(unknown)))

    if record["schema_version"] != SCHEMA_VERSION or not _is_int(record["schema_version"]):
        raise EnvelopeError(f"schema_version must equal {SCHEMA_VERSION}")
    _require_identifier(record["record_id"], "record_id")
    _require_identifier(record["source"], "source")
    _require_timestamp(record["observed_at"], "observed_at")

    if "monotonic_time" in record:
        monotonic = record["monotonic_time"]
        if not isinstance(monotonic, dict) or set(monotonic) != {"value", "clock_domain"}:
            raise EnvelopeError("monotonic_time must contain value and clock_domain")
        if not _is_int(monotonic["value"]) or monotonic["value"] < 0:
            raise EnvelopeError("monotonic_time.value must be a non-negative integer")
        _require_identifier(monotonic["clock_domain"], "monotonic_time.clock_domain")

    _check_json_value(record["payload"])
    if not isinstance(record["units"], dict):
        raise EnvelopeError("units must be an object")
    _check_json_value(record["units"], "units")
    if not isinstance(record["quality"], str) or record["quality"] not in QUALITY_STATES:
        raise EnvelopeError("quality is not a recognized quality state")
    _validate_provenance(record["provenance"])
    _validate_transformations(record["transformations"])

    authorization = record["authorization"]
    if not isinstance(authorization, dict) or set(authorization) != {"status", "scope", "approval_ref"}:
        raise EnvelopeError("authorization must contain status, scope, and approval_ref")
    if not isinstance(authorization["status"], str) or authorization["status"] not in {"not_authorized", "authorized", "declined"}:
        raise EnvelopeError("authorization.status is not recognized")
    if authorization["status"] == "authorized":
        if not isinstance(authorization["scope"], list) or not authorization["scope"]:
            raise EnvelopeError("authorized records require a non-empty scope")
        for item in authorization["scope"]:
            _require_identifier(item, "authorization.scope item")
        _require_identifier(authorization["approval_ref"], "authorization.approval_ref")
    elif authorization["approval_ref"] is not None:
        raise EnvelopeError("non-authorized records must not contain an approval_ref")

    if not isinstance(record["validation"], dict):
        raise EnvelopeError("validation must be an object")
    _check_json_value(record["validation"], "validation")
    if not isinstance(record["retention"], dict):
        raise EnvelopeError("retention must be an object")
    _check_json_value(record["retention"], "retention")

    detached = dict(record)
    detached["payload"] = json.loads(json.dumps(record["payload"], allow_nan=False))
    detached["units"] = json.loads(json.dumps(record["units"], allow_nan=False))
    return detached


def canonical_json_bytes(record: Mapping[str, Any]) -> bytes:
    """Return deterministic UTF-8 JSON bytes after strict validation."""
    validated = validate_record(record)
    try:
        text = json.dumps(
            validated, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise EnvelopeError(str(exc)) from exc
    return (text + "\n").encode("utf-8")


def record_digest(record: Mapping[str, Any]) -> str:
    """Return the SHA-256 digest of the canonical record bytes."""
    return hashlib.sha256(canonical_json_bytes(record)).hexdigest()
