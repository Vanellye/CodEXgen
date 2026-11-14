"""PONS: read-only component status and provenance registry.

The canonical anchor is an immutable identity. Component claims are observations,
not proof of accuracy or signer trust. Expected digests must come from a separately
reviewed manifest; this module does not authenticate that manifest.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from threading import RLock
from typing import Dict, Optional

CANONICAL_ANCHOR_ID = "7f7a43a973a96a06dd432bf94843213d09133323"
ANCHOR_BRANCH = "zero-dissipation-anchor"
ANCHOR_REF_SHA = "df5ead3b55cfabd0ba40e902b4080946cba794dc"
_ALLOWED_STATES = {"READY", "DEGRADED", "HOLD", "UNKNOWN"}


@dataclass(frozen=True)
class AnchorIdentity:
    """Immutable anchor identity; intentionally exposes no mutation operation."""
    anchor_id: str = CANONICAL_ANCHOR_ID
    branch: str = ANCHOR_BRANCH
    ref_sha: str = ANCHOR_REF_SHA


@dataclass(frozen=True)
class Component:
    component_id: str
    source_ref: str
    source_path: str
    expected_sha256: Optional[str] = None
    manifest_id: Optional[str] = None


class PONSRegistry:
    """Central status registry with a hash-chained, append-only-by-API event ledger."""

    def __init__(self, ledger_path: Optional[str] = None,
                 anchor: AnchorIdentity = AnchorIdentity()):
        if anchor.anchor_id != CANONICAL_ANCHOR_ID:
            raise ValueError("Canonical anchor identity mismatch; refusing startup.")
        if anchor.branch != ANCHOR_BRANCH or anchor.ref_sha != ANCHOR_REF_SHA:
            raise ValueError("Canonical anchor reference mismatch; refusing startup.")
        self.anchor = anchor
        self.ledger_path = Path(ledger_path) if ledger_path else None
        self._components: Dict[str, Component] = {}
        self._observations: Dict[str, dict] = {}
        self._provenance: Dict[str, dict] = {}
        self._provenance: Dict[str, dict] = {}
        self._lock = RLock()
        self._last_event_hash = "0" * 64
        if self.ledger_path and self.ledger_path.exists():
            self.verify_ledger()

    @staticmethod
    def sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def register(self, component: Component) -> None:
        if not component.component_id or not component.source_ref or not component.source_path:
            raise ValueError("component_id, source_ref and source_path are required")
        if component.expected_sha256 and len(component.expected_sha256) != 64:
            raise ValueError("expected_sha256 must be a 64-character SHA-256 hex digest")
        with self._lock:
            old = self._components.get(component.component_id)
            if old and old != component:
                raise ValueError("component registration is immutable; use a new versioned id")
            self._components[component.component_id] = component
            self._append("component_registered", {
                "component_id": component.component_id,
                "source_ref": component.source_ref,
                "source_path": component.source_path,
                "expected_sha256": component.expected_sha256,
                "manifest_id": component.manifest_id,
            })

    def observe_status(self, component_id: str, state: str, detail: str = "") -> dict:
        state = state.upper()
        if state not in _ALLOWED_STATES:
            raise ValueError("state must be READY, DEGRADED, HOLD or UNKNOWN; accuracy is not self-declarable")
        with self._lock:
            if component_id not in self._components:
                raise KeyError("component is not registered with PONS")
            obs = {"state": state, "detail": str(detail)[:500],
                   "observed_at": datetime.now(timezone.utc).isoformat()}
            self._observations[component_id] = obs
            self._append("status_observed", {"component_id": component_id, **obs})
            return self.component_status(component_id)

    def verify_provenance(self, component_id: str, source_bytes: Optional[bytes]) -> dict:
        with self._lock:
            component = self._components[component_id]
            if source_bytes is None or component.expected_sha256 is None:
                result = {"state": "UNKNOWN", "actual_sha256": None,
                          "expected_sha256": component.expected_sha256,
                          "reason": "source bytes or independently pinned expected digest unavailable"}
            else:
                actual = self.sha256(source_bytes)
                match = actual == component.expected_sha256.lower()
                result = {"state": "VERIFIED" if match else "HOLD",
                          "actual_sha256": actual,
                          "expected_sha256": component.expected_sha256.lower(),
                          "reason": "digest match" if match else "digest mismatch"}
            self._provenance[component_id] = result
            self._append("provenance_checked", {"component_id": component_id, **result})
            return result

    def component_status(self, component_id: str) -> dict:
        component = self._components[component_id]
        obs = self._observations.get(component_id, {"state": "UNKNOWN", "detail": "no status observation"})
        return {
            "component_id": component_id,
            "reported_state": obs["state"],
            "detail": obs.get("detail", ""),
            "provenance_state": self._provenance.get(component_id, {"state": "NOT_CHECKED"})["state"],
            "actual_sha256": self._provenance.get(component_id, {}).get("actual_sha256"),
            "source_ref": component.source_ref,
            "source_path": component.source_path,
            "expected_sha256": component.expected_sha256,
            "anchor_id": self.anchor.anchor_id,
            "anchor_ref_sha": self.anchor.ref_sha,
        }

    def report(self) -> dict:
        with self._lock:
            return {
                "authority": "PONS",
                "anchor": asdict(self.anchor),
                "registered_components": sorted(self._components),
                "components": [self.component_status(k) for k in sorted(self._components)],
                "ledger_head": self._last_event_hash,
                "claims": "component status is reported; provenance is independently recomputed; accuracy is not self-declarable",
            }

    def _append(self, event_type: str, payload: dict) -> None:
        event = {
            "sequence": self._next_sequence(),
            "previous_hash": self._last_event_hash,
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "anchor_id": self.anchor.anchor_id,
            "payload": payload,
        }
        canonical = json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        digest = self.sha256(canonical.encode("utf-8"))
        record = {"event": event, "event_hash": digest}
        if self.ledger_path:
            self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
            with self.ledger_path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "
")
                stream.flush()
                os.fsync(stream.fileno())
        self._last_event_hash = digest
        self._sequence = event["sequence"]

    def _next_sequence(self) -> int:
        if not self.ledger_path or not self.ledger_path.exists():
            return getattr(self, "_sequence", 0) + 1
        return getattr(self, "_sequence", 0) + 1

    def verify_ledger(self) -> dict:
        previous = "0" * 64
        sequence = 0
        if self.ledger_path and self.ledger_path.exists():
            for line_number, line in enumerate(self.ledger_path.read_text(encoding="utf-8").splitlines(), 1):
                record = json.loads(line)
                event = record["event"]
                if event["sequence"] != sequence + 1 or event["previous_hash"] != previous:
                    raise ValueError(f"ledger chain discontinuity at line {line_number}")
                canonical = json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                digest = self.sha256(canonical.encode("utf-8"))
                if digest != record["event_hash"]:
                    raise ValueError(f"ledger hash mismatch at line {line_number}")
                if event["anchor_id"] != self.anchor.anchor_id:
                    raise ValueError(f"anchor identity mismatch at line {line_number}")
                sequence += 1
                previous = digest
        self._sequence = sequence
        self._last_event_hash = previous
        return {"valid": True, "events": sequence, "head": previous,
                "note": "hash-chain integrity only; not an external signature or tamper-proof storage"}
