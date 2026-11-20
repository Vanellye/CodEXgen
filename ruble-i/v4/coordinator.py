"""Ruble-I v4 prepare-only coordinator. No provider calls or live withdrawals."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from typing import Callable, Iterable


LIVE_SUBMISSION_ENABLED = False


class HoldTransfer(Exception):
    """Transfer cannot proceed because a required control is missing or failed."""


class LiveExecutionDisabled(RuntimeError):
    """Live provider submission is intentionally unavailable in v4 prepare mode."""


@dataclass(frozen=True)
class TransferIntent:
    intent_id: str
    source_account_ref: str
    beneficiary_id: str
    provider: str
    rail: str
    asset: str
    amount_minor: int
    fee_limit_minor: int
    idempotency_key: str
    purpose: str
    created_at: str
    expires_at: str
    policy_version: str = "v4.0.0"

    def canonical(self) -> str:
        return json.dumps(self.__dict__, sort_keys=True, separators=(",", ":"))

    def digest(self) -> str:
        return sha256(self.canonical().encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class BoundedPolicy:
    version: str
    expires_at: str
    allowed_providers: frozenset[str]
    allowed_rails: frozenset[str]
    allowed_assets: frozenset[str]
    allowed_beneficiary_ids: frozenset[str]
    per_transfer_max_minor: int | None
    rolling_24h_max_minor: int | None
    per_beneficiary_rolling_24h_max_minor: int | None
    max_fee_minor: int | None
    configured: bool = True


@dataclass(frozen=True)
class HistoricalTransfer:
    beneficiary_id: str
    asset: str
    amount_minor: int
    occurred_at: str


def _time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise HoldTransfer("timestamps must include a timezone")
    return parsed.astimezone(timezone.utc)


def prepare_transfer(
    intent: TransferIntent,
    policy: BoundedPolicy,
    history: Iterable[HistoricalTransfer] = (),
    now: datetime | None = None,
) -> dict:
    """Validate and prepare only; never submits a payment."""
    if not policy.configured:
        raise HoldTransfer("bounded withdrawal limits are not configured")
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise HoldTransfer("coordinator clock must be timezone-aware")
    now = now.astimezone(timezone.utc)
    expiry = _time(intent.expires_at)
    created = _time(intent.created_at)
    policy_expiry = _time(policy.expires_at)
    if expiry <= now or created > now or policy_expiry <= now:
        raise HoldTransfer("intent or policy is expired/not yet valid")
    if intent.amount_minor <= 0 or intent.fee_limit_minor < 0:
        raise HoldTransfer("invalid amount or fee ceiling")
    if not intent.intent_id or not intent.idempotency_key or not intent.beneficiary_id:
        raise HoldTransfer("required identifiers are missing")
    if intent.provider not in policy.allowed_providers:
        raise HoldTransfer("provider is not allowlisted")
    if intent.rail not in policy.allowed_rails:
        raise HoldTransfer("payment rail is not allowlisted")
    if intent.asset not in policy.allowed_assets:
        raise HoldTransfer("asset is not allowlisted")
    if intent.beneficiary_id not in policy.allowed_beneficiary_ids:
        raise HoldTransfer("beneficiary is not independently verified/allowlisted")
    caps = (policy.per_transfer_max_minor, policy.rolling_24h_max_minor,
            policy.per_beneficiary_rolling_24h_max_minor, policy.max_fee_minor)
    if any(cap is None or cap < 0 for cap in caps):
        raise HoldTransfer("all bounded limits must be explicitly configured")
    if intent.amount_minor > policy.per_transfer_max_minor:
        raise HoldTransfer("per-transfer cap exceeded")
    if intent.fee_limit_minor > policy.max_fee_minor:
        raise HoldTransfer("fee ceiling exceeded")
    window_start = now - timedelta(hours=24)
    recent = []
    for item in history:
        when = _time(item.occurred_at)
        if window_start <= when <= now and item.asset == intent.asset:
            recent.append(item)
    total = sum(item.amount_minor for item in recent)
    beneficiary_total = sum(item.amount_minor for item in recent
                            if item.beneficiary_id == intent.beneficiary_id)
    if total + intent.amount_minor > policy.rolling_24h_max_minor:
        raise HoldTransfer("rolling 24-hour aggregate cap exceeded")
    if beneficiary_total + intent.amount_minor > policy.per_beneficiary_rolling_24h_max_minor:
        raise HoldTransfer("beneficiary rolling 24-hour cap exceeded")
    return {
        "status": "PREPARED",
        "mode": "PREPARE_ONLY",
        "intent_id": intent.intent_id,
        "intent_sha256": intent.digest(),
        "provider": intent.provider,
        "rail": intent.rail,
        "beneficiary_id": intent.beneficiary_id,
        "asset": intent.asset,
        "amount_minor": intent.amount_minor,
        "fee_limit_minor": intent.fee_limit_minor,
        "policy_version": policy.version,
        "live_submission_enabled": False,
        "next_state": "AWAITING_INDEPENDENT_APPROVAL",
    }


def verify_independent_approval(
    prepared: dict,
    approval_artifact: dict | None,
    verifier: Callable[[dict, dict], bool] | None,
) -> dict:
    """Fail closed unless an independent verifier accepts exact-intent evidence."""
    if not approval_artifact or verifier is None:
        raise HoldTransfer("independent approval evidence/verifier missing")
    if approval_artifact.get("intent_sha256") != prepared.get("intent_sha256"):
        raise HoldTransfer("approval is not bound to this exact transfer intent")
    if approval_artifact.get("policy_version") != prepared.get("policy_version"):
        raise HoldTransfer("approval policy version mismatch")
    if approval_artifact.get("reviewer_id") in (None, "", "self"):
        raise HoldTransfer("independent reviewer identity missing or self-approved")
    if verifier(prepared, approval_artifact) is not True:
        raise HoldTransfer("reviewer signature, scope, freshness, or revocation check failed")
    return {**prepared, "approval_status": "INDEPENDENTLY_VERIFIED",
            "next_state": "SUBMISSION_DISABLED", "live_submission_enabled": False}


def submit_live_transfer(*_args, **_kwargs):
    raise LiveExecutionDisabled("v4 PREPARE_ONLY: live transfer submission is disabled")
