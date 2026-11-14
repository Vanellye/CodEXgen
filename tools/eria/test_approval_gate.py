import unittest

from approval_gate import has_current_human_approval


HEAD = "a" * 40
OLD = "b" * 40


def review(login, account_type="User", state="APPROVED", commit=HEAD,
           submitted="2026-11-13T10:00:00Z"):
    return {
        "user": {"login": login, "type": account_type},
        "state": state,
        "commit_id": commit,
        "submitted_at": submitted,
    }


class ApprovalGateTests(unittest.TestCase):
    def test_missing_approval_blocks(self):
        ok, _ = has_current_human_approval([], HEAD, "author")
        self.assertFalse(ok)

    def test_stale_approval_blocks(self):
        ok, _ = has_current_human_approval([review("reviewer", commit=OLD)],
                                           HEAD, "author")
        self.assertFalse(ok)

    def test_bot_only_approval_blocks(self):
        ok, _ = has_current_human_approval(
            [review("automation[bot]", account_type="Bot")], HEAD, "author"
        )
        self.assertFalse(ok)

    def test_unknown_account_type_blocks(self):
        ok, _ = has_current_human_approval(
            [review("unknown", account_type=None)], HEAD, "author"
        )
        self.assertFalse(ok)

    def test_pull_request_author_cannot_approve_own_change(self):
        ok, _ = has_current_human_approval([review("author")], HEAD, "author")
        self.assertFalse(ok)

    def test_latest_nonapproval_supersedes_earlier_approval(self):
        reviews = [
            review("reviewer", state="APPROVED",
                   submitted="2026-11-13T10:00:00Z"),
            review("reviewer", state="CHANGES_REQUESTED",
                   submitted="2026-11-13T11:00:00Z"),
        ]
        ok, _ = has_current_human_approval(reviews, HEAD, "author")
        self.assertFalse(ok)

    def test_current_human_approval_passes(self):
        ok, message = has_current_human_approval(
            [review("reviewer")], HEAD, "author"
        )
        self.assertTrue(ok)
        self.assertIn("reviewer", message)

    def test_malformed_identity_does_not_approve(self):
        malformed = review("", account_type="User")
        ok, _ = has_current_human_approval([malformed], HEAD, "author")
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
