import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from verify_evidence import verify

POLICY = json.loads((ROOT / "policy.json").read_text(encoding="utf-8"))
SHA = "a" * 40
MERGE_SHA = "b" * 40


def sample(action="deployment"):
    evidence = {
        "event_id": "evt-001",
        "status": "confirmed",
        "source_url": "https://github.com/example/repo/actions/runs/1",
        "observed_at": "2026-11-13T12:00:00Z",
        "issuer": "deployment-controller",
        "actor": "service-account",
    }
    approval = {
        "kind": "human",
        "approver_id": "reviewer-1",
        "approved_action": action,
        "approved_sha": SHA,
        "approved_at": "2026-11-13T11:00:00Z",
        "approval_ref": "https://github.com/example/repo/pull/1#review",
    }
    if action == "ci":
        evidence.update({"issuer": "github-actions", "conclusion": "success", "workflow_sha": SHA})
    elif action == "merge":
        evidence.update({"issuer": "github", "pr_merged": True, "merge_commit_sha": MERGE_SHA})
    elif action == "deployment":
        evidence.update({"deployment_status": "success", "deployed_sha": SHA, "environment": "staging"})
    elif action == "release":
        evidence.update({"issuer": "release-controller", "published": True, "release_tag": "v1.0.0"})
    elif action == "external_dispatch":
        evidence.update({"issuer": "github", "dispatch_id": "dispatch-1", "destination": "service://example"})
    elif action == "hardware_activation":
        evidence.update({"issuer": "device-attestor", "device_id": "device-1", "attestation_id": "attest-1"})
    elif action == "biological_intervention":
        evidence.update({"issuer": "ethics-review-authority", "protocol_id": "protocol-1",
                         "protocol_version": "1", "ethics_approval_id": "ethics-1",
                         "attestation_id": "attest-2"})
    record = {"schema_version": "1.0", "action_type": action, "subject_sha": SHA, "evidence": evidence}
    if action != "ci":
        record["approval"] = approval
    return record


class EvidenceGateTests(unittest.TestCase):
    def test_ci_exact_sha_passes_without_action(self):
        result = verify(sample("ci"), SHA, POLICY)
        self.assertTrue(result["accepted"])
        self.assertFalse(result["execution_performed"])

    def test_each_consequential_action_requires_complete_evidence(self):
        for action in ("merge", "deployment", "release", "external_dispatch",
                       "hardware_activation", "biological_intervention"):
            with self.subTest(action=action):
                self.assertTrue(verify(sample(action), SHA, POLICY)["accepted"])

    def test_missing_evidence_rejected(self):
        record = sample()
        del record["evidence"]["event_id"]
        with self.assertRaisesRegex(ValueError, "event_id"):
            verify(record, SHA, POLICY)

    def test_stale_subject_sha_rejected(self):
        with self.assertRaisesRegex(ValueError, "expected commit SHA"):
            verify(sample(), "c" * 40, POLICY)

    def test_untrusted_issuer_rejected(self):
        record = sample()
        record["evidence"]["issuer"] = "unknown-source"
        with self.assertRaisesRegex(ValueError, "trusted_issuers"):
            verify(record, SHA, POLICY)

    def test_non_https_source_rejected(self):
        record = sample()
        record["evidence"]["source_url"] = "http://example.test/event"
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            verify(record, SHA, POLICY)

    def test_failed_deployment_rejected(self):
        record = sample()
        record["evidence"]["deployment_status"] = "failed"
        with self.assertRaisesRegex(ValueError, "deployment_status"):
            verify(record, SHA, POLICY)

    def test_deployment_wrong_commit_rejected(self):
        record = sample()
        record["evidence"]["deployed_sha"] = "d" * 40
        with self.assertRaisesRegex(ValueError, "deployed_sha"):
            verify(record, SHA, POLICY)

    def test_missing_approval_rejected(self):
        record = sample()
        del record["approval"]
        with self.assertRaisesRegex(ValueError, "approval"):
            verify(record, SHA, POLICY)

    def test_automated_approval_rejected(self):
        record = sample()
        record["approval"]["kind"] = "bot"
        with self.assertRaisesRegex(ValueError, "must be human"):
            verify(record, SHA, POLICY)

    def test_wrong_action_approval_rejected(self):
        record = sample()
        record["approval"]["approved_action"] = "release"
        with self.assertRaisesRegex(ValueError, "exact action"):
            verify(record, SHA, POLICY)

    def test_wrong_sha_approval_rejected(self):
        record = sample()
        record["approval"]["approved_sha"] = "e" * 40
        with self.assertRaisesRegex(ValueError, "exact subject_sha"):
            verify(record, SHA, POLICY)

    def test_self_approval_rejected(self):
        record = sample()
        record["approval"]["approver_id"] = record["evidence"]["actor"]
        with self.assertRaisesRegex(ValueError, "distinct"):
            verify(record, SHA, POLICY)

    def test_biological_record_requires_ethics_reference(self):
        record = sample("biological_intervention")
        del record["evidence"]["ethics_approval_id"]
        with self.assertRaisesRegex(ValueError, "ethics_approval_id"):
            verify(record, SHA, POLICY)

    def test_unknown_action_rejected(self):
        record = sample()
        record["action_type"] = "execute_anything"
        with self.assertRaisesRegex(ValueError, "unsupported action_type"):
            verify(record, SHA, POLICY)


if __name__ == "__main__":
    unittest.main()
