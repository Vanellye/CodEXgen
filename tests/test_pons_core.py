import hashlib
import tempfile
import unittest
from pathlib import Path

from pons import AnchorIdentity, Component, PONSRegistry


class PONSTests(unittest.TestCase):
    def test_anchor_is_frozen(self):
        anchor = AnchorIdentity()
        with self.assertRaises(Exception):
            anchor.ref_sha = "0" * 40

    def test_rejects_altered_anchor(self):
        with self.assertRaises(ValueError):
            PONSRegistry(anchor=AnchorIdentity(ref_sha="0" * 40))

    def test_provenance_match_and_mismatch(self):
        source = b"ERIA component source"
        expected = hashlib.sha256(source).hexdigest()
        registry = PONSRegistry()
        registry.register(Component("conversation", "commit-a", "tools/agent.py", expected, "manifest-v1"))
        self.assertEqual(registry.verify_provenance("conversation", source)["state"], "VERIFIED")
        self.assertEqual(registry.verify_provenance("conversation", b"changed")["state"], "HOLD")

    def test_missing_digest_is_unknown(self):
        registry = PONSRegistry()
        registry.register(Component("music", "commit-b", "music/engine.py"))
        self.assertEqual(registry.verify_provenance("music", b"audio")["state"], "UNKNOWN")

    def test_accuracy_cannot_be_self_declared(self):
        registry = PONSRegistry()
        registry.register(Component("stride", "commit-c", "stride.py"))
        with self.assertRaises(ValueError):
            registry.observe_status("stride", "ACCURATE")

    def test_ledger_chain_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            registry = PONSRegistry(str(path))
            registry.register(Component("pantheon", "commit-d", "pantheon.py"))
            registry.observe_status("pantheon", "READY", "process responsive")
            self.assertTrue(registry.verify_ledger()["valid"])
            rows = path.read_text().splitlines()
            path.write_text(rows[0] + "\n" + rows[1].replace("READY", "HOLD") + "\n")
            with self.assertRaises(ValueError):
                PONSRegistry(str(path))

    def test_status_report_keeps_anchor_identity(self):
        registry = PONSRegistry()
        registry.register(Component("filesystem", "commit-e", "filesystem.py"))
        report = registry.report()
        self.assertEqual(report["anchor"]["anchor_id"], "7f7a43a973a96a06dd432bf94843213d09133323")
        self.assertEqual(report["components"][0]["reported_state"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
