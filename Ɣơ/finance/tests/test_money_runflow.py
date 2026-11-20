from datetime import date
from fractions import Fraction
import pytest
from gamma_finance.money import FxQuote, Money
from gamma_finance.runflow import Decision, FundingEvidence, live_submission_enabled, prepare_withdrawal

def test_currency_minor_units_and_exact_fx():
    quote = FxQuote("USD", "EUR", Fraction(9, 10), date(2026, 11, 20), "fixture:exact-rate")
    assert quote.convert_minor(Money("USD", 1000)) == Money("EUR", 900)
    assert Money("KRW", 100).add(Money("KRW", 50)) == Money("KRW", 150)

def test_fx_requires_source_and_positive_rate():
    with pytest.raises(ValueError):
        FxQuote("USD", "EUR", Fraction(0, 1), date(2026, 11, 20), "fixture")

def test_missing_or_unverified_balance_holds():
    assert prepare_withdrawal("p1", 100, "USD", None, policy_cap_minor=1000).decision == Decision.HOLD
    bad = FundingEvidence("e1", False, 1000, "USD", "bank:ref", "2026-11-20T10:00:00Z")
    assert prepare_withdrawal("p2", 100, "USD", bad, policy_cap_minor=1000).decision == Decision.HOLD

def test_duplicate_or_excessive_proposal_denied():
    duplicate = FundingEvidence("e2", True, 1000, "USD", "bank:ref", "2026-11-20T10:00:00Z", False)
    assert prepare_withdrawal("p3", 100, "USD", duplicate, policy_cap_minor=1000).decision == Decision.DENY
    valid = FundingEvidence("e3", True, 1000, "USD", "bank:ref2", "2026-11-20T10:00:00Z")
    assert prepare_withdrawal("p4", 1001, "USD", valid, policy_cap_minor=2000).decision == Decision.DENY

def test_prepared_is_not_live():
    valid = FundingEvidence("e4", True, 1000, "USD", "bank:ref3", "2026-11-20T10:00:00Z")
    p = prepare_withdrawal("p5", 100, "USD", valid, policy_cap_minor=1000)
    assert p.decision == Decision.PREPARED
    assert p.execution_mode == "PREPARE_ONLY"
    assert live_submission_enabled() is False
