import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from eria_conversation_server import Store


class FakeRepository:
    def __init__(self, root):
        self.root = Path(root)

    def files(self):
        return ["src/sample.kt", ".env"]


class DashboardStoreTests(unittest.TestCase):
    def test_index_keeps_source_hash_and_skips_secret_names(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            root.mkdir()
            (root / "src").mkdir()
            original = b"package sample\n"
            (root / "src/sample.kt").write_bytes(original)
            (root / ".env").write_text("SHOULD_NOT_INDEX", encoding="utf-8")
            store = Store(Path(td) / "data.sqlite3")
            count = store.index_repository(FakeRepository(root))
            self.assertEqual(count, 1)
            records = store.provenance()
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["path"], "src/sample.kt")
            self.assertEqual(records[0]["source_sha256"], hashlib.sha256(original).hexdigest())

    def test_authorization_requests_always_start_on_hold(self):
        with tempfile.TemporaryDirectory() as td:
            store = Store(Path(td) / "data.sqlite3")
            request = store.create_pons_request("repository.write", "branch:feature/demo", "Need review")
            self.assertEqual(request["status"], "HOLD")
            self.assertFalse(request["approval_created"])
            self.assertEqual(store.pons_requests()[0]["request_id"], request["request_id"])

    def test_audit_events_are_append_only(self):
        with tempfile.TemporaryDirectory() as td:
            store = Store(Path(td) / "data.sqlite3")
            store.add_audit("test_event", "RECORDED", {"safe": True})
            self.assertEqual(store.audit_history()[0]["event"], "test_event")
            with store.connect() as db:
                with self.assertRaises(Exception):
                    db.execute("UPDATE audit_events SET status='CHANGED' WHERE id=1")
                with self.assertRaises(Exception):
                    db.execute("DELETE FROM audit_events WHERE id=1")


if __name__ == "__main__":
    unittest.main()
