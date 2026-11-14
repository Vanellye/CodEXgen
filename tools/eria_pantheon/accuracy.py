#!/usr/bin/env python3
"""Independent, evidence-backed AVS service for ERIA. Standard-library only."""
from __future__ import annotations

import hashlib
import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


_PONS_AUTHORITY = object()


class LedgerIntegrityError(RuntimeError):
    pass


class EvidenceRejected(ValueError):
    pass


def _canonical(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class EvidenceLedger:
    """Append-only hash-chained JSONL ledger; tampering is detected on open/read."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.verify()

    def _records(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        records = []
        with self.path.open("r", encoding="utf-8") as stream:
            for number, line in enumerate(stream, 1):
                try:
                    item = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise LedgerIntegrityError(f"Invalid ledger JSON at line {number}") from exc
                if not isinstance(item, dict):
                    raise LedgerIntegrityError(f"Invalid ledger record at line {number}")
                records.append(item)
        return records

    def verify(self) -> dict[str, Any]:
        with self._lock:
            previous = "GENESIS"
            records = self._records()
            for number, record in enumerate(records, 1):
                digest = record.get("record_sha256")
                body = {k: v for k, v in record.items() if k != "record_sha256"}
                if record.get("previous_sha256") != previous:
                    raise LedgerIntegrityError(f"Broken ledger link at line {number}")
                expected = hashlib.sha256(_canonical(body)).hexdigest()
                if digest != expected:
                    raise LedgerIntegrityError(f"Ledger hash mismatch at line {number}")
                previous = digest
            return {"valid": True, "records": len(records), "head_sha256": previous}

    def append(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            state = self.verify()
            body = dict(payload)
            body["previous_sha256"] = state["head_sha256"]
            record = dict(body)
            record["record_sha256"] = hashlib.sha256(_canonical(body)).hexdigest()
            encoded = _canonical(record) + b"\n"
            fd = os.open(str(self.path), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
            try:
                with os.fdopen(fd, "ab", closefd=False) as stream:
                    stream.write(encoded)
                    stream.flush()
                    os.fsync(stream.fileno())
            finally:
                os.close(fd)
            return record

    def records(self) -> list[dict[str, Any]]:
        with self._lock:
            self.verify()
            return self._records()


class AccuracyValidationService:
    """PONS-owned authority for AVS evidence intake and score issuance.

    Evidence is an attestation by a verifier external to the component being
    assessed. The score measures evidence-attested outcomes, not metaphysical
    truth; verifier quality and source quality remain explicit dependencies.
    """

    def __init__(self, ledger_path: str | Path, *, authority: object = None):
        if authority is not _PONS_AUTHORITY:
            raise PermissionError("AVS may only be constructed by PONS.")
        self.ledger = EvidenceLedger(ledger_path)
        self._lock = threading.RLock()

    def submit_evidence(
        self, *, claim_id: str, subject_component: str, verifier_id: str,
        evidence_ref: str, outcome: bool, weight: float = 1.0,
        method: str = "independent_review", _authority: object = None,
    ) -> dict[str, Any]:
        if _authority is not _PONS_AUTHORITY:
            raise PermissionError("Evidence intake is restricted to the PONS facade.")
        fields = (claim_id, subject_component, verifier_id, evidence_ref, method)
        if not all(isinstance(x, str) and x.strip() for x in fields):
            raise EvidenceRejected("All evidence identity and reference fields are required.")
        if verifier_id.strip() == subject_component.strip():
            raise EvidenceRejected("Self-certification is prohibited.")
        if type(outcome) is not bool:
            raise EvidenceRejected("outcome must be a boolean attestation.")
        if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not 0 < float(weight) <= 100:
            raise EvidenceRejected("weight must be greater than 0 and at most 100.")
        record = {
            "record_type": "avs_evidence",
            "evidence_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "claim_id": claim_id.strip(),
            "subject_component": subject_component.strip(),
            "verifier_id": verifier_id.strip(),
            "evidence_ref": evidence_ref.strip(),
            "outcome": outcome,
            "weight": float(weight),
            "method": method.strip(),
        }
        with self._lock:
            existing = self.ledger.records()
            if any(x.get("record_type") == "avs_evidence" and x.get("claim_id") == record["claim_id"]
                   and x.get("verifier_id") == record["verifier_id"] for x in existing):
                raise EvidenceRejected("This verifier has already submitted evidence for this claim.")
            return self.ledger.append(record)

    def evaluate(self, required_claims: Iterable[str], *, _authority: object = None) -> dict[str, Any]:
        if _authority is not _PONS_AUTHORITY:
            raise PermissionError("AVS score issuance is restricted to the PONS facade.")
        claims = list(dict.fromkeys(str(x).strip() for x in required_claims if str(x).strip()))
        if not claims:
            return {"status": "NOT_EVALUATED", "accuracy_score": None,
                    "verified_claims": 0, "required_claims": 0, "unverified_claims": []}
        records = [x for x in self.ledger.records() if x.get("record_type") == "avs_evidence"]
        by_claim: dict[str, list[dict[str, Any]]] = {}
        for item in records:
            by_claim.setdefault(item["claim_id"], []).append(item)
        verified = [claim for claim in claims if by_claim.get(claim)]
        missing = [claim for claim in claims if not by_claim.get(claim)]
        weighted_total = 0.0
        weighted_correct = 0.0
        for claim in verified:
            # Multiple independent reviewers contribute weighted evidence.
            for item in by_claim[claim]:
                weighted_total += float(item["weight"])
                if item["outcome"] is True:
                    weighted_correct += float(item["weight"])
        score = round(100.0 * weighted_correct / weighted_total, 2) if weighted_total else None
        return {
            "status": "INCOMPLETE" if missing else "EVIDENCE_VALIDATED",
            "accuracy_score": score,
            "score_scope": "verified_claims_only",
            "verified_claims": len(verified),
            "required_claims": len(claims),
            "unverified_claims": missing,
            "evidence_records": sum(len(by_claim.get(c, [])) for c in verified),
            "ledger": self.ledger.verify(),
            "issued_by": "PONS/AccuracyValidationService",
            "self_certification_allowed": False,
            "verifier_identity": "UNAUTHENTICATED_LABEL",
        }
