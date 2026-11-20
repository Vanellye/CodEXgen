import pytest
from gamma_finance.valuation import ValuationState, assess_marker
from gamma_finance.firecrawl import scrape
def test_marker_without_independent_evidence_has_no_value():
    r=assess_marker(".rock","asset-1")
    assert r.state==ValuationState.REVIEW_REQUIRED and r.value_minor is None
def test_independent_marker_valuation_is_recorded_not_liquidity():
    r=assess_marker(".air","asset-2",independent_report_ref="report:7",
                    reviewer_ref="reviewer:key-9",value_minor=1250,currency="USD")
    assert r.state==ValuationState.EVIDENCE_BACKED and r.value_minor==1250
def test_invalid_marker_or_value_holds():
    assert assess_marker(".fake","asset").state==ValuationState.HOLD
    assert assess_marker(".ether","asset",independent_report_ref="r",reviewer_ref="k",
                         value_minor=-1,currency="USD").state==ValuationState.HOLD
def test_firecrawl_enforces_https_allowlist():
    with pytest.raises(ValueError): scrape("http://example.com",allowed_domains={"example.com"})
    with pytest.raises(ValueError): scrape("https://bad.example",allowed_domains={"example.com"})
