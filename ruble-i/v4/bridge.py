"""Normalized Wise/Plaid evidence bridge for PREPARE_ONLY allowance proposals.

This is an adapter boundary, not an authenticated provider client. Connection
attestations must come from separately verified provider integrations.
"""
from __future__ import annotations
from dataclasses import dataclass
from allowance import (
    AllowancePolicy, BalanceEvidence, BeneficiaryRequest,
    AllowanceHold, prepare_hybrid_allocation,
)


@dataclass(frozen=True)
class ProviderConnectionEvidence:
    provider: str
    authenticated: bool
    account_verified: bool
    transfer_permission_verified: bool
    eligible_rails: frozenset[str]
    connection_evidence_ref: str


def prepare_cross_provider_allowance(
    policy: AllowancePolicy,
    connections: list[ProviderConnectionEvidence],
    balances: list[BalanceEvidence],
    beneficiaries: list[BeneficiaryRequest],
    already_allocated_minor: int = 0,
    beneficiary_period_usage: dict[str, int] | None = None,
    now=None,
) -> dict:
    """Validate each provider boundary then prepare one normalized proposal."""
    if not connections:
        raise AllowanceHold("no separately authenticated provider connection evidence")
    allowed = {"wise_platform", "plaid_transfer"}
    seen = set()
    connection_refs = []
    for item in connections:
        if item.provider not in allowed or item.provider in seen:
            raise AllowanceHold("unknown or duplicate provider connection")
        if not (item.authenticated and item.account_verified and
                item.transfer_permission_verified and item.connection_evidence_ref):
            raise AllowanceHold("provider authentication, account, or permission evidence missing")
        if not item.eligible_rails:
            raise AllowanceHold("provider has no verified eligible payment rails")
        seen.add(item.provider)
        connection_refs.append(item.connection_evidence_ref)
    if any(balance.provider not in seen for balance in balances):
        raise AllowanceHold("balance evidence has no matching authenticated provider connection")
    proposal = prepare_hybrid_allocation(
        policy, balances, beneficiaries,
        already_allocated_minor=already_allocated_minor,
        beneficiary_period_usage=beneficiary_period_usage,
        now=now,
    )
    proposal["provider_connections"] = sorted(connection_refs)
    proposal["provider_set"] = sorted(seen)
    proposal["status"] = "CROSS_PROVIDER_PROPOSAL_AWAITING_INDEPENDENT_APPROVAL"
    # Recompute digest after adding bridge evidence, so the reviewer signs the
    # exact provider set and connection evidence references too.
    import hashlib, json
    proposal.pop("proposal_sha256", None)
    canonical = json.dumps(proposal, sort_keys=True, separators=(",", ":"))
    proposal["proposal_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return proposal
