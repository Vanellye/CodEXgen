import base64, hashlib, json
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from gamma_ops.coddoc import load_coddoc, ordered_events, validate_document
from gamma_ops.readiness import readiness_result
from gamma_ops.reviewer import canonical_payload

ROOT = Path(__file__).parents[1]
SAMPLE = ROOT / "events" / "TRUE-LIGHTWORK-WAVE-MAVEN.coddoc"

def _approved_record(tmp_path, monkeypatch, *, tier="READ_ONLY"):
    artifact = tmp_path / "artifact.md"
    artifact.write_text("reviewable artifact", encoding="utf-8")
    artifact_digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    private = Ed25519PrivateKey.generate()
    public_pem = private.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode("utf-8")
    registry = {"format":"ERIA_REVIEWER_REGISTRY","version":1,
                "reviewers":{"reviewer-fixture":{"enabled":True,"public_key_pem":public_pem}},"revoked":[]}
    registry_path = tmp_path / "reviewers.json"
    registry_bytes = (json.dumps(registry,sort_keys=True,separators=(",",":"))+"\n").encode("utf-8")
    registry_path.write_bytes(registry_bytes)
    monkeypatch.setenv("ERIA_REVIEWER_REGISTRY_SHA256",hashlib.sha256(registry_bytes).hexdigest())
    now = 1795194000
    payload = {"proposal_sha256":artifact_digest,"scope":"open:artifact.md",
      "commit_sha":"0123456789abcdef0123456789abcdef01234567",
      "review_ref":"review:fixture-1","issued_at":now-1,"expires_at":now+3600,
      "reviewer_id":"reviewer-fixture"}
    approval={"payload":payload,"signature_base64":base64.b64encode(private.sign(canonical_payload(payload))).decode("ascii")}
    approval_path=tmp_path/"approval.json"
    approval_path.write_text(json.dumps(approval),encoding="utf-8")
    record={
      "operable_id":"demo","readiness_state":"READY_TO_OPEN","execution_tier":tier,
      "live_execution_enabled":False,
      "checks":{key:"PASS" for key in ("python_tests","arm64_compile","inventory","coddoc_validation")},
      "review":{"state":"APPROVED","review_ref":"review:fixture-1","approval_path":"approval.json",
        "reviewer_registry_path":"reviewers.json","scope":"open:artifact.md","commit_sha":payload["commit_sha"]},
      "source_ref":"commit:"+payload["commit_sha"],"artifact_path":"artifact.md"
    }
    return record,registry_path,now

def test_coddoc_validates_and_preserves_unknown_timestamps():
    doc = load_coddoc(SAMPLE)
    assert doc["document_id"] == "true-lightwork-wave-maven"
    assert any(event["occurred_at"] is None for event in doc["events"])
    assert len(doc["_source_sha256"]) == 64

def test_timeline_uses_authored_sequence_not_invented_time():
    doc = load_coddoc(SAMPLE)
    ordered = ordered_events(doc)
    assert [event["sequence"] for event in ordered] == sorted(event["sequence"] for event in ordered)
    assert ordered[0]["occurred_at"] is None

def test_duplicate_sequence_is_rejected():
    doc = json.loads(SAMPLE.read_text(encoding="utf-8"))
    doc["events"][1]["sequence"] = doc["events"][0]["sequence"]
    assert any("sequence is duplicated" in error for error in validate_document(doc))

def test_operable_is_not_ready_without_all_gates(tmp_path,monkeypatch):
    record,_,now=_approved_record(tmp_path,monkeypatch)
    record["checks"].pop("coddoc_validation")
    (tmp_path/"artifact.md").unlink()
    ready,reasons=readiness_result(record,repository_root=tmp_path,now_epoch=now)
    assert not ready
    assert any("coddoc_validation is not PASS" in reason for reason in reasons)
    assert any("artifact is missing" in reason for reason in reasons)

def test_exact_signed_artifact_review_passes_with_external_registry_pin(tmp_path,monkeypatch):
    record,_,now=_approved_record(tmp_path,monkeypatch)
    ready,reasons=readiness_result(record,repository_root=tmp_path,now_epoch=now)
    assert ready,reasons

def test_tampered_artifact_and_wrong_scope_hold(tmp_path,monkeypatch):
    record,_,now=_approved_record(tmp_path,monkeypatch)
    (tmp_path/"artifact.md").write_text("changed after approval",encoding="utf-8")
    ready,reasons=readiness_result(record,repository_root=tmp_path,now_epoch=now)
    assert not ready and any("proposal digest" in reason for reason in reasons)
    (tmp_path/"artifact.md").write_text("reviewable artifact",encoding="utf-8")
    record["review"]["scope"]="different-scope"
    ready,reasons=readiness_result(record,repository_root=tmp_path,now_epoch=now)
    assert not ready and any("scope mismatch" in reason for reason in reasons)

def test_registry_pin_mismatch_and_revocation_hold(tmp_path,monkeypatch):
    record,registry_path,now=_approved_record(tmp_path,monkeypatch)
    registry=json.loads(registry_path.read_text(encoding="utf-8"))
    registry["revoked"]=["reviewer-fixture"]
    registry_bytes=(json.dumps(registry,sort_keys=True,separators=(",",":"))+"\n").encode("utf-8")
    registry_path.write_bytes(registry_bytes)
    ready,reasons=readiness_result(record,repository_root=tmp_path,now_epoch=now)
    assert not ready and any("digest does not match" in reason for reason in reasons)
    monkeypatch.setenv("ERIA_REVIEWER_REGISTRY_SHA256",hashlib.sha256(registry_bytes).hexdigest())
    ready,reasons=readiness_result(record,repository_root=tmp_path,now_epoch=now)
    assert not ready and any("revoked" in reason for reason in reasons)

def test_missing_external_registry_pin_means_hold(tmp_path,monkeypatch):
    record,_,now=_approved_record(tmp_path,monkeypatch)
    monkeypatch.delenv("ERIA_REVIEWER_REGISTRY_SHA256",raising=False)
    ready,reasons=readiness_result(record,repository_root=tmp_path,now_epoch=now)
    assert not ready and any("external reviewer registry digest pin is not configured" in reason for reason in reasons)

def test_live_financial_tier_never_becomes_ready(tmp_path,monkeypatch):
    record,_,now=_approved_record(tmp_path,monkeypatch,tier="LIVE_FINANCIAL")
    ready,reasons=readiness_result(record,repository_root=tmp_path,now_epoch=now)
    assert not ready and any("categorically excluded" in reason for reason in reasons)
