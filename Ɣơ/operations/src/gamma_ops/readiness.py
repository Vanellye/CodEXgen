"""Fail-closed readiness checks. This module never launches or executes an operable."""
from __future__ import annotations
import hashlib
from pathlib import Path
from typing import Any
from .reviewer import verify_readiness_approval

REQUIRED_CHECKS = ("python_tests", "arm64_compile", "inventory", "coddoc_validation")

def readiness_result(record: dict[str, Any], *, repository_root: str | Path = ".",
                     now_epoch: int | None = None) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if record.get("readiness_state") != "READY_TO_OPEN":
        reasons.append("readiness_state is not READY_TO_OPEN")
    if record.get("execution_tier") == "LIVE_FINANCIAL":
        reasons.append("live financial execution is categorically excluded from this readiness gate")
    if record.get("live_execution_enabled") is not False:
        reasons.append("live_execution_enabled must be explicitly false")
    checks = record.get("checks")
    if not isinstance(checks, dict):
        reasons.append("required validation checks are missing")
    else:
        for name in REQUIRED_CHECKS:
            if checks.get(name) != "PASS":
                reasons.append(f"check {name} is not PASS")
    review = record.get("review")
    if not isinstance(review, dict) or review.get("state") != "APPROVED":
        reasons.append("independent human review is not APPROVED")
    elif not isinstance(review.get("review_ref"), str) or not review["review_ref"].strip():
        reasons.append("review evidence reference is missing")
    source_ref = record.get("source_ref")
    if not isinstance(source_ref, str) or not source_ref.strip():
        reasons.append("source provenance reference is missing")
    artifact_path = record.get("artifact_path")
    artifact_digest = None
    root = Path(repository_root).resolve()
    if not isinstance(artifact_path, str) or not artifact_path.strip():
        reasons.append("reviewable artifact path is missing")
    else:
        raw = root / artifact_path
        try:
            cursor = raw
            while cursor != root and cursor != cursor.parent:
                if cursor.is_symlink():
                    raise ValueError("artifact path contains a symlink")
                cursor = cursor.parent
            candidate = raw.resolve(strict=True)
            candidate.relative_to(root)
            if not candidate.is_file():
                raise ValueError("artifact path is not a regular file")
            artifact_digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
        except (OSError, ValueError):
            reasons.append("reviewable artifact is missing, symlinked, or outside repository root")
    if isinstance(review, dict) and review.get("state") == "APPROVED" and artifact_digest:
        verified, reason = verify_readiness_approval(
            review, repository_root=root, expected_artifact_sha256=artifact_digest, now_epoch=now_epoch
        )
        if not verified:
            reasons.append(reason)
    elif isinstance(review, dict) and review.get("state") == "APPROVED":
        reasons.append("signed approval cannot be checked because artifact integrity is unavailable")
    return not reasons, reasons

def ready_records(registry: dict[str, Any], *, repository_root: str | Path = ".") -> list[dict[str, Any]]:
    records = registry.get("operables", [])
    if not isinstance(records, list):
        return []
    result = []
    for record in records:
        if isinstance(record, dict):
            ready, _ = readiness_result(record, repository_root=repository_root)
            if ready:
                result.append(record)
    return result
