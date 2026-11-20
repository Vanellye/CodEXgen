import json
from pathlib import Path
from gamma_ops.coddoc import load_coddoc, ordered_events, validate_document
from gamma_ops.readiness import readiness_result

ROOT = Path(__file__).parents[1]
SAMPLE = ROOT / "events" / "TRUE-LIGHTWORK-WAVE-MAVEN.coddoc"

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

def test_operable_is_not_ready_without_all_gates(tmp_path):
    record = {
        "operable_id": "demo",
        "readiness_state": "READY_TO_OPEN",
        "execution_tier": "READ_ONLY",
        "live_execution_enabled": False,
        "checks": {"python_tests": "PASS", "arm64_compile": "PASS", "inventory": "PASS"},
        "review": {"state": "APPROVED", "reviewer_identity_verified": True, "review_ref": "review:1"},
        "source_ref": "commit:abc",
        "artifact_path": "artifact.md",
    }
    ready, reasons = readiness_result(record, repository_root=tmp_path)
    assert not ready
    assert any("coddoc_validation is not PASS" in reason for reason in reasons)
    assert any("artifact does not exist" in reason for reason in reasons)

def test_live_financial_tier_never_becomes_ready_here(tmp_path):
    artifact = tmp_path / "artifact.md"
    artifact.write_text("reviewable", encoding="utf-8")
    record = {
        "operable_id": "trader", "readiness_state": "READY_TO_OPEN",
        "execution_tier": "LIVE_FINANCIAL", "live_execution_enabled": False,
        "checks": {key: "PASS" for key in ("python_tests", "arm64_compile", "inventory", "coddoc_validation")},
        "review": {"state": "APPROVED", "reviewer_identity_verified": True, "review_ref": "review:1"},
        "source_ref": "commit:abc", "artifact_path": "artifact.md",
    }
    ready, reasons = readiness_result(record, repository_root=tmp_path)
    assert not ready
    assert any("categorically excluded" in reason for reason in reasons)
