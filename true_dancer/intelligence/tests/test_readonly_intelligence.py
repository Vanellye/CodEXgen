import hashlib
import unittest

from true_dancer.intelligence.avs import AvsValidator
from true_dancer.intelligence.contracts import EvidenceRecord, ReadGrant
from true_dancer.intelligence.pons import PonsAuthorizer
from true_dancer.intelligence.postgres_readonly import PostgresReadOnlyStore, ReadOnlyQueryDenied


NOW = 1_800_000_000
REV = "synthetic-commit-sha"


def grant(**overrides):
    fields = dict(reviewer_id="independent-reviewer", approval_ref="PONS-TEST-1",
                  scope="intelligence:shop_daily_sales:read", issued_at=NOW-10,
                  expires_at=NOW+600, source_revision=REV, nonce="nonce-1",
                  revoked=False, signature="valid-test-signature")
    fields.update(overrides)
    return ReadGrant(**fields)


class FakeCursor:
    description = (("business_date",), ("gross_sales",), ("order_count",))
    def fetchall(self):
        return [("2026-11-20", "100.00", 2)]


class FakeConnection:
    def __init__(self): self.calls=[]; self.rolled_back=False; self.closed=False
    def execute(self, sql, params=None):
        self.calls.append((sql, params))
        return FakeCursor()
    def rollback(self): self.rolled_back=True
    def close(self): self.closed=True


class ReadOnlyIntelligenceTests(unittest.TestCase):
    def setUp(self):
        self.conn = FakeConnection()
        self.pons = PonsAuthorizer(lambda g: g.signature == "valid-test-signature")
        self.avs = AvsValidator(lambda e: e.source == "postgresql")
        self.store = PostgresReadOnlyStore("postgresql://synthetic", self.pons, self.avs,
                                           connection_factory=lambda dsn: self.conn)

    def test_authorized_read_sets_transaction_read_only_and_rolls_back(self):
        snap = self.store.read("shop_daily_sales", ("2026-11-01", 30), grant=grant(),
                               source_revision=REV, now=NOW)
        self.assertEqual(len(snap.rows), 1)
        self.assertEqual(snap.rows[0]["order_count"], 2)
        self.assertEqual(self.conn.calls[0][0], "SET TRANSACTION READ ONLY")
        self.assertTrue(self.conn.rolled_back and self.conn.closed)
        self.assertEqual(snap.evidence.source_revision, REV)

    def test_missing_or_invalid_pons_grant_blocks_before_connect(self):
        called=[]
        store=PostgresReadOnlyStore("dsn", self.pons, self.avs,
                                    connection_factory=lambda dsn: called.append(dsn))
        with self.assertRaises(ReadOnlyQueryDenied):
            store.read("shop_daily_sales", ("2026-11-01", 30), grant=grant(revoked=True),
                       source_revision=REV, now=NOW)
        self.assertEqual(called, [])

    def test_unallowlisted_query_rejected(self):
        with self.assertRaisesRegex(ReadOnlyQueryDenied, "query_not_allowlisted"):
            self.store.read("arbitrary_sql", (), grant=grant(), source_revision=REV, now=NOW)

    def test_source_sha_mismatch_denied(self):
        with self.assertRaisesRegex(ReadOnlyQueryDenied, "source_revision_mismatch"):
            self.store.read("shop_daily_sales", ("2026-11-01", 30),
                            grant=grant(source_revision="other-sha"),
                            source_revision=REV, now=NOW)

    def test_avs_rejects_digest_tampering(self):
        payload=b"original"
        evidence=EvidenceRecord("e1", "fixture", REV, NOW,
                                hashlib.sha256(b"tampered").hexdigest(), "fixture:e1", payload)
        result=AvsValidator(lambda e: True).validate(evidence, expected_revision=REV, now=NOW)
        self.assertFalse(result.valid)
        self.assertEqual(result.status, "payload_digest_mismatch")

    def test_avs_rejects_missing_attestation(self):
        payload=b"evidence"
        evidence=EvidenceRecord("e2", "fixture", REV, NOW,
                                hashlib.sha256(payload).hexdigest(), "fixture:e2", payload)
        result=AvsValidator(lambda e: False).validate(evidence, expected_revision=REV, now=NOW)
        self.assertFalse(result.valid)
        self.assertEqual(result.status, "independent_attestation_failed")


if __name__ == "__main__": unittest.main()
