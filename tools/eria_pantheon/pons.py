#!/usr/bin/env python3
"""PONS: small, fail-closed ERIA/PANTHEON service and provenance bridge.

Application-level contract boundary only; not an OS sandbox, identity provider,
cryptographic verifier, or Pantheon compiler/runtime.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import threading
from pathlib import Path
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, Optional, Type


CANONICAL_ANCHOR_SHA = "b549dea5af2e51402cf41234f3e2b3cdfb064032"
COMPONENT_PATHS = (
    "app/src/main/java/com/vanellye/eria/RepositoryDashboardScreen.kt",
    "app/src/main/java/com/vanellye/eria/MainActivity.kt",
    "tools/eria_repository_conversation.py",
    "tools/eria_conversation_server.py",
    "tools/eria_repository.html",
    "tools/eria_pantheon/pons.py",
    "tools/eria_pantheon/interface.py",
    "tools/eria_ttt_bypass.py",
)


class CapabilityDenied(PermissionError):
    """Raised when a capability is absent or its exact scope is not approved."""


class Decision(str, Enum):
    HOLD = "HOLD"
    PROPOSAL_ONLY = "PROPOSAL_ONLY"
    REVIEW_READY = "REVIEW_READY"


class Lifetime(str, Enum):
    SINGLETON = "singleton"
    TRANSIENT = "transient"


@dataclass(frozen=True)
class BridgeEnvelope:
    """Source and derived records; neither is authoritative by default."""
    source_id: str
    source_name: str
    source_sha256: str
    source_authority: str = "NON_AUTHORITATIVE"
    derived_sha256: Optional[str] = None
    derived_authority: str = "NON_AUTHORITATIVE"
    transformations: tuple[str, ...] = ()
    provenance: Dict[str, Any] = field(default_factory=dict)
    schema_version: str = "eria.pantheon.envelope/1.0"

    @classmethod
    def from_bytes(cls, source: bytes, source_name: str, **provenance: Any) -> "BridgeEnvelope":
        return cls(
            source_id=str(uuid.uuid4()),
            source_name=source_name,
            source_sha256=hashlib.sha256(source).hexdigest(),
            provenance=dict(provenance),
        )

    def with_derived(self, derived: bytes, operation: str) -> "BridgeEnvelope":
        """Return a derived record without replacing or promoting its source."""
        return BridgeEnvelope(
            source_id=self.source_id,
            source_name=self.source_name,
            source_sha256=self.source_sha256,
            source_authority="NON_AUTHORITATIVE",
            derived_sha256=hashlib.sha256(derived).hexdigest(),
            derived_authority="NON_AUTHORITATIVE",
            transformations=self.transformations + (operation,),
            provenance=dict(self.provenance),
            schema_version=self.schema_version,
        )

    def to_record(self) -> Dict[str, Any]:
        record = asdict(self)
        record["transformations"] = list(self.transformations)
        return record


@dataclass(frozen=True)
class CapabilityGrant:
    capability: str
    requested_scope: str
    approved_scope: str
    approval_reference: str
    verified_by_adapter: bool = False

    def permits(self, capability: str, scope: str) -> bool:
        # verified_by_adapter is an upstream assertion, not cryptographic proof.
        return (
            self.capability == capability
            and bool(self.approval_reference.strip())
            and self.verified_by_adapter
            and self.requested_scope == scope
            and self.approved_scope == scope
        )


class Pons:
    """Dependency registry and exact-scope capability gate.

    Resolution itself has no implicit network, filesystem, process, Git, or
    hardware behavior. Factories are caller-supplied and remain explicit.
    """
    def __init__(self) -> None:
        self._factories: Dict[Type[Any], tuple[Callable[[], Any], Lifetime]] = {}
        self._singletons: Dict[Type[Any], Any] = {}
        self._lock = threading.RLock()

    def register(self, key: Type[Any], factory: Callable[[], Any], *,
                 lifetime: Lifetime = Lifetime.TRANSIENT) -> None:
        if not isinstance(key, type) or not callable(factory):
            raise TypeError("key must be a type and factory must be callable")
        with self._lock:
            if key in self._factories:
                raise ValueError(f"Service already registered: {key.__name__}")
            self._factories[key] = (factory, Lifetime(lifetime))

    def register_instance(self, key: Type[Any], instance: Any) -> None:
        with self._lock:
            if key in self._factories:
                raise ValueError(f"Service already registered: {key.__name__}")
            self._factories[key] = (lambda: instance, Lifetime.SINGLETON)
            self._singletons[key] = instance

    def resolve(self, key: Type[Any]) -> Any:
        with self._lock:
            if key not in self._factories:
                raise LookupError(f"Unregistered service: {key.__name__}")
            factory, lifetime = self._factories[key]
            if lifetime is Lifetime.SINGLETON:
                if key not in self._singletons:
                    self._singletons[key] = factory()
                return self._singletons[key]
        return factory()

    @staticmethod
    def authorize(grant: Optional[CapabilityGrant], capability: str, scope: str) -> Decision:
        if grant is None or not grant.permits(capability, scope):
            return Decision.HOLD
        return Decision.PROPOSAL_ONLY

    @staticmethod
    def describe() -> Dict[str, Any]:
        return {
            "bridge": "PONS",
            "version": "1.0",
            "mode": "proposal-and-inspection",
            "source_authority": "NON_AUTHORITATIVE",
            "derived_authority": "NON_AUTHORITATIVE",
            "capability_policy": "exact-scope; missing-or-unverified-approval=HOLD",
            "execution_enabled": False,
            "git_mutation_enabled": False,
            "transmission_enabled": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def provenance_report(repository_root: Any) -> Dict[str, Any]:
        """Compare live component bytes with the immutable canonical anchor.

        This is a read-only integrity comparison, not a signature, authorship,
        or trust assertion. Missing/unreadable Git objects fail closed.
        """
        root = Path(repository_root).resolve()
        components = []
        for relative in COMPONENT_PATHS:
            current_path = (root / relative).resolve()
            if root not in current_path.parents or not current_path.is_file():
                components.append({
                    "path": relative, "status": "MISSING",
                    "current_sha256": "", "anchor_sha256": "",
                })
                continue
            try:
                current_bytes = current_path.read_bytes()
                current_hash = hashlib.sha256(current_bytes).hexdigest()
                anchored = subprocess.run(
                    ["git", "-C", str(root), "show", f"{CANONICAL_ANCHOR_SHA}:{relative}"],
                    capture_output=True, check=True,
                ).stdout
                anchor_hash = hashlib.sha256(anchored).hexdigest()
                components.append({
                    "path": relative,
                    "status": "MATCH" if current_hash == anchor_hash else "CHANGED",
                    "current_sha256": current_hash,
                    "anchor_sha256": anchor_hash,
                })
            except (OSError, subprocess.CalledProcessError):
                components.append({
                    "path": relative, "status": "UNVERIFIABLE",
                    "current_sha256": current_hash if "current_hash" in locals() else "",
                    "anchor_sha256": "",
                })
        statuses = [item["status"] for item in components]
        if any(value in {"MISSING", "CHANGED"} for value in statuses):
            overall = "DRIFT_DETECTED"
        elif any(value == "UNVERIFIABLE" for value in statuses):
            overall = "UNVERIFIABLE"
        else:
            overall = "MATCH_TO_CANONICAL_ANCHOR"
        return {
            "canonical_anchor_sha": CANONICAL_ANCHOR_SHA,
            "integrity": overall,
            "components_checked": len(components),
            "components_matching": sum(value == "MATCH" for value in statuses),
            "components": components,
            "authority": "NON_AUTHORITATIVE",
            "note": "Byte comparison against the canonical commit; not a signature or trust proof.",
        }

    @staticmethod
    def canonical_record(envelope: BridgeEnvelope) -> str:
        return json.dumps(envelope.to_record(), sort_keys=True,
                          separators=(",", ":"), ensure_ascii=False)
