"""Independent insurance-marker interpretation; never invents asset value."""
from dataclasses import dataclass
from enum import Enum
from .reviewer import verify_reviewer_approval
MARKERS = {".rock", ".air", ".ether", ".excedra"}
class ValuationState(str, Enum):
    HOLD = "HOLD"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    EVIDENCE_BACKED = "EVIDENCE_BACKED"
@dataclass(frozen=True)
class MarkerAssessment:
    marker: str
    record_id: str
    state: ValuationState
    value_minor: int | None
    currency: str | None
    reason: str

def assess_marker(marker: str, record_id: str, *, independent_report_ref=None,
                  reviewer_approval=None, enrolled_reviewers=None, expected_proposal_sha256=None,
                  expected_scope=None, revoked_reviewers=None, now_epoch=None,
                  value_minor=None, currency=None):
    if marker not in MARKERS or not record_id.strip():
        return MarkerAssessment(marker, record_id, ValuationState.HOLD, None, None,
                                "unknown marker or missing record identifier")
    if not independent_report_ref or not reviewer_approval:
        return MarkerAssessment(marker, record_id, ValuationState.REVIEW_REQUIRED, None, None,
                                "independent report and reviewer approval are required")
    if not enrolled_reviewers:
        return MarkerAssessment(marker, record_id, ValuationState.HOLD, None, None,
                                "no trusted independent reviewer enrollment registry is available")
    if value_minor is None or currency is None or expected_proposal_sha256 is None or expected_scope is None:
        return MarkerAssessment(marker, record_id, ValuationState.REVIEW_REQUIRED, None, None,
                                "valuation amount, currency, proposal digest, and exact scope are required")
    if not isinstance(value_minor, int) or isinstance(value_minor, bool) or value_minor < 0 or currency not in {"USD", "EUR", "RUB", "KRW"}:
        return MarkerAssessment(marker, record_id, ValuationState.HOLD, None, None,
                                "invalid valuation amount or currency")
    check = verify_reviewer_approval(reviewer_approval, enrolled_reviewers=enrolled_reviewers,
        expected_proposal_sha256=expected_proposal_sha256, expected_scope=expected_scope,
        revoked_reviewers=revoked_reviewers, now_epoch=now_epoch)
    if not check.valid:
        return MarkerAssessment(marker, record_id, ValuationState.HOLD, None, None, check.reason)
    return MarkerAssessment(marker, record_id, ValuationState.EVIDENCE_BACKED, value_minor, currency,
                            "signed independent valuation recorded; not proof of ownership or liquidity")
