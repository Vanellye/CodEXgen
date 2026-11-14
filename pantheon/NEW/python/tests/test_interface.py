import unittest

from eria_pantheon import ERIAPantheonInterface, PantheonError


class PantheonBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = ERIAPantheonInterface()

    def test_new_source_reported(self):
        result = self.api.build_narrative({
            "source_id": "public-dataset",
            "record_id": "record-001",
            "permission_basis": "public-use license",
            "purpose": "aggregate trend analysis",
            "captured_at": "2026-11-14T00:00:00Z",
            "provenance_digest": "sha256:test-digest",
            "content_summary": "An aggregate count increased.",
            "data_class": 1,
            "evidence_status": 1,
            "authorization_confirmed": True,
        })
        self.assertIn("SOURCE-REPORTED", result)
        self.assertIn("Proof reference: NONE", result)

    def test_new_rejects_unconfirmed_authorization(self):
        record = {
            "source_id": "public-dataset",
            "record_id": "record-002",
            "permission_basis": "public-use license",
            "purpose": "test",
            "captured_at": "2026-11-14T00:00:00Z",
            "provenance_digest": "sha256:test-digest",
            "content_summary": "Test statement.",
            "data_class": 1,
            "evidence_status": 1,
            "authorization_confirmed": False,
        }
        with self.assertRaisesRegex(PantheonError, "NOT_AUTHORIZED"):
            self.api.build_narrative(record)

    def test_facade_additive_correction(self):
        result = self.api.build_correction({
            "notice_id": "notice-01",
            "source_record_id": "record-original",
            "target_record_id": "record-followup",
            "evidence_reference": "evidence-01",
            "reason": "Add a linked public record.",
            "recorded_at": "2026-11-14T00:00:00Z",
            "reviewer_id": "reviewer-test",
            "relation": 2,
            "source_authorized": True,
            "link_verified": True,
        })
        self.assertIn("CORRECTS-PRIOR-NOTICE", result)
        self.assertIn("ADDITIVE LINK", result)

    def test_facade_rejects_unverified_link(self):
        correction = {
            "notice_id": "notice-02",
            "source_record_id": "record-original",
            "target_record_id": "record-followup",
            "evidence_reference": "evidence-02",
            "reason": "Test unverified link.",
            "recorded_at": "2026-11-14T00:00:00Z",
            "reviewer_id": "reviewer-test",
            "relation": 2,
            "source_authorized": True,
            "link_verified": False,
        }
        with self.assertRaisesRegex(PantheonError, "LINK_UNVERIFIED"):
            self.api.build_correction(correction)


if __name__ == "__main__":
    unittest.main()
