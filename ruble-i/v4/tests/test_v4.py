import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from coordinator import (BoundedPolicy, HistoricalTransfer, HoldTransfer,
                         LiveExecutionDisabled, TransferIntent,
                         prepare_transfer, submit_live_transfer,
                         verify_independent_approval)
from adapters import WisePlatformAdapter, PlaidTransferAdapter


NOW = datetime(2026, 11, 20, 12, 0, tzinfo=timezone.utc)
INTENT = TransferIntent(
    intent_id="tx-00000001", source_account_ref="vault-src-001",
    beneficiary_id="beneficiary-001", provider="wise_platform",
    rail="IBAN_SEPA", asset="EUR", amount_minor=2500,
    fee_limit_minor=100, idempotency_key="idem-key-000000000001",
    purpose="test fixture", created_at="2026-11-20T11:00:00Z",
    expires_at="2026-11-20T13:00:00Z",
)
POLICY = BoundedPolicy(
    version="v4.0.0", expires_at="2026-12-01T00:00:00Z",
    allowed_providers=frozenset({"wise_platform", "plaid_transfer"}),
    allowed_rails=frozenset({"IBAN_SEPA", "ACH"}),
    allowed_assets=frozenset({"EUR", "USD"}),
    allowed_beneficiary_ids=frozenset({"beneficiary-001"}),
    per_transfer_max_minor=10000, rolling_24h_max_minor=20000,
    per_beneficiary_rolling_24h_max_minor=5000, max_fee_minor=200,
)


class V4Tests(unittest.TestCase):
    def test_prepare_only_wise(self):
        result = prepare_transfer(INTENT, POLICY, now=NOW)
        self.assertEqual(result["status"], "PREPARED")
        self.assertFalse(result["live_submission_enabled"])

    def test_aggregate_cap(self):
        history = [HistoricalTransfer("beneficiary-001", "EUR", 3000,
                                      "2026-11-20T10:00:00Z")]
        with self.assertRaises(HoldTransfer):
            prepare_transfer(INTENT, POLICY, history, now=NOW)

    def test_unknown_beneficiary_denied(self):
        bad = TransferIntent(**{**INTENT.__dict__, "beneficiary_id":"unknown"})
        with self.assertRaises(HoldTransfer):
            prepare_transfer(bad, POLICY, now=NOW)

    def test_unconfigured_limits_fail_closed(self):
        bad_policy = BoundedPolicy(**{**POLICY.__dict__, "configured":False})
        with self.assertRaises(HoldTransfer):
            prepare_transfer(INTENT, bad_policy, now=NOW)

    def test_exact_scope_approval_required(self):
        prepared = prepare_transfer(INTENT, POLICY, now=NOW)
        artifact = {"intent_sha256":prepared["intent_sha256"],
                    "policy_version":"v4.0.0", "reviewer_id":"independent-reviewer"}
        verified = verify_independent_approval(prepared, artifact,
                                               lambda p, a: True)
        self.assertEqual(verified["approval_status"], "INDEPENDENTLY_VERIFIED")
        altered = dict(artifact, intent_sha256="0"*64)
        with self.assertRaises(HoldTransfer):
            verify_independent_approval(prepared, altered, lambda p, a: True)

    def test_missing_or_rejecting_verifier_holds(self):
        prepared = prepare_transfer(INTENT, POLICY, now=NOW)
        artifact = {"intent_sha256":prepared["intent_sha256"],
                    "policy_version":"v4.0.0", "reviewer_id":"independent-reviewer"}
        with self.assertRaises(HoldTransfer):
            verify_independent_approval(prepared, artifact, None)
        with self.assertRaises(HoldTransfer):
            verify_independent_approval(prepared, artifact, lambda p, a: False)

    def test_provider_adapters_prepare_but_never_submit(self):
        wise = WisePlatformAdapter().prepare(
            beneficiary_ref="wise-recipient-ref", rail="IBAN_SEPA",
            asset="EUR", amount_minor=2500, intent_sha256=INTENT.digest())
        plaid = PlaidTransferAdapter().prepare(
            beneficiary_ref="plaid-recipient-ref", rail="ACH",
            asset="USD", amount_minor=2500, intent_sha256=INTENT.digest())
        self.assertEqual(wise.mode, "PREPARE_ONLY")
        self.assertEqual(plaid.provider, "plaid_transfer")
        with self.assertRaises(LiveExecutionDisabled):
            WisePlatformAdapter().submit(wise)

    def test_global_live_submission_is_disabled(self):
        with self.assertRaises(LiveExecutionDisabled):
            submit_live_transfer(INTENT)


if __name__ == "__main__":
    unittest.main()
