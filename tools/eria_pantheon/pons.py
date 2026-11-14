#!/usr/bin/env python3
"""PONS: small, fail-closed ERIA/PANTHEON service and provenance bridge.

Application-level contract boundary only; not an OS sandbox, identity provider,
cryptographic verifier, or Pantheon compiler/runtime.
"""
from __future__ import annotations

import hashlib
import json
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, Optional, Type


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
    def canonical_record(envelope: BridgeEnvelope) -> str:
        return json.dumps(envelope.to_record(), sort_keys=True,
                          separators=(",", ":"), ensure_ascii=False)
