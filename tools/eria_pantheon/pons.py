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
import math


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
    def __init__(
        self, *, reviewer_root_public_key_b64: Optional[str] = None,
        revoked_reviewer_key_ids: Optional[set[str]] = None,
    ) -> None:
        self._factories: Dict[Type[Any], tuple[Callable[[], Any], Lifetime]] = {}
        self._singletons: Dict[Type[Any], Any] = {}
        self._lock = threading.RLock()
        self._accuracy_service = None
        self._reviewer_identity = None
        if reviewer_root_public_key_b64:
            from .reviewer_identity import ReviewerIdentityAuthority
            self._reviewer_identity = ReviewerIdentityAuthority(
                reviewer_root_public_key_b64, revoked_key_ids=revoked_reviewer_key_ids
            )

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

    def install_accuracy_service(self, ledger_path: str) -> Any:
        """Install the sole AVS authority as a PONS-owned singleton."""
        from .accuracy import AccuracyValidationService, _PONS_AUTHORITY
        with self._lock:
            if self._accuracy_service is None:
                self._accuracy_service = AccuracyValidationService(
                    ledger_path, authority=_PONS_AUTHORITY
                )
        return {"installed": True, "authority": "PONS_ONLY"}

    def reviewer_identity_configured(self) -> bool:
        return self._reviewer_identity is not None

    def issue_reviewer_challenge(self, certificate: Dict[str, Any]) -> Dict[str, str]:
        if self._reviewer_identity is None:
            raise PermissionError("PONS reviewer trust root is not configured; evidence intake is disabled.")
        if self._accuracy_service is None:
            raise LookupError("PONS AVS service is not installed.")
        challenge = self._reviewer_identity.issue_challenge(certificate)
        self._accuracy_service.ledger.append({
            "record_type": "reviewer_challenge_issued",
            "challenge_id": challenge["challenge_id"],
            "nonce": challenge["nonce"],
            "reviewer_id": challenge["reviewer_id"],
            "reviewer_key_id": challenge["key_id"],
            "reviewer_certificate_sha256": challenge["certificate_sha256"],
            "issued_at": challenge["issued_at"],
            "expires_at": challenge["expires_at"],
        })
        return challenge

    def submit_accuracy_evidence(
        self, *, certificate: Dict[str, Any], challenge_id: str,
        signed_payload: Dict[str, Any], signature_b64: str,
    ) -> Dict[str, Any]:
        from .accuracy import _PONS_AUTHORITY
        if self._accuracy_service is None:
            raise LookupError("PONS AVS service is not installed.")
        if self._reviewer_identity is None:
            raise PermissionError("PONS reviewer trust root is not configured; evidence intake is disabled.")
        required = {"challenge_id", "nonce", "claim_id", "subject_component",
                    "evidence_ref", "outcome", "weight", "method", "signed_at"}
        if not isinstance(signed_payload, dict) or set(signed_payload) != required:
            raise ValueError("Signed evidence payload has an invalid schema.")
        if signed_payload.get("challenge_id") != challenge_id:
            raise PermissionError("Challenge ID mismatch.")
        if not isinstance(signed_payload.get("claim_id"), str) or not signed_payload["claim_id"].strip():
            raise ValueError("claim_id is required.")
        if not isinstance(signed_payload.get("subject_component"), str) or not signed_payload["subject_component"].strip():
            raise ValueError("subject_component is required.")
        if not isinstance(signed_payload.get("evidence_ref"), str) or not signed_payload["evidence_ref"].strip():
            raise ValueError("evidence_ref is required.")
        if type(signed_payload.get("outcome")) is not bool:
            raise ValueError("outcome must be a boolean.")
        weight = signed_payload.get("weight")
        if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not math.isfinite(weight) or not 0 < weight <= 100:
            raise ValueError("weight must be finite, greater than 0, and at most 100.")
        if not isinstance(signed_payload.get("method"), str) or not signed_payload["method"].strip():
            raise ValueError("method is required.")
        reviewer = self._reviewer_identity.authenticate_evidence(
            certificate=certificate, challenge_id=challenge_id,
            signed_payload=signed_payload, signature_b64=signature_b64,
        )
        if reviewer.reviewer_id == signed_payload["subject_component"]:
            raise PermissionError("Self-certification is prohibited.")
        from dataclasses import asdict
        return self._accuracy_service.submit_evidence(
            claim_id=signed_payload["claim_id"],
            subject_component=signed_payload["subject_component"],
            evidence_ref=signed_payload["evidence_ref"],
            outcome=signed_payload["outcome"],
            weight=float(weight),
            method=signed_payload["method"],
            verified_reviewer=asdict(reviewer),
            certificate=certificate,
            signed_payload=signed_payload,
            signature_b64=signature_b64,
            _authority=_PONS_AUTHORITY,
        )

    def evaluate_accuracy(self, required_claims: Any) -> Dict[str, Any]:
        from .accuracy import _PONS_AUTHORITY
        from .reviewer_identity import ReviewerAuthenticationError
        if self._accuracy_service is None:
            raise LookupError("PONS AVS service is not installed.")
        if self._reviewer_identity is None:
            raise PermissionError("PONS reviewer trust root is not configured; accuracy scores are disabled.")
        authenticated_ids = set()
        ledger_records = self._accuracy_service.ledger.records()
        challenges = {
            item.get("challenge_id"): item
            for item in ledger_records
            if item.get("record_type") == "reviewer_challenge_issued"
        }
        for record in ledger_records:
            if record.get("record_type") != "avs_evidence":
                continue
            try:
                reviewer = self._reviewer_identity.verify_stored_attestation(
                    certificate=record["reviewer_certificate"],
                    signed_payload=record["signed_payload"],
                    signature_b64=record["reviewer_signature_ed25519"],
                )
                payload = record["signed_payload"]
                if (
                    reviewer.reviewer_id == record.get("verifier_id")
                    and payload.get("claim_id") == record.get("claim_id")
                    and payload.get("subject_component") == record.get("subject_component")
                    and payload.get("evidence_ref") == record.get("evidence_ref")
                    and payload.get("outcome") is record.get("outcome")
                    and payload.get("weight") == record.get("weight")
                    and payload.get("method") == record.get("method")
                    and reviewer.key_id == record.get("reviewer_key_id")
                    and reviewer.certificate_sha256 == record.get("reviewer_certificate_sha256")
                    and reviewer.public_key_sha256 == record.get("reviewer_public_key_sha256")
                    and record.get("identity_verified") is True
                    and payload.get("challenge_id") in challenges
                    and payload.get("nonce") == challenges[payload.get("challenge_id")].get("nonce")
                    and reviewer.reviewer_id == challenges[payload.get("challenge_id")].get("reviewer_id")
                    and reviewer.key_id == challenges[payload.get("challenge_id")].get("reviewer_key_id")
                    and payload.get("signed_at") >= challenges[payload.get("challenge_id")].get("issued_at")
                    and payload.get("signed_at") <= challenges[payload.get("challenge_id")].get("expires_at")
                ):
                    authenticated_ids.add(record["evidence_id"])
            except (KeyError, TypeError, ValueError, ReviewerAuthenticationError):
                continue
        return self._accuracy_service.evaluate(
            required_claims, authenticated_evidence_ids=authenticated_ids,
            _authority=_PONS_AUTHORITY,
        )

    def accuracy_ledger_status(self) -> Dict[str, Any]:
        if self._accuracy_service is None:
            raise LookupError("PONS AVS service is not installed.")
        return self._accuracy_service.ledger.verify()

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
            "accuracy_authority": "PONS_ONLY",
            "self_certification_allowed": False,
            "reviewer_identity": "ED25519_ROOT_CERTIFICATE_REQUIRED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def canonical_record(envelope: BridgeEnvelope) -> str:
        return json.dumps(envelope.to_record(), sort_keys=True,
                          separators=(",", ":"), ensure_ascii=False)
