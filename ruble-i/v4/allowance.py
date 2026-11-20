"""Hybrid balance-backed allowance proposals; approval remains independent.

No provider calls, scheduled jobs, account aggregation, or money movement occur here.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Callable, Iterable


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
    # Stable identifier for the underlying source of funds. Wise/Plaid views of
    # the same bank account must carry the same ID and are counted only once.
    funding_source_ref: str = ""


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
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise AllowanceHold("invalid timestamp") from exc
    if dt.tzinfo is None:
        raise AllowanceHold("timestamps must include timezone")
    return dt.astimezone(timezone.utc)


def _digest(value: dict) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def prepare_hybrid_allocation(
    policy: AllowancePolicy,
    balances: Iterable[BalanceEvidence],
    beneficiaries: Iterable[BeneficiaryRequest],
    already_allocated_minor: int = 0,
    beneficiary_period_usage: dict[str, int] | None = None,
    now: datetime | None = None,
) -> dict:
    """Prepare a capped proposal using unique, verified balance evidence."""
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    limits = (policy.total_pool_cap_minor, policy.per_beneficiary_cap_minor,
              policy.per_transfer_cap_minor, policy.rolling_period_cap_minor)
    if any(value is None or value <= 0 for value in limits):
        raise AllowanceHold("all pool and limit values must be positive and configured")
    if policy.period_seconds <= 0 or policy.max_balance_age_seconds <= 0:
        raise AllowanceHold("period and evidence freshness must be positive")
    if already_allocated_minor < 0:
        raise AllowanceHold("existing allocation cannot be negative")
    if not policy.policy_version or not policy.asset:
        raise AllowanceHold("policy version and asset are required")
    if _dt(policy.allocation_expires_at) <= now:
        raise AllowanceHold("allocation policy is expired")

    evidence = list(balances)
    if not evidence:
        raise AllowanceHold("no provider balance evidence supplied")
    verified_available = 0
    evidence_refs: list[str] = []
    seen_accounts: set[tuple[str, str, str]] = set()
    seen_funding_sources: set[str] = set()
    for item in evidence:
        if not item.verified or not item.evidence_ref:
            raise AllowanceHold("balance evidence is not independently verified")
        if not item.provider or not item.account_ref or not item.funding_source_ref:
            raise AllowanceHold("provider, account, and unique funding-source references are required")
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
        if item.funding_source_ref in seen_funding_sources:
            raise AllowanceHold("duplicate underlying funding source; cross-provider double count denied")
        seen_accounts.add(account_key)
        seen_funding_sources.add(item.funding_source_ref)
        verified_available += item.available_minor - item.reserved_minor
        evidence_refs.append(item.evidence_ref)

    pool = min(policy.total_pool_cap_minor, policy.rolling_period_cap_minor,
               verified_available)
    remaining = max(0, pool - already_allocated_minor)
    usage = beneficiary_period_usage or {}
    rows = []
    total = 0
    seen_beneficiaries: set[str] = set()
    for request in beneficiaries:
        if not request.beneficiary_id or request.requested_minor <= 0:
            raise AllowanceHold("beneficiary and positive requested amount required")
        if request.beneficiary_id in seen_beneficiaries:
            raise AllowanceHold("duplicate beneficiary request")
        seen_beneficiaries.add(request.beneficiary_id)
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
        "schema": "ruble-i.v4.hybrid-allowance-proposal.v2",
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
    proposal["proposal_sha256"] = _digest(proposal)
    return proposal


def approve_allocation_proposal(
    proposal: dict,
    approval_artifact: dict | None,
    verifier: Callable[[dict, dict], bool] | None,
) -> dict:
    """Verify independent Ed25519 approval through the injected trusted verifier.

    The verifier must be Ed25519ReviewerVerifier.verify backed by an externally
    governed registry. A test-only permissive callback is never production trust.
    """
    if not approval_artifact or verifier is None:
        raise AllowanceHold("independent approval evidence/verifier missing")
    if proposal.get("mode") != "PREPARE_ONLY" or proposal.get("live_submission_enabled") is not False:
        raise AllowanceHold("proposal is not a valid prepare-only proposal")
    digest = proposal.get("proposal_sha256")
    if not digest or approval_artifact.get("intent_sha256") != digest:
        raise AllowanceHold("approval is not bound to exact allowance proposal")
    if approval_artifact.get("policy_version") != proposal.get("policy_version"):
        raise AllowanceHold("approval policy version mismatch")
    if not approval_artifact.get("reviewer_id") or approval_artifact.get("reviewer_id") == "self":
        raise AllowanceHold("independent reviewer identity missing or self-approved")
    prepared = {
        "intent_sha256": digest,
        "provider": "ruble_i_allowance",
        "rail": "SCHEDULED_ALLOCATION",
        "beneficiary_id": "MULTI_BENEFICIARY",
        "asset": proposal["asset"],
        "amount_minor": proposal["proposed_total_minor"],
        "fee_limit_minor": 0,
        "policy_version": proposal["policy_version"],
    }
    if verifier(prepared, approval_artifact) is not True:
        raise AllowanceHold("reviewer signature, scope, freshness, or revocation check failed")
    return {
        **proposal,
        "status": "INDEPENDENTLY_APPROVED_ALLOCATION_PROPOSAL",
        "approval_status": "INDEPENDENTLY_VERIFIED",
        "next_state": "ALLOCATION_RECORDING_REQUIRES_SEPARATE_GOVERNED_COMMIT",
        "live_submission_enabled": False,
    }
