import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from allowance import (
    AllowanceHold, AllowancePolicy, BalanceEvidence, BeneficiaryRequest,
    prepare_hybrid_allocation, approve_allocation_proposal,
)
from schedule import ScheduledAllowance, ScheduleHold, prepare_due_occurrence


class AllowanceTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now(timezone.utc)
        self.policy = AllowancePolicy(
            "test-v1", "USD", 10000, 4000, 2500, 8000, 86400, 300,
            (self.now + timedelta(hours=1)).isoformat())
        self.balance = BalanceEvidence(
            "wise", "acct-pseudo-1", "USD", 12000, 2000,
            self.now.isoformat(), True, "evidence:balance-001", "funding-source-001")

    def test_pool_uses_verified_available_less_reserves_and_caps(self):
        result = prepare_hybrid_allocation(self.policy, [self.balance],
            [BeneficiaryRequest("ben-a", 5000, 3000), BeneficiaryRequest("ben-b", 5000, 3000)], now=self.now)
        self.assertEqual(result["verified_available_after_reserves_minor"], 10000)
        self.assertEqual(result["proposed_total_minor"], 5000)
        self.assertEqual([x["proposed_minor"] for x in result["beneficiaries"]], [2500, 2500])
        self.assertFalse(result["live_submission_enabled"])

    def test_stale_balance_holds(self):
        stale = BalanceEvidence("wise", "acct", "USD", 10000, 0,
            (self.now - timedelta(hours=1)).isoformat(), True, "evidence:old", "source-old")
        with self.assertRaises(AllowanceHold):
            prepare_hybrid_allocation(self.policy, [stale], [BeneficiaryRequest("ben-a", 1000, 1000)], now=self.now)

    def test_unverified_balance_holds(self):
        bad = BalanceEvidence("plaid", "acct", "USD", 10000, 0,
            self.now.isoformat(), False, "evidence:unverified", "source-unverified")
        with self.assertRaises(AllowanceHold):
            prepare_hybrid_allocation(self.policy, [bad], [BeneficiaryRequest("ben-a", 1000, 1000)], now=self.now)

    def test_existing_allocations_reduce_pool(self):
        result = prepare_hybrid_allocation(self.policy, [self.balance],
            [BeneficiaryRequest("ben-a", 5000, 4000)], already_allocated_minor=7000, now=self.now)
        self.assertEqual(result["proposed_total_minor"], 1000)

    def test_negative_reserve_rejected(self):
        bad = BalanceEvidence("wise", "acct", "USD", 10000, -1,
            self.now.isoformat(), True, "evidence:bad", "source-bad")
        with self.assertRaises(AllowanceHold):
            prepare_hybrid_allocation(self.policy, [bad], [BeneficiaryRequest("ben-a", 1000, 1000)], now=self.now)

    def test_same_underlying_funds_across_providers_not_double_counted(self):
        plaid = BalanceEvidence("plaid", "plaid-acct", "USD", 12000, 2000,
            self.now.isoformat(), True, "evidence:plaid", "funding-source-001")
        with self.assertRaises(AllowanceHold):
            prepare_hybrid_allocation(self.policy, [self.balance, plaid],
                [BeneficiaryRequest("ben-a", 1000, 1000)], now=self.now)

    def test_allocation_requires_exact_independent_approval(self):
        proposal = prepare_hybrid_allocation(self.policy, [self.balance],
            [BeneficiaryRequest("ben-a", 1000, 1000)], now=self.now)
        artifact = {"intent_sha256": proposal["proposal_sha256"], "policy_version": "test-v1",
                    "reviewer_id": "independent-reviewer"}
        approved = approve_allocation_proposal(proposal, artifact, lambda p, a: True)
        self.assertEqual(approved["approval_status"], "INDEPENDENTLY_VERIFIED")
        self.assertFalse(approved["live_submission_enabled"])
        with self.assertRaises(AllowanceHold):
            approve_allocation_proposal(proposal, dict(artifact, intent_sha256="0"*64), lambda p, a: True)
        with self.assertRaises(AllowanceHold):
            approve_allocation_proposal(proposal, artifact, None)

    def test_scheduled_occurrence_only_prepares_when_due(self):
        plan = ScheduledAllowance("schedule-1", 86400, (self.now-timedelta(days=1)).isoformat(),
                                  (self.now+timedelta(days=2)).isoformat(), self.policy)
        result = prepare_due_occurrence(plan, 1, [self.balance],
            [BeneficiaryRequest("ben-a", 1000, 1000)], now=self.now)
        self.assertEqual(result["status"], "SCHEDULED_PROPOSAL_AWAITING_INDEPENDENT_APPROVAL")
        self.assertFalse(result["live_submission_enabled"])

    def test_future_occurrence_holds(self):
        plan = ScheduledAllowance("schedule-1", 86400, (self.now+timedelta(days=1)).isoformat(),
                                  (self.now+timedelta(days=3)).isoformat(), self.policy)
        with self.assertRaises(ScheduleHold):
            prepare_due_occurrence(plan, 0, [self.balance],
                [BeneficiaryRequest("ben-a", 1000, 1000)], now=self.now)


if __name__ == "__main__":
    unittest.main()


class CrossProviderBridgeTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now(timezone.utc)
        self.policy = AllowancePolicy("test-v1", "USD", 10000, 4000, 2500, 8000, 86400, 300,
            (self.now + timedelta(hours=1)).isoformat())
        self.balance = BalanceEvidence("wise_platform", "acct-pseudo-1", "USD", 12000, 2000,
            self.now.isoformat(), True, "evidence:balance-001", "funding-source-001")
    def test_bridge_requires_provider_auth_and_permission(self):
        from bridge import ProviderConnectionEvidence, prepare_cross_provider_allowance
        connection = ProviderConnectionEvidence("wise_platform", True, True, True,
            frozenset({"IBAN_SEPA"}), "evidence:wise-connection")
        result = prepare_cross_provider_allowance(self.policy, [connection], [self.balance],
            [BeneficiaryRequest("ben-a", 1000, 1000)], now=self.now)
        self.assertEqual(result["provider_set"], ["wise_platform"])
        self.assertEqual(result["status"], "CROSS_PROVIDER_PROPOSAL_AWAITING_INDEPENDENT_APPROVAL")
        self.assertFalse(result["live_submission_enabled"])

    def test_bridge_rejects_missing_provider_permissions(self):
        from bridge import ProviderConnectionEvidence, prepare_cross_provider_allowance
        connection = ProviderConnectionEvidence("wise_platform", True, True, False,
            frozenset({"IBAN_SEPA"}), "evidence:wise-connection")
        with self.assertRaises(AllowanceHold):
            prepare_cross_provider_allowance(self.policy, [connection], [self.balance],
                [BeneficiaryRequest("ben-a", 1000, 1000)], now=self.now)
