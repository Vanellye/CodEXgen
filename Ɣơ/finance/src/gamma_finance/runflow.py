"""Fail-closed withdrawal proposal lifecycle. No live executor exists."""
from dataclasses import dataclass
from enum import Enum

class Decision(str, Enum):
    HOLD = "HOLD"
    DENY = "DENY"
    PREPARED = "PREPARED"

@dataclass(frozen=True)
class FundingEvidence:
    evidence_id: str
    verified: bool
    available_minor: int
    currency: str
    source_ref: str
    observed_at: str
    unique: bool = True

@dataclass(frozen=True)
class Proposal:
    proposal_id: str
    amount_minor: int
    currency: str
    evidence_id: str
    decision: Decision
    reason: str
    execution_mode: str = "PREPARE_ONLY"

def prepare_withdrawal(proposal_id, amount_minor, currency, evidence, *, policy_cap_minor):
    if amount_minor <= 0 or policy_cap_minor <= 0:
        return Proposal(proposal_id, amount_minor, currency, "", Decision.DENY,
                        "amount and policy cap must be positive")
    if evidence is None:
        return Proposal(proposal_id, amount_minor, currency, "", Decision.HOLD,
                        "missing balance evidence")
    if not evidence.verified or not evidence.source_ref or not evidence.observed_at:
        return Proposal(proposal_id, amount_minor, currency, evidence.evidence_id,
                        Decision.HOLD, "balance evidence is unverified or incomplete")
    if not evidence.unique:
        return Proposal(proposal_id, amount_minor, currency, evidence.evidence_id,
                        Decision.DENY, "duplicate evidence reference")
    if currency != evidence.currency:
        return Proposal(proposal_id, amount_minor, currency, evidence.evidence_id,
                        Decision.HOLD, "currency mismatch")
    if amount_minor > policy_cap_minor or amount_minor > evidence.available_minor:
        return Proposal(proposal_id, amount_minor, currency, evidence.evidence_id,
                        Decision.DENY, "amount exceeds verified funds or policy cap")
    return Proposal(proposal_id, amount_minor, currency, evidence.evidence_id,
                    Decision.PREPARED, "proposal prepared; independent approval required")

def live_submission_enabled() -> bool:
    return False
