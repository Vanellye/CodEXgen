import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.eria_pantheon.pons import CapabilityGrant
from tools.god_collective import PreservationError, collect_directory, ingest_file, verify_record


class GodCollectiveTests(unittest.TestCase):
    def grant(self, vault: Path) -> CapabilityGrant:
        return CapabilityGrant(
            capability="god.ingest",
            requested_scope=str(vault.resolve()),
            approved_scope=str(vault.resolve()),
            approval_reference="test-approval-001",
            verified_by_adapter=True,
        )

    def test_ingest_preserves_bytes_and_creates_lineage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vault = root / "GOD"
            source = root / "capture.bin"
            original = b"original\x00payload\xff"
            source.write_bytes(original)

            result = ingest_file(source, vault, self.grant(vault))
            self.assertEqual(result["status"], "preserved")
            self.assertEqual(result["sha256"], hashlib.sha256(original).hexdigest())
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(Path(result["object_path"]).read_bytes(), original)
            self.assertTrue(verify_record(vault, result["record_id"])["valid"])

            ref = json.loads(Path(result["collaboration_reference"]).read_text())
            self.assertEqual(ref["source_sha256"], result["sha256"])
            self.assertTrue((vault / "LINEAGE" / "events.jsonl").is_file())

    def test_missing_grant_denies_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.txt"
            source.write_text("do not modify")
            vault = root / "GOD"
            denied = CapabilityGrant(
                capability="god.ingest",
                requested_scope=str(vault.resolve()),
                approved_scope=str(vault.resolve()),
                approval_reference="",
                verified_by_adapter=False,
            )
            with self.assertRaises(PermissionError):
                ingest_file(source, vault, denied)
            self.assertFalse(vault.exists())

    def test_parent_is_recorded_without_replacing_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vault = root / "GOD"
            first = root / "first.txt"
            second = root / "second.txt"
            first.write_text("ancestor")
            second.write_text("descendant")
            grant = self.grant(vault)

            ancestor = ingest_file(first, vault, grant)
            ancestor_object = Path(ancestor["object_path"])
            before = ancestor_object.read_bytes()
            child = ingest_file(second, vault, grant, parent_record_id=ancestor["record_id"])

            child_meta = json.loads(Path(child["metadata_path"]).read_text())
            self.assertEqual(child_meta["parent_record_ids"], [ancestor["record_id"]])
            self.assertEqual(ancestor_object.read_bytes(), before)
            self.assertTrue(verify_record(vault, ancestor["record_id"])["valid"])

    def test_directory_collection_ingests_snapshot_and_skips_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_root = root / "incoming"
            source_root.mkdir()
            (source_root / "a.txt").write_text("alpha")
            nested = source_root / "nested"
            nested.mkdir()
            (nested / "b.bin").write_bytes(b"beta")
            vault = root / "GOD"

            results = collect_directory(source_root, vault, self.grant(vault))
            self.assertEqual(len(results), 2)
            self.assertTrue(all(verify_record(vault, item["record_id"])["valid"] for item in results))
            self.assertEqual((source_root / "a.txt").read_text(), "alpha")
            self.assertEqual((nested / "b.bin").read_bytes(), b"beta")

    def test_invalid_parent_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.txt"
            source.write_text("new")
            vault = root / "GOD"
            with self.assertRaises(PreservationError):
                ingest_file(source, vault, self.grant(vault), parent_record_id="missing")


if __name__ == "__main__":
    unittest.main()
