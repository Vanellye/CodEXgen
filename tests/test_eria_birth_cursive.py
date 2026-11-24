import unittest

from tools.eria_birth_cursive import (
    BirthCursiveEngine,
    CursiveCycleError,
    CursiveDepthError,
)


class BirthCursiveTests(unittest.TestCase):
    def setUp(self):
        self.engine = BirthCursiveEngine()

    def test_nested_ui_text_is_derived_and_origin_is_unchanged(self):
        source = {
            "dialog": {
                "title": "May you fail",
                "buttons": [
                    {"label": "You are worthless"},
                    {"label": "Continue"},
                ],
            }
        }
        before = {
            "dialog": {
                "title": "May you fail",
                "buttons": [
                    {"label": "You are worthless"},
                    {"label": "Continue"},
                ],
            }
        }

        derived, records = self.engine.transform_tree(source)

        self.assertEqual(source, before)
        self.assertEqual(
            derived["dialog"]["title"],
            "May your efforts open paths to learning, growth, and success.",
        )
        self.assertEqual(
            derived["dialog"]["buttons"][0]["label"],
            "Your life has inherent worth and dignity.",
        )
        self.assertEqual(derived["dialog"]["buttons"][1]["label"], "Continue")
        self.assertEqual(len(records), 3)
        self.assertEqual(records[0].origin_text, "May you fail")
        self.assertNotEqual(records[0].origin_sha256, records[0].derived_sha256)

    def test_technical_fields_are_not_transformed(self):
        source = {
            "message": "May you fail",
            "error_code": "May you fail",
            "command": "May you fail",
            "url": "May you fail",
        }
        derived, records = self.engine.transform_tree(source)
        self.assertEqual(derived["message"], "May your efforts open paths to learning, growth, and success.")
        self.assertEqual(derived["error_code"], "May you fail")
        self.assertEqual(derived["command"], "May you fail")
        self.assertEqual(derived["url"], "May you fail")
        self.assertEqual(len(records), 1)

    def test_unknown_text_is_preserved_and_flagged(self):
        source = {"label": "An ambiguous expression"}
        derived, records = self.engine.transform_tree(source)
        self.assertEqual(derived, source)
        self.assertEqual(records[0].status, "REVIEW_REQUIRED")
        self.assertIsNone(records[0].rule_id)

    def test_co_signature_reference_is_not_claimed_as_verified(self):
        record = self.engine.transform_text(
            "May you fail",
            "/button/label",
            co_signers=("origin-owner", "reviewer"),
            co_signature_ref="signature-ledger:event-42",
        )
        self.assertEqual(record.co_signature_status, "REFERENCE_ATTACHED_UNVERIFIED")
        self.assertEqual(record.signature_verification, "NOT_PERFORMED_BY_THIS_MODULE")

    def test_cycles_are_rejected(self):
        source = {"label": "May you fail"}
        source["nested"] = source
        with self.assertRaises(CursiveCycleError):
            self.engine.transform_tree(source)

    def test_depth_limit_is_enforced(self):
        engine = BirthCursiveEngine(max_depth=2)
        source = {"a": {"b": {"c": {"label": "May you fail"}}}}
        with self.assertRaises(CursiveDepthError):
            engine.transform_tree(source)


if __name__ == "__main__":
    unittest.main()
