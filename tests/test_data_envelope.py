import hashlib
import json
import unittest

from codexgen_contracts.envelope import (
    EnvelopeError, canonical_json_bytes, record_digest, validate_record,
)


def valid_record():
    return {
        "record_id": "sensor.sample-001",
        "schema_version": 1,
        "source": "device.sensor-a",
        "observed_at": "2026-11-09T19:00:00-06:00",
        "monotonic_time": {"value": 123456, "clock_domain": "device.boot-7"},
        "payload": {"reading": 0, "enabled": False, "note": None, "values": [1, 2.5]},
        "units": {"reading": "milli-unit"},
        "quality": "VALID",
        "provenance": {
            "source_ref": "refs/heads/main",
            "source_digest": "a" * 64,
            "signature_status": "unverified",
        },
        "transformations": [
            {"operation": "normalize", "version": "1.0"}
        ],
        "authorization": {
            "status": "not_authorized", "scope": [], "approval_ref": None
        },
        "validation": {"status": "pending", "tests": []},
        "retention": {"class": "local", "policy": "review-required"},
    }


class EnvelopeTests(unittest.TestCase):
    def test_valid_record_preserves_zero_false_null_and_units(self):
        record = valid_record()
        validated = validate_record(record)
        self.assertEqual(validated["payload"]["reading"], 0)
        self.assertIs(validated["payload"]["enabled"], False)
        self.assertIsNone(validated["payload"]["note"])
        self.assertEqual(validated["units"]["reading"], "milli-unit")

    def test_canonical_bytes_and_digest_are_deterministic(self):
        record = valid_record()
        first = canonical_json_bytes(record)
        second = canonical_json_bytes(dict(reversed(list(record.items()))))
        self.assertEqual(first, second)
        self.assertEqual(record_digest(record), hashlib.sha256(first).hexdigest())

    def test_missing_and_unknown_fields_are_rejected(self):
        record = valid_record()
        del record["source"]
        with self.assertRaises(EnvelopeError):
            validate_record(record)
        record = valid_record()
        record["unreviewed_repair"] = True
        with self.assertRaises(EnvelopeError):
            validate_record(record)

    def test_timezone_is_required(self):
        record = valid_record()
        record["observed_at"] = "2026-11-09T19:00:00"
        with self.assertRaises(EnvelopeError):
            validate_record(record)

    def test_non_finite_numbers_are_rejected(self):
        record = valid_record()
        record["payload"]["reading"] = float("nan")
        with self.assertRaises(EnvelopeError):
            canonical_json_bytes(record)

    def test_unknown_quality_and_bad_digest_are_rejected(self):
        record = valid_record()
        record["quality"] = "GOOD_ENOUGH"
        with self.assertRaises(EnvelopeError):
            validate_record(record)
        record = valid_record()
        record["provenance"]["source_digest"] = "not-a-digest"
        with self.assertRaises(EnvelopeError):
            validate_record(record)

    def test_authorization_is_explicit_and_scoped(self):
        record = valid_record()
        record["authorization"] = {
            "status": "authorized", "scope": ["export.bundle"],
            "approval_ref": "approval-123",
        }
        validate_record(record)
        record["authorization"]["scope"] = []
        with self.assertRaises(EnvelopeError):
            validate_record(record)
        record = valid_record()
        record["authorization"]["status"] = "authorized"
        with self.assertRaises(EnvelopeError):
            validate_record(record)


if __name__ == "__main__":
    unittest.main()
