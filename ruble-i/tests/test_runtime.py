import sys
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from runtime import Ledger, RubleError, parse, stamp

ROOT = Path(__file__).resolve().parents[1]

class RubleRuntimeTests(unittest.TestCase):
    def test_example_is_deterministic_and_hash_chained(self):
        source = ROOT / "examples" / "allowance-and-exchange.rubi"
        first = Ledger().execute(parse(source), stamp("2026-11-20T10:30:00Z"))
        second = Ledger().execute(parse(source), stamp("2026-11-20T10:30:00Z"))
        self.assertEqual(first, second)
        self.assertEqual(first["accounts"]["reserve-usd"]["balance"], 235000)
        self.assertEqual(first["accounts"]["hourly-allowance-usd"]["balance"], 3750)
        self.assertEqual(first["accounts"]["ration-spend-usd"]["balance"], 1250)
        self.assertEqual(first["accounts"]["travel-eur"]["balance"], 9200)
        self.assertEqual(len(first["events"]), 5)
        self.assertEqual(first["events"][-1]["previous_hash"], first["events"][-2]["hash"])

    def test_transfer_rejects_insufficient_funds(self):
        ledger = Ledger()
        ledger.account("a", "USD", "100")
        ledger.account("b", "USD", "0")
        with self.assertRaisesRegex(RubleError, "insufficient_funds"):
            ledger.move("tx-1", "a", "b", "101", "USD", "TRANSFER", {})
        self.assertEqual(ledger.accounts["a"]["balance"], 100)

    def test_transfer_rejects_asset_mismatch(self):
        ledger = Ledger()
        ledger.account("a", "USD", "100")
        ledger.account("b", "EUR", "0")
        with self.assertRaisesRegex(RubleError, "asset_mismatch"):
            ledger.move("tx-2", "a", "b", "10", "USD", "TRANSFER", {})

    def test_duplicate_event_id_is_rejected(self):
        ledger = Ledger()
        ledger.event("NOTE", "same-id", {})
        with self.assertRaisesRegex(RubleError, "duplicate_event_id"):
            ledger.event("NOTE", "same-id", {})

    def test_naive_timestamp_is_rejected(self):
        with self.assertRaisesRegex(RubleError, "timestamp_must_include_timezone"):
            stamp("2026-11-20T10:00:00")

if __name__ == "__main__":
    unittest.main()
