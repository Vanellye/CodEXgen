import json
from io import BytesIO
import pytest
from gamma_finance.valuation import ValuationState, assess_marker
from gamma_finance.reviewer import verify_reviewer_approval
from gamma_finance.firecrawl import scrape

FIXTURE=json.loads((__import__("pathlib").Path(__file__).parent/"fixtures"/"reviewer-approval-test-only.json").read_text())
PAYLOAD=FIXTURE["payload"]
REGISTRY={PAYLOAD["reviewer_id"]:{"public_key_pem":FIXTURE["public_key_pem"],"enabled":True}}

def test_signed_fixture_verifies_exact_scope_and_digest():
    r=verify_reviewer_approval(FIXTURE,enrolled_reviewers=REGISTRY,
      expected_proposal_sha256=PAYLOAD["proposal_sha256"],expected_scope=PAYLOAD["scope"],now_epoch=PAYLOAD["issued_at"]+1)
    assert r.valid

def test_valuation_requires_cryptographically_verified_reviewer():
    r=assess_marker(".air","asset-fixture-001",independent_report_ref="fixture-report:1",
      reviewer_approval=FIXTURE,enrolled_reviewers=REGISTRY,
      expected_proposal_sha256=PAYLOAD["proposal_sha256"],expected_scope=PAYLOAD["scope"],
      value_minor=1250,currency="USD",now_epoch=PAYLOAD["issued_at"]+1)
    assert r.state==ValuationState.EVIDENCE_BACKED and r.value_minor==1250

def test_missing_unenrolled_wrong_scope_revoked_and_stale_approval_hold():
    kwargs=dict(independent_report_ref="fixture-report:1",reviewer_approval=FIXTURE,
      enrolled_reviewers=REGISTRY,expected_proposal_sha256=PAYLOAD["proposal_sha256"],
      expected_scope=PAYLOAD["scope"],value_minor=1250,currency="USD")
    assert assess_marker(".rock","asset-1",**{**kwargs,"enrolled_reviewers":{}},now_epoch=PAYLOAD["issued_at"]+1).state==ValuationState.HOLD
    assert assess_marker(".rock","asset-1",**{**kwargs,"expected_scope":"wrong"},now_epoch=PAYLOAD["issued_at"]+1).state==ValuationState.HOLD
    assert assess_marker(".rock","asset-1",**{**kwargs,"revoked_reviewers":{PAYLOAD["reviewer_id"]}},now_epoch=PAYLOAD["issued_at"]+1).state==ValuationState.HOLD
    assert assess_marker(".rock","asset-1",**kwargs,now_epoch=PAYLOAD["expires_at"]).state==ValuationState.HOLD

def test_signature_tampering_holds():
    bad={**FIXTURE,"signature_base64":"A"*88}
    r=verify_reviewer_approval(bad,enrolled_reviewers=REGISTRY,
      expected_proposal_sha256=PAYLOAD["proposal_sha256"],expected_scope=PAYLOAD["scope"],now_epoch=PAYLOAD["issued_at"]+1)
    assert not r.valid

def test_marker_without_evidence_has_no_value():
    r=assess_marker(".rock","asset-1")
    assert r.state==ValuationState.REVIEW_REQUIRED and r.value_minor is None

def test_invalid_marker_or_value_holds():
    assert assess_marker(".fake","asset").state==ValuationState.HOLD
    assert assess_marker(".ether","asset",independent_report_ref="r",reviewer_approval=FIXTURE,
      enrolled_reviewers=REGISTRY,expected_proposal_sha256=PAYLOAD["proposal_sha256"],
      expected_scope=PAYLOAD["scope"],value_minor=-1,currency="USD",now_epoch=PAYLOAD["issued_at"]+1).state==ValuationState.HOLD

def test_firecrawl_rejects_http_unapproved_and_local_hosts():
    with pytest.raises(ValueError): scrape("http://example.com",allowed_domains={"example.com"})
    with pytest.raises(ValueError): scrape("https://not-allowed.com",allowed_domains={"example.com"})
    with pytest.raises(ValueError): scrape("https://service.local",allowed_domains={"service.local"})
    with pytest.raises(ValueError): scrape("https://example.com",allowed_domains={"*.com"})

def test_firecrawl_rejects_unapproved_final_redirect(monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY","fixture-key-not-real")
    payload={"success":True,"data":{"markdown":"evidence",
      "metadata":{"sourceURL":"https://example.com/start","url":"https://redirect-target.com/final"}}}
    class Response(BytesIO):
        def __enter__(self): return self
        def __exit__(self,*args): self.close()
    monkeypatch.setattr("gamma_finance.firecrawl.urlopen",
      lambda request,timeout: Response(json.dumps(payload).encode("utf-8")))
    with pytest.raises(RuntimeError,match="redirect hostname"):
        scrape("https://example.com/start",allowed_domains={"example.com"})

def test_firecrawl_accepts_mocked_same_host_response(monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY","fixture-key-not-real")
    payload={"success":True,"data":{"markdown":"public sample",
      "metadata":{"sourceURL":"https://example.com/start","url":"https://example.com/final"}}}
    class Response(BytesIO):
        def __enter__(self): return self
        def __exit__(self,*args): self.close()
    monkeypatch.setattr("gamma_finance.firecrawl.urlopen",
      lambda request,timeout: Response(json.dumps(payload).encode("utf-8")))
    result=scrape("https://example.com/start",allowed_domains={"example.com"})
    assert result.domain=="example.com"
    assert result.final_url=="https://example.com/final"
    assert result.mode=="SOURCE_EVIDENCE_ONLY"
