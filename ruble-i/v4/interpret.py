"""Human-readable interpretation; never transmits or submits a transfer."""
from __future__ import annotations


def interpret_transfer(prepared: dict, approval_status: str = "NOT_CHECKED") -> dict:
    """Return English explanation, verification result, and transmission gate."""
    amount = prepared.get("amount_minor")
    asset = prepared.get("asset", "UNKNOWN_ASSET")
    provider = prepared.get("provider", "UNKNOWN_PROVIDER")
    rail = prepared.get("rail", "UNKNOWN_RAIL")
    english = (
        f"Prepared a {amount} minor-unit {asset} transfer using {provider} "
        f"over {rail}, for beneficiary reference {prepared.get('beneficiary_id', 'UNKNOWN')}. "
        "This is a preparation record, not a payment instruction or proof of account ownership."
    )
    verified = approval_status == "INDEPENDENTLY_VERIFIED"
    return {
        "english_interpretation": english,
        "cryptographic_review_status": approval_status,
        "review_gate_passed": verified,
        "provider_transmission": "DISABLED_IN_V4_PREPARE_MODE",
        "funds_moved": False,
        "next_action": "HUMAN_REVIEW_AND_PROVIDER_ONBOARDING_REQUIRED",
    }
