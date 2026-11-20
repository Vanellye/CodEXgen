import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from allowance import (
    AllowanceHold, AllowancePolicy, BalanceEvidence, BeneficiaryRequest,
    prepare_hybrid_allocation,
)


class AllowanceTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now(timezone.utc)
        self.policy = AllowancePolicy(
            "test-v1", "USD", 10000, 4000, 2500, 8000, 86400, 300,
            (self.now + timedelta(hours=1)).isoformat()
        )
        self.balance = BalanceEvidence(
            "wise", "acct-pseudo-1", "USD", 12000, 2000,
            self.now.isoformat(), True, "evidence:balance-001"
        )

    def test_pool_uses_verified_available_less_reserves_and_caps(self):
        result = prepare_hybrid_allocation(
            self.policy, [self.balance],
            [BeneficiaryRequest("ben-a", 5000, 3000),
             BeneficiaryRequest("ben-b", 5000, 3000)],
            now=self.now,
        )
        self.assertEqual(result["verified_available_after_reserves_minor"], 10000)
        self.assertEqual(result["proposed_total_minor"], 6000)
        self.assertEqual([x["proposed_minor"] for x in result["beneficiaries"]], [3000, 3000])
        self.assertFalse(result["live_submission_enabled"])

    def test_stale_balance_holds(self):
        stale = BalanceEvidence("wise", "acct", "USD", 10000, 0,
                                (self.now - timedelta(hours=1)).isoformat(),
                                True, "evidence:old")
        with self.assertRaises(AllowanceHold):
            prepare_hybrid_allocation(self.policy, [stale],
                [BeneficiaryRequest("ben-a", 1000, 1000)], now=self.now)

    def test_unverified_balance_holds(self):
        bad = BalanceEvidence("plaid", "acct", "USD", 10000, 0,
                              self.now.isoformat(), False, "evidence:unverified")
        with self.assertRaises(AllowanceHold):
            prepare_hybrid_allocation(self.policy, [bad],
                [BeneficiaryRequest("ben-a", 1000, 1000)], now=self.now)

    def test_existing_allocations_reduce_pool(self):
        result = prepare_hybrid_allocation(self.policy, [self.balance],
            [BeneficiaryRequest("ben-a", 5000, 4000)],
            already_allocated_minor=7000, now=self.now)
        self.assertEqual(result["proposed_total_minor"], 1000)

    def test_negative_reserve_rejected(self):
        bad = BalanceEvidence("wise", "acct", "USD", 10000, -1,
                              self.now.isoformat(), True, "evidence:bad")
        with self.assertRaises(AllowanceHold):
            prepare_hybrid_allocation(self.policy, [bad],
                [BeneficiaryRequest("ben-a", 1000, 1000)], now=self.now)


if __name__ == "__main__":
    unittest.main()
