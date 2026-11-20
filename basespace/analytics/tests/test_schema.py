import sqlite3
import unittest
from pathlib import Path

SCHEMA = Path(__file__).parents[1] / "db" / "bs_analytics_schema.sql"

class AnalyticsSchemaTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.executescript(SCHEMA.read_text(encoding="utf-8"))

    def tearDown(self):
        self.db.close()

    def test_required_tables_exist(self):
        names = {row[0] for row in self.db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertTrue({"dataset", "source_record", "metric_definition", "analysis_run", "revision_event", "evidence_event", "approval_event"}.issubset(names))

    def test_source_record_is_append_only(self):
        self.db.execute("INSERT INTO dataset(dataset_id,title,source_uri,source_type,grain,status) VALUES(?,?,?,?,?,?)", ("DS-TEST", "Test", "file://test.csv", "CSV", "one row", "INGESTED"))
        self.db.execute("INSERT INTO source_record(source_record_id,dataset_id,source_key,source_payload_json,payload_sha256) VALUES(?,?,?,?,?)", ("SRC-1", "DS-TEST", "row-1", "{}", "a" * 64))
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("UPDATE source_record SET source_key='changed' WHERE source_record_id='SRC-1'")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("DELETE FROM source_record WHERE source_record_id='SRC-1'")

    def test_approval_records_bind_reviewer_and_scope(self):
        columns = {row[1] for row in self.db.execute("PRAGMA table_info(approval_event)")}
        self.assertTrue({"reviewer_login", "reviewer_identity_verified", "signature_verified", "scope", "expires_at", "revoked"}.issubset(columns))

if __name__ == "__main__":
    unittest.main()
