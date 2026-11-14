import hashlib
import json
import tempfile
import unittest
import uuid
from pathlib import Path

from tools.eria_pantheon.pons import CapabilityGrant
from tools.god_collective import PreservationError, ingest_file, verify_record
from tools.god_parent_validation import ParentValidationError, validate_parent_chain


class GodParentValidationTests(unittest.TestCase):
    def grant(self, vault: Path) -> CapabilityGrant:
        scope = str(vault.resolve())
        return CapabilityGrant(
            capability="god.ingest",
            requested_scope=scope,
            approved_scope=scope,
            approval_reference="test-parent-validation",
            verified_by_adapter=True,
        )

    def capture(self, root: Path, vault: Path, name: str, body: bytes,
                parent_ids=None):
        source = root / name
        source.write_bytes(body)
        return ingest_file(
            source, vault, self.grant(vault), parent_record_ids=parent_ids
        )

    def metadata(self, vault: Path, record_id: str) -> tuple[Path, dict]:
        path = vault / "SOURCE_PROVENANCE" / "records" / f"{record_id}.json"
        return path, json.loads(path.read_text(encoding="utf-8"))

    def save_metadata(self, path: Path, record: dict) -> None:
        path.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n",
                        encoding="utf-8")

    def test_multiple_parents_are_validated_and_their_hashes_are_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vault = root / "GOD"
            left = self.capture(root, vault, "left.bin", b"left-original")
            right = self.capture(root, vault, "right.bin", b"right-original")
            child = self.capture(
                root, vault, "combined.bin", b"combined-original",
                [left["record_id"], right["record_id"]],
            )
            _, metadata = self.metadata(vault, child["record_id"])
            self.assertEqual(metadata["parent_record_ids"],
                             [left["record_id"], right["record_id"]])
            self.assertEqual(
                [item["record_id"] for item in metadata["validated_parents"]],
                [left["record_id"], right["record_id"]],
            )
            self.assertEqual(
                [item["sha256"] for item in metadata["validated_parents"]],
                [left["sha256"], right["sha256"]],
            )
            self.assertTrue(verify_record(vault, child["record_id"])["valid"])

    def test_corrupt_parent_object_blocks_child_ingestion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vault = root / "GOD"
            parent = self.capture(root, vault, "parent.bin", b"ancestor")
            object_path = Path(parent["object_path"])
            object_path.write_bytes(b"tampered")
            with self.assertRaises(PreservationError):
                self.capture(root, vault, "child.bin", b"descendant",
                             [parent["record_id"]])

    def test_embedded_parent_id_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vault = root / "GOD"
            parent = self.capture(root, vault, "parent.bin", b"ancestor")
            path, record = self.metadata(vault, parent["record_id"])
            record["record_id"] = str(uuid.uuid4())
            self.save_metadata(path, record)
            with self.assertRaises(PreservationError):
                self.capture(root, vault, "child.bin", b"descendant",
                             [parent["record_id"]])

    def test_missing_ancestor_is_rejected_recursively(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vault = root / "GOD"
            parent = self.capture(root, vault, "parent.bin", b"ancestor")
            path, record = self.metadata(vault, parent["record_id"])
            record["parent_record_ids"] = [str(uuid.uuid4())]
            record["validated_parents"] = []
            self.save_metadata(path, record)
            with self.assertRaises(ParentValidationError):
                validate_parent_chain(vault, [parent["record_id"]])

    def test_ancestry_cycle_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vault = root / "GOD"
            first = self.capture(root, vault, "first.bin", b"first")
            second = self.capture(root, vault, "second.bin", b"second")
            first_path, first_record = self.metadata(vault, first["record_id"])
            second_path, second_record = self.metadata(vault, second["record_id"])
            first_record["parent_record_ids"] = [second["record_id"]]
            second_record["parent_record_ids"] = [first["record_id"]]
            self.save_metadata(first_path, first_record)
            self.save_metadata(second_path, second_record)
            with self.assertRaises(ParentValidationError):
                validate_parent_chain(vault, [first["record_id"]])

    def test_duplicate_parent_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vault = root / "GOD"
            parent = self.capture(root, vault, "parent.bin", b"ancestor")
            with self.assertRaises(PreservationError):
                self.capture(root, vault, "child.bin", b"descendant",
                             [parent["record_id"], parent["record_id"]])

    def test_object_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vault = root / "GOD"
            parent = self.capture(root, vault, "parent.bin", b"ancestor")
            path, record = self.metadata(vault, parent["record_id"])
            record["object_relative_path"] = "../../outside"
            self.save_metadata(path, record)
            with self.assertRaises(ParentValidationError):
                validate_parent_chain(vault, [parent["record_id"]])


if __name__ == "__main__":
    unittest.main()
