"""Independent insurance-marker interpretation; never invents asset value."""
from dataclasses import dataclass
from enum import Enum
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
                  reviewer_ref=None, value_minor=None, currency=None):
    if marker not in MARKERS or not record_id.strip():
        return MarkerAssessment(marker, record_id, ValuationState.HOLD, None, None,
                                "unknown marker or missing record identifier")
    if not independent_report_ref or not reviewer_ref or value_minor is None or currency is None:
        return MarkerAssessment(marker, record_id, ValuationState.REVIEW_REQUIRED, None, None,
                                "marker is metadata only; independent valuation evidence is incomplete")
    if value_minor < 0 or currency not in {"USD", "EUR", "RUB", "KRW"}:
        return MarkerAssessment(marker, record_id, ValuationState.HOLD, None, None,
                                "invalid valuation amount or currency")
    return MarkerAssessment(marker, record_id, ValuationState.EVIDENCE_BACKED, value_minor, currency,
                            "independent valuation recorded; not proof of liquidity")
