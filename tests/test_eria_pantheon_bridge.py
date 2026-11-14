import hashlib
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from eria_pantheon.pons import (
    BridgeEnvelope, CapabilityGrant, Decision, Lifetime, Pons,
)
from eria_pantheon.interface import ERIAPantheonInterface


class FakeRepository:
    def __init__(self, root):
        self.root = Path(root)

    def ask(self, question):
        return "ASKED:" + question


class PonsTests(unittest.TestCase):
    def test_singleton_and_transient_lifetimes(self):
        class Service:
            pass
        pons = Pons()
        pons.register(Service, Service, lifetime=Lifetime.SINGLETON)
        self.assertIs(pons.resolve(Service), pons.resolve(Service))

        class Transient:
            pass
        pons.register(Transient, Transient)
        self.assertIsNot(pons.resolve(Transient), pons.resolve(Transient))

    def test_missing_or_unverified_grant_holds(self):
        self.assertEqual(Pons.authorize(None, "transmit", "host"), Decision.HOLD)
        grant = CapabilityGrant("transmit", "host", "host", "approval-1", False)
        self.assertEqual(Pons.authorize(grant, "transmit", "host"), Decision.HOLD)

    def test_exact_scope_is_proposal_only_not_execution(self):
        grant = CapabilityGrant("transmit", "host", "host", "approval-1", True)
        self.assertEqual(
            Pons.authorize(grant, "transmit", "host"), Decision.PROPOSAL_ONLY
        )
        self.assertFalse(Pons.describe()["transmission_enabled"])

    def test_derived_record_never_promotes_authority(self):
        source = b"source"
        envelope = BridgeEnvelope.from_bytes(source, "a.py")
        derived = envelope.with_derived(b"translation", "translate/v1")
        self.assertEqual(envelope.source_sha256, hashlib.sha256(source).hexdigest())
        self.assertEqual(derived.source_sha256, envelope.source_sha256)
        self.assertEqual(derived.source_authority, "NON_AUTHORITATIVE")
        self.assertEqual(derived.derived_authority, "NON_AUTHORITATIVE")

    def test_code_bypass_preserves_bytes_and_audits_outside_repo(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root, home = base / "repo", base / "audit-home"
            root.mkdir()
            home.mkdir()
            original = b"print('unchanged')\n"
            (root / "sample.py").write_bytes(original)
            interface = ERIAPantheonInterface(FakeRepository(root))
            old_home = os.environ.get("HOME")
            os.environ["HOME"] = str(home)
            try:
                result = interface.handle(
                    'code.bypass sample.py --reason "preserve source"'
                )
            finally:
                if old_home is None:
                    os.environ.pop("HOME", None)
                else:
                    os.environ["HOME"] = old_home
            self.assertIn("bypassed_local_not_transmitted", result)
            self.assertIn("translator_invoked: false", result)
            self.assertIn("transmitter_invoked: false", result)
            self.assertEqual((root / "sample.py").read_bytes(), original)
            self.assertTrue(
                (home / ".eria/audit/ttt_code_bypass.jsonl").is_file()
            )
            self.assertFalse((root / ".eria").exists())

    def test_path_escape_is_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            interface = ERIAPantheonInterface(FakeRepository(td))
            result = interface.handle(
                'code.bypass ../outside.py --reason "test"'
            )
            self.assertIn("escapes repository root", result)

    def test_conversation_engine_dispatches_integration_command(self):
        from eria_repository_conversation import Conversation
        with tempfile.TemporaryDirectory() as td:
            output = Conversation(FakeRepository(td)).ask("integration.status")
            self.assertIn("conversation_engine: connected", output)
            self.assertIn("source_authority: NON_AUTHORITATIVE", output)


if __name__ == "__main__":
    unittest.main()
