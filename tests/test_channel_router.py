"""Tests for the local permission-checked push/pull router."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))
from channel_router import LocalChannelRouter, PermissionDenied, RouterError


class LocalChannelRouterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "router.sqlite3"
        self.router = LocalChannelRouter(self.path)
        self.router.create_channel("realm-a", "owner")
        self.router.grant("realm-a", "owner", "alice", can_publish=True)
        self.router.grant("realm-a", "owner", "bob", can_read=True)

    def test_push_delivers_to_authorized_pull_reader(self):
        event = self.router.push("realm-a", "alice", "message", {"text": "hello"},
                                 idempotency_key="m-1")
        received = self.router.pull("realm-a", "bob")
        self.assertEqual([item.event_id for item in received], [event])
        self.assertEqual(received[0].payload["text"], "hello")
        self.assertEqual(self.router.delivery_state(event, "bob"), "delivered")

    def test_unauthorized_push_and_pull_are_rejected(self):
        with self.assertRaises(PermissionDenied):
            self.router.push("realm-a", "bob", "message", {}, idempotency_key="x")
        with self.assertRaises(PermissionDenied):
            self.router.pull("realm-a", "intruder")

    def test_idempotency_prevents_duplicate_event(self):
        first = self.router.push("realm-a", "alice", "message", {"v": 1},
                                 idempotency_key="same")
        second = self.router.push("realm-a", "alice", "message", {"v": 1},
                                  idempotency_key="same")
        self.assertEqual(first, second)
        self.assertEqual(len(self.router.history("realm-a")), 1)
        with self.assertRaises(RouterError):
            self.router.push("realm-a", "alice", "message", {"v": 2},
                             idempotency_key="same")

    def test_consequential_event_requires_explicit_acceptance(self):
        event = self.router.push("realm-a", "alice", "action-request", {"action": "open-gate"},
                                 idempotency_key="gate-1", requires_acceptance=True)
        self.router.pull("realm-a", "bob")
        self.assertEqual(self.router.delivery_state(event, "bob"), "delivered")
        self.router.decide(event, "bob", accept=True)
        self.assertEqual(self.router.delivery_state(event, "bob"), "accepted")

    def test_decline_is_not_receipt_or_acceptance(self):
        event = self.router.push("realm-a", "alice", "action-request", {},
                                 idempotency_key="decline-1", requires_acceptance=True)
        self.router.pull("realm-a", "bob")
        self.router.decide(event, "bob", accept=False)
        self.assertEqual(self.router.delivery_state(event, "bob"), "declined")

    def test_revocation_stops_future_pull_and_marks_pending_delivery(self):
        event = self.router.push("realm-a", "alice", "message", {},
                                 idempotency_key="revoke-1")
        self.router.revoke("realm-a", "owner", "bob")
        self.assertEqual(self.router.delivery_state(event, "bob"), "revoked")
        with self.assertRaises(PermissionDenied):
            self.router.pull("realm-a", "bob")

    def test_recovery_reopens_database_and_preserves_events(self):
        event = self.router.push("realm-a", "alice", "message", {"safe": True},
                                 idempotency_key="recover-1")
        recovered = LocalChannelRouter(self.path)
        pulled = recovered.pull("realm-a", "bob")
        self.assertEqual([item.event_id for item in pulled], [event])
        self.assertEqual(recovered.delivery_state(event, "bob"), "delivered")

    def test_revocation_after_delivery_prevents_later_acceptance(self):
        event = self.router.push("realm-a", "alice", "action-request", {},
                                 idempotency_key="late-revoke", requires_acceptance=True)
        self.router.pull("realm-a", "bob")
        self.router.revoke("realm-a", "owner", "bob")
        self.assertEqual(self.router.delivery_state(event, "bob"), "revoked")
        with self.assertRaises(RouterError):
            self.router.decide(event, "bob", accept=True)

    def test_only_owner_can_grant_or_revoke(self):
        with self.assertRaises(PermissionDenied):
            self.router.grant("realm-a", "alice", "mallory", can_read=True)
        with self.assertRaises(PermissionDenied):
            self.router.revoke("realm-a", "alice", "bob")

    def test_pull_limit_is_bounded(self):
        with self.assertRaises(RouterError):
            self.router.pull("realm-a", "bob", limit=501)


if __name__ == "__main__":
    unittest.main()
