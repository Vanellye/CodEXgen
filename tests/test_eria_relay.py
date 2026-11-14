import json
import unittest
from tools.eria_pantheon.approval import sign_grant
from tools.eria_pantheon.relay import PonsRelayClient, RelayHold


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, size=-1): return self.payload[:size]


class RelayTests(unittest.TestCase):
    def setUp(self):
        self.key = "r" * 48
        payload = {
            "grant_id": "relay-grant-1", "capability": "eria.acquire",
            "scope": "storage/inbox/", "issued_at": 1000,
            "expires_at": 1500, "nonce": "relay-nonce-1",
        }
        self.grant = sign_grant(payload, self.key)
        self.calls = []
        def opener(request, timeout):
            self.calls.append((request, timeout))
            if request.full_url.endswith("/next"):
                return FakeResponse({"request_id": "req-1", "grant": self.grant})
            return FakeResponse({"status": "acknowledged"})
        self.opener = opener

    def test_https_poll_verifies_then_acknowledges(self):
        client = PonsRelayClient("https://relay.example", "t" * 32, self.key,
                                 opener=self.opener)
        seen = []
        result = client.poll_once(lambda grant: seen.append(grant) or {"state": "accepted"})
        self.assertEqual(result["status"], "processed")
        self.assertEqual(seen[0]["grant_id"], "relay-grant-1")
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(self.calls[0][0].get_method(), "GET")
        self.assertEqual(self.calls[1][0].get_method(), "POST")
        self.assertTrue(self.calls[0][0].get_header("Authorization").startswith("Bearer "))

    def test_rejects_plain_http(self):
        with self.assertRaises(RelayHold):
            PonsRelayClient("http://relay.example", "t" * 32, self.key)

    def test_rejects_invalid_token(self):
        with self.assertRaises(RelayHold):
            PonsRelayClient("https://relay.example", "short", self.key)

    def test_empty_queue_is_idle(self):
        client = PonsRelayClient("https://relay.example", "t" * 32, self.key,
                                 opener=lambda req, timeout: FakeResponse({"status": "empty"}))
        self.assertEqual(client.poll_once(lambda _: self.fail("must not call handler")),
                         {"status": "idle"})


if __name__ == "__main__":
    unittest.main()
