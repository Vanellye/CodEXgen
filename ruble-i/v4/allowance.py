"""Hybrid, prepare-only allowance allocator for Ruble-I v4.

Balances are evidence inputs, not authorization. Allocations remain proposals
until independently approved. This module never calls a provider or moves funds.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Iterable


class AllowanceHold(Exception):
    pass


@dataclass(frozen=True)
class BalanceEvidence:
    provider: str
    account_ref: str
    asset: str
    available_minor: int
    reserved_minor: int
    observed_at: str
    verified: bool
    evidence_ref: str


@dataclass(frozen=True)
class BeneficiaryRequest:
    beneficiary_id: str
    requested_minor: int
    per_period_cap_minor: int


@dataclass(frozen=True)
class AllowancePolicy:
    policy_version: str
    asset: str
    total_pool_cap_minor: int
    per_beneficiary_cap_minor: int
    per_transfer_cap_minor: int
    rolling_period_cap_minor: int
    period_seconds: int
    max_balance_age_seconds: int
    allocation_expires_at: str


def _dt(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise AllowanceHold("timestamps must include timezone")
    return dt.astimezone(timezone.utc)


def prepare_hybrid_allocation(
    policy: AllowancePolicy,
    balances: Iterable[BalanceEvidence],
    beneficiaries: Iterable[BeneficiaryRequest],
    already_allocated_minor: int = 0,
    beneficiary_period_usage: dict[str, int] | None = None,
    now: datetime | None = None,
) -> dict:
    """Prepare a capped proposal using verified balances and configured limits."""
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if min(policy.total_pool_cap_minor, policy.per_beneficiary_cap_minor,
           policy.per_transfer_cap_minor, policy.rolling_period_cap_minor) <= 0:
        raise AllowanceHold("all pool and limit values must be positive and configured")
    if policy.period_seconds <= 0 or policy.max_balance_age_seconds <= 0:
        raise AllowanceHold("period and evidence freshness must be positive")
    if already_allocated_minor < 0:
        raise AllowanceHold("existing allocation cannot be negative")
    if _dt(policy.allocation_expires_at) <= now:
        raise AllowanceHold("allocation policy is expired")

    evidence = list(balances)
    if not evidence:
        raise AllowanceHold("no provider balance evidence supplied")
    verified_available = 0
    evidence_refs = []
    seen_accounts = set()
    for item in evidence:
        if not item.verified or not item.evidence_ref:
            raise AllowanceHold("balance evidence is not independently verified")
        if item.asset != policy.asset:
            continue
        if item.available_minor < 0 or item.reserved_minor < 0:
            raise AllowanceHold("negative balance or reserve rejected")
        if item.reserved_minor > item.available_minor:
            raise AllowanceHold("reserve exceeds available balance")
        observed = _dt(item.observed_at)
        age = (now - observed).total_seconds()
        if age < 0 or age > policy.max_balance_age_seconds:
            raise AllowanceHold("balance evidence is stale or from the future")
        account_key = (item.provider, item.account_ref, item.asset)
        if account_key in seen_accounts:
            raise AllowanceHold("duplicate provider account evidence")
        seen_accounts.add(account_key)
        verified_available += item.available_minor - item.reserved_minor
        evidence_refs.append(item.evidence_ref)

    pool = min(policy.total_pool_cap_minor, policy.rolling_period_cap_minor,
               verified_available)
    remaining = max(0, pool - already_allocated_minor)
    usage = beneficiary_period_usage or {}
    rows = []
    total = 0
    for request in beneficiaries:
        if not request.beneficiary_id or request.requested_minor <= 0:
            raise AllowanceHold("beneficiary and positive requested amount required")
        if request.per_period_cap_minor <= 0:
            raise AllowanceHold("beneficiary period cap must be configured")
        prior = usage.get(request.beneficiary_id, 0)
        if prior < 0:
            raise AllowanceHold("negative beneficiary period usage")
        cap = min(policy.per_beneficiary_cap_minor,
                  request.per_period_cap_minor,
                  policy.per_transfer_cap_minor)
        available_for_beneficiary = max(0, cap - prior)
        grant = min(request.requested_minor, available_for_beneficiary, remaining)
        rows.append({
            "beneficiary_id": request.beneficiary_id,
            "requested_minor": request.requested_minor,
            "proposed_minor": grant,
            "prior_period_usage_minor": prior,
            "beneficiary_period_cap_minor": cap,
            "status": "PROPOSED" if grant else "ZERO_ALLOCATION",
        })
        total += grant
        remaining -= grant

    proposal = {
        "schema": "ruble-i.v4.hybrid-allowance-proposal.v1",
        "mode": "PREPARE_ONLY",
        "status": "AWAITING_INDEPENDENT_APPROVAL",
        "policy_version": policy.policy_version,
        "asset": policy.asset,
        "verified_available_after_reserves_minor": verified_available,
        "configured_total_pool_cap_minor": policy.total_pool_cap_minor,
        "rolling_period_cap_minor": policy.rolling_period_cap_minor,
        "already_allocated_minor": already_allocated_minor,
        "proposed_total_minor": total,
        "unallocated_pool_minor": remaining,
        "period_seconds": policy.period_seconds,
        "expires_at": policy.allocation_expires_at,
        "balance_evidence_refs": sorted(evidence_refs),
        "beneficiaries": rows,
        "live_submission_enabled": False,
    }
    canonical = json.dumps(proposal, sort_keys=True, separators=(",", ":"))
    proposal["proposal_sha256"] = sha256(canonical.encode()).hexdigest()
    return proposal
