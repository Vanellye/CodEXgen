"""Fail-closed readiness checks. This module never launches or executes an operable."""
from __future__ import annotations
from pathlib import Path
from typing import Any

REQUIRED_CHECKS = ("python_tests", "arm64_compile", "inventory", "coddoc_validation")

def readiness_result(record: dict[str, Any], *, repository_root: str | Path = ".") -> tuple[bool, list[str]]:
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
    else:
        if review.get("reviewer_identity_verified") is not True:
            reasons.append("independent reviewer identity is not verified")
        if not isinstance(review.get("review_ref"), str) or not review["review_ref"].strip():
            reasons.append("review evidence reference is missing")
    source_ref = record.get("source_ref")
    if not isinstance(source_ref, str) or not source_ref.strip():
        reasons.append("source provenance reference is missing")
    artifact_path = record.get("artifact_path")
    if not isinstance(artifact_path, str) or not artifact_path.strip():
        reasons.append("reviewable artifact path is missing")
    else:
        root = Path(repository_root).resolve()
        candidate = (root / artifact_path).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            reasons.append("artifact path escapes the repository root")
        else:
            if not candidate.is_file():
                reasons.append("reviewable artifact does not exist as a file")
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
